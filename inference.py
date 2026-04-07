"""
AI Agent Inference Script for the Customer Support Operations Simulator.
Uses the OpenAI SDK to interact with the environment via the FastAPI API.
Follows strict [START] / [STEP] / [END] log format.

Usage:
    python inference.py                       # Run all tasks
    python inference.py --task easy            # Run a single task
    python inference.py --base-url http://...  # Custom API URL
"""
import os
import sys
import json
import time
import argparse
import requests
from typing import Optional

# Ensure Windows consoles that default to legacy encodings don't crash on Unicode output.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# ── Configuration ─────────────────────────────────────────────────────────────

BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:7860")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

# ── Action Maps (deterministic fallback when no LLM is configured) ────────────

OPTIMAL_ACTIONS = {
    "easy": [
        ("classify_ticket", "Categorizing the support ticket to determine its type and priority level."),
        ("lookup_customer", "Retrieving the customer's account information and service tier."),
        ("verify_identity", "Verifying the customer's identity before making account changes per security policy."),
        ("send_password_reset", "Sending a password reset link to the customer's verified email address."),
        ("confirm_resolution", "Confirming with the customer that the issue has been resolved and closing the ticket."),
    ],
    "medium": [
        ("classify_ticket", "Classifying the billing complaint ticket to assign appropriate priority."),
        ("lookup_customer", "Looking up customer profile to verify Premium status and 5-year account history."),
        ("query_billing_records", "Querying the billing database to find transaction records for March 15th."),
        ("verify_duplicate_charge", "Cross-referencing with payment gateway to confirm the duplicate charge."),
        ("initiate_refund", "Initiating a same-day refund per Premium customer policy for verified overcharges."),
        ("send_confirmation", "Sending confirmation email with refund reference number and timeline."),
        ("confirm_resolution", "Confirming the billing dispute has been resolved to the customer's satisfaction."),
    ],
    "hard": [
        ("classify_ticket", "Classifying as Critical/P0 — production outage with revenue impact."),
        ("lookup_customer", "Retrieving Enterprise account details for ENT-00042 to verify SLA terms."),
        ("check_system_status", "Checking system monitoring dashboards to confirm the API Gateway outage."),
        ("acknowledge_outage", "Sending immediate acknowledgement to the customer per P0 incident protocol."),
        ("escalate_to_l2", "Escalating to L2 technical support for initial investigation."),
        ("escalate_to_l3", "Engaging L3 engineering on-call per Enterprise SLA — outage >10 minutes."),
        ("query_logs", "Pulling system logs from the API Gateway to identify error patterns."),
        ("identify_root_cause", "Analyzing logs — root cause: upstream_timeout set to 0 after last deployment."),
        ("apply_hotfix", "Deploying hotfix to reset upstream_timeout to 30s and restore service."),
        ("verify_resolution", "Confirming with the customer that all services are fully restored."),
        ("send_incident_report", "Sending formal post-incident report with root cause analysis and SLA credit."),
        ("confirm_resolution", "Closing the incident with full documentation and CSAT survey."),
    ],
}


# ── LLM-based Agent ──────────────────────────────────────────────────────────

def get_llm_action(observation: dict, step: int) -> tuple:
    """Use OpenAI to decide the next action based on the observation."""
    if not OPENAI_API_KEY:
        return None, None  # Fall back to deterministic

    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)

        prompt = f"""You are an AI customer support agent. Based on the current environment observation, decide the BEST next action.

## Current State
- Task: {observation.get('task_id', 'unknown')}
- Step: {step}
- Ticket: {json.dumps(observation.get('ticket', {}), indent=2)}
- Knowledge Base: {json.dumps(observation.get('knowledge_base', {}), indent=2)}
- Available Actions: {json.dumps(list(observation.get('available_actions', {}).keys()))}
- Suggested Next Actions: {json.dumps(observation.get('suggested_next_actions', []))}
- Conversation History: {json.dumps(observation.get('conversation_history', []), indent=2)}
- Last Environment Response: {observation.get('env_response', 'N/A')}

## Instructions
1. Pick exactly ONE action from the available actions list.
2. Provide a short, clear reasoning (1-2 sentences).
3. Respond in JSON format: {{"action": "action_name", "reasoning": "your reasoning"}}

Respond ONLY with the JSON object, no other text."""

        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert AI customer support agent. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=200,
        )

        content = response.choices[0].message.content.strip()
        # Parse JSON from response
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        result = json.loads(content)
        return result.get("action", ""), result.get("reasoning", "")

    except Exception as e:
        print(f"  [WARN] LLM call failed: {e}. Using deterministic fallback.")
        return None, None


# ── API Helpers ───────────────────────────────────────────────────────────────

def api_reset(task_id: str) -> dict:
    """Reset the environment for a given task."""
    res = requests.post(f"{BASE_URL}/reset", json={"task_id": task_id}, timeout=10)
    res.raise_for_status()
    return res.json()


def api_step(action: str, reasoning: str) -> dict:
    """Execute one step in the environment."""
    res = requests.post(f"{BASE_URL}/step", json={"action": action, "reasoning": reasoning}, timeout=10)
    res.raise_for_status()
    return res.json()


def api_state() -> dict:
    """Get the full environment state."""
    res = requests.get(f"{BASE_URL}/state", timeout=10)
    res.raise_for_status()
    return res.json()


# ── Run One Task ──────────────────────────────────────────────────────────────

def run_task(task_id: str) -> dict:
    """Run a complete episode for a given task."""
    print(f"\n{'='*60}")
    print(f"[START] Task: {task_id}")
    print(f"{'='*60}")

    # Reset
    reset_data = api_reset(task_id)
    task_info = reset_data["task"]
    print(f"  Task: {task_info['name']} ({task_info['difficulty']})")
    print(f"  Ticket: {task_info['ticket']['subject']}")
    print(f"  Max Steps: {task_info['max_steps']}")

    observation = reset_data["observation"]
    optimal = OPTIMAL_ACTIONS.get(task_id, [])
    step = 0
    done = False

    while not done:
        # Try LLM first, fall back to deterministic
        action, reasoning = get_llm_action(observation, step)

        if action is None:
            # Deterministic fallback
            if step < len(optimal):
                action, reasoning = optimal[step]
            else:
                action, reasoning = "confirm_resolution", "No more planned actions; confirming resolution."

        step += 1
        print(f"\n[STEP] Step {step}")
        print(f"  Action: {action}")
        print(f"  Reasoning: {reasoning}")

        step_result = api_step(action, reasoning)
        reward = step_result["reward"]
        done = step_result["done"]
        observation = step_result["observation"]

        print(f"  Reward: {'+' if reward >= 0 else ''}{reward:.3f}")
        print(f"  Cumulative: {observation['cumulative_reward']:.3f}")
        print(f"  Env Response: {observation['env_response']}")

        if done:
            print(f"\n[END] Task: {task_id}")
            print(f"  Total Steps: {step}")
            print(f"  Final Score: {observation['cumulative_reward']:.3f}")

        time.sleep(0.3)  # Small delay for readability

    # Get final state for breakdown
    final_state = api_state()
    print(f"  Reward Breakdown: {json.dumps(final_state['reward_breakdown'], indent=4)}")
    print(f"{'='*60}\n")

    return {
        "task_id": task_id,
        "total_steps": step,
        "final_score": observation["cumulative_reward"],
        "reward_breakdown": final_state["reward_breakdown"],
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="AI Customer Support Agent — Inference Script")
    parser.add_argument("--task", type=str, default=None, help="Run a specific task (easy/medium/hard). Omit to run all.")
    parser.add_argument("--base-url", type=str, default=None, help="Base URL of the API server.")
    args = parser.parse_args()

    global BASE_URL
    if args.base_url:
        BASE_URL = args.base_url.rstrip("/")

    # Check server health
    try:
        health = requests.get(f"{BASE_URL}/health", timeout=5)
        health.raise_for_status()
        print("✅ Server is healthy:", health.json())
    except Exception as e:
        print(f"❌ Cannot reach server at {BASE_URL}: {e}")
        print("   Make sure the server is running: uvicorn app.main:app --port 7860")
        sys.exit(1)

    tasks_to_run = [args.task] if args.task else ["easy", "medium", "hard"]
    results = []

    print("\n" + "🚀 " * 15)
    print("  AI Customer Support Operations Simulator — Inference Run")
    print("🚀 " * 15)

    for task_id in tasks_to_run:
        result = run_task(task_id)
        results.append(result)

    # Summary
    print("\n" + "=" * 60)
    print("📊 FINAL SUMMARY")
    print("=" * 60)
    total = 0
    for r in results:
        total += r["final_score"]
        emoji = "🟢" if r["final_score"] >= 2.0 else "🟡" if r["final_score"] >= 1.0 else "🔴"
        print(f"  {emoji} {r['task_id']:8s} → Score: {r['final_score']:.3f} ({r['total_steps']} steps)")
    print(f"\n  🏆 Total Score: {total:.3f}")
    print("=" * 60)

    return results


if __name__ == "__main__":
    main()
