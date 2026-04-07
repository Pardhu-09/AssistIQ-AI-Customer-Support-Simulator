"""
OpenEnv Environment: AI Customer Support Operations Simulator.
Implements step(), reset(), and state() with a full reward system.
"""
import time
from typing import Dict, Any, List, Optional, Tuple
from app.tasks import TASKS, VALID_ACTIONS, ACTION_DESCRIPTIONS


class CustomerSupportEnv:
    """
    OpenEnv-compatible environment simulating an AI customer support agent.
    The agent must classify tickets, look up customer data, apply policies,
    and resolve issues using the correct sequence of actions.
    """

    def __init__(self):
        self.task: Optional[Dict[str, Any]] = None
        self.task_id: str = ""
        self.step_count: int = 0
        self.done: bool = False
        self.cumulative_reward: float = 0.0
        self.conversation_history: List[Dict[str, str]] = []
        self.actions_taken: List[str] = []
        self.reward_breakdown: Dict[str, float] = {}
        self.debug_info: Dict[str, Any] = {}
        self._initialized: bool = False
        self._start_time: float = 0.0
        self._correct_actions_hit: List[str] = []
        self._hallucinations: int = 0
        self._redundant_actions: int = 0
        self._escalation_done: bool = False

    # ------------------------------------------------------------------
    # Core API
    # ------------------------------------------------------------------

    def reset(self, task_id: str) -> Dict[str, Any]:
        """Reset the environment for a new episode."""
        if task_id not in TASKS:
            raise ValueError(f"Unknown task_id '{task_id}'. Valid: {list(TASKS.keys())}")

        self.task = TASKS[task_id]
        self.task_id = task_id
        self.step_count = 0
        self.done = False
        self.cumulative_reward = 0.0
        self.conversation_history = []
        self.actions_taken = []
        self.reward_breakdown = {
            "correctness": 0.0,
            "efficiency": 0.0,
            "response_quality": 0.0,
            "hallucination_penalty": 0.0,
            "redundancy_penalty": 0.0,
        }
        self.debug_info = {
            "valid_next_actions": self._get_valid_next_actions(),
            "expected_sequence": self.task["expected_actions"],
            "resolved": False,
            "escalation_required": self.task["escalation_required"],
        }
        self._initialized = True
        self._start_time = time.time()
        self._correct_actions_hit = []
        self._hallucinations = 0
        self._redundant_actions = 0
        self._escalation_done = False

        obs = self._build_observation(action=None, reward=0.0, info="Episode started.")
        self.conversation_history.append({
            "role": "system",
            "content": f"New ticket received: {self.task['ticket']['subject']}"
        })
        return obs

    def step(self, action: str, reasoning: Optional[str] = None) -> Tuple[Dict[str, Any], float, bool, Dict[str, Any]]:
        """Execute one step in the environment."""
        if not self._initialized:
            raise RuntimeError("Call reset() before step().")
        if self.done:
            return self._build_observation(action, 0.0, "Episode already done."), 0.0, True, self.debug_info

        self.step_count += 1
        reward, info_msg = self._calculate_reward(action, reasoning)
        self.cumulative_reward += reward
        self.actions_taken.append(action)

        # Add to conversation history
        self.conversation_history.append({"role": "agent", "content": f"Action: {action}"})
        if reasoning:
            self.conversation_history[-1]["reasoning"] = reasoning

        env_response = self._simulate_env_response(action)
        self.conversation_history.append({"role": "environment", "content": env_response})

        # Check terminal conditions
        if action == "confirm_resolution" or self.step_count >= self.task["max_steps"]:
            self.done = True
            bonus = self._compute_completion_bonus()
            self.cumulative_reward += bonus
            reward += bonus
            info_msg += f" Episode complete. Bonus: +{bonus:.2f}"
            self.debug_info["resolved"] = (action == "confirm_resolution")

        self.debug_info["valid_next_actions"] = self._get_valid_next_actions()
        self.debug_info["step_count"] = self.step_count
        self.debug_info["last_action"] = action
        self.debug_info["last_reasoning"] = reasoning

        obs = self._build_observation(action, reward, info_msg)
        return obs, reward, self.done, self.debug_info

    def state(self) -> Dict[str, Any]:
        """Return the current full environment state."""
        return {
            "task_id": self.task_id,
            "step_count": self.step_count,
            "cumulative_reward": round(self.cumulative_reward, 3),
            "done": self.done,
            "conversation_history": self.conversation_history,
            "current_observation": self._build_observation(None, 0.0, ""),
            "reward_breakdown": {k: round(v, 3) for k, v in self.reward_breakdown.items()},
            "debug_info": self.debug_info,
        }

    # ------------------------------------------------------------------
    # Reward Calculation
    # ------------------------------------------------------------------

    def _calculate_reward(self, action: str, reasoning: Optional[str]) -> Tuple[float, str]:
        """Multi-criteria reward calculation."""
        reward = 0.0
        info_parts = []

        # 1. Hallucination check — action not in valid global actions
        if action not in VALID_ACTIONS:
            penalty = -0.5
            self.reward_breakdown["hallucination_penalty"] += penalty
            self._hallucinations += 1
            return penalty, f"Hallucinated action '{action}'. Penalty: {penalty}"

        # 2. Redundancy check — action taken again unnecessarily
        if action in self.actions_taken and action not in ["request_more_info", "send_confirmation"]:
            penalty = -0.2
            self.reward_breakdown["redundancy_penalty"] += penalty
            self._redundant_actions += 1
            info_parts.append(f"Redundant action. Penalty: {penalty}")
            reward += penalty

        # 3. Correctness — is this action in the expected sequence?
        expected = self.task["expected_actions"]
        next_expected_idx = len(self._correct_actions_hit)
        if next_expected_idx < len(expected) and action == expected[next_expected_idx]:
            correctness_reward = 0.4
            self.reward_breakdown["correctness"] += correctness_reward
            self._correct_actions_hit.append(action)
            reward += correctness_reward
            info_parts.append(f"Correct action (+{correctness_reward})")
        elif action in expected:
            # Correct action, wrong order
            partial = 0.1
            self.reward_breakdown["correctness"] += partial
            reward += partial
            info_parts.append(f"Out-of-order correct action (+{partial})")
        else:
            # Suboptimal but not hallucinated
            reward += 0.0
            info_parts.append("Valid but suboptimal action (0.0)")

        # 4. Escalation check for hard task
        if self.task["escalation_required"] and action in ["escalate_to_l2", "escalate_to_l3"]:
            if not self._escalation_done:
                escalation_reward = 0.3
                self.reward_breakdown["correctness"] += escalation_reward
                reward += escalation_reward
                self._escalation_done = True
                info_parts.append(f"Required escalation done (+{escalation_reward})")

        # 5. Response quality — has reasoning been provided?
        if reasoning and len(reasoning) > 20:
            quality_reward = 0.1
            self.reward_breakdown["response_quality"] += quality_reward
            reward += quality_reward
            info_parts.append(f"Reasoning provided (+{quality_reward})")

        # 6. Efficiency — penalize if too many steps taken
        if self.step_count > self.task["max_steps"] * 0.8:
            slowness_penalty = -0.05
            self.reward_breakdown["efficiency"] += slowness_penalty
            reward += slowness_penalty
            info_parts.append(f"Efficiency warning ({slowness_penalty})")

        return round(reward, 3), " | ".join(info_parts) if info_parts else "Action processed."

    def _compute_completion_bonus(self) -> float:
        """Bonus for completing the task."""
        if not self.task:
            return 0.0
        correct_ratio = len(self._correct_actions_hit) / max(len(self.task["expected_actions"]), 1)
        step_efficiency = max(0, 1.0 - self.step_count / self.task["max_steps"])
        bonus = round(correct_ratio * 1.0 + step_efficiency * 0.5, 3)
        self.reward_breakdown["efficiency"] += step_efficiency * 0.5
        return bonus

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _get_valid_next_actions(self) -> List[str]:
        """Suggest the next set of valid actions based on state."""
        if not self.task:
            return VALID_ACTIONS[:5]
        taken = set(self.actions_taken)
        expected = self.task["expected_actions"]
        next_idx = len(self._correct_actions_hit)
        suggestions = []
        if next_idx < len(expected):
            suggestions.append(expected[next_idx])
        suggestions += [a for a in VALID_ACTIONS if a not in taken][:4]
        return list(dict.fromkeys(suggestions))[:5]

    def _simulate_env_response(self, action: str) -> str:
        """Simulate the environment's response to an action."""
        ticket = self.task["ticket"]
        responses = {
            "classify_ticket": f"✅ Ticket {ticket['id']} classified as [{ticket['category']}] | Priority: {ticket['priority']}.",
            "lookup_customer": f"✅ Customer found: {ticket['customer_name']} | Tier: {ticket['customer_tier']} | Account age: {ticket['account_age_days']} days.",
            "verify_identity": "✅ Identity verified via last 4 digits of phone number.",
            "send_password_reset": "✅ Password reset email sent to customer's verified email address.",
            "query_billing_records": "✅ Billing records retrieved. Found 2 charges of $99.99 on 2024-03-15 at 14:02 and 14:03.",
            "verify_duplicate_charge": "✅ Payment gateway confirmed: duplicate transaction ID TX-99812 charged twice.",
            "initiate_refund": "✅ Refund of $99.99 initiated. Expected in 3-5 business days. Ref: REF-112233.",
            "send_confirmation": "✅ Confirmation email sent with resolution details and reference number.",
            "check_system_status": "⚠️ Status Page: API Gateway (us-east-1) — DEGRADED. Error rate: 100%. Started: 23 min ago.",
            "acknowledge_outage": "✅ Acknowledgement sent to customer. SLA timer started.",
            "escalate_to_l2": "✅ Ticket escalated to L2 support. ETA: 10 minutes.",
            "escalate_to_l3": "✅ P0 incident created. L3 Engineering on-call paged. War room link shared.",
            "query_logs": "✅ Logs retrieved: 502 errors originating from misconfigured upstream timeout (30s → 0s after last deploy).",
            "identify_root_cause": "✅ Root cause identified: Deployment commit #a3f9c2 set upstream_timeout=0. Rolled back config identified.",
            "apply_hotfix": "✅ Hotfix deployed: upstream_timeout reset to 30s. API Gateway health: HEALTHY. Error rate: 0%.",
            "verify_resolution": "✅ Customer confirmed services are fully restored.",
            "send_incident_report": "✅ Post-incident report sent. SLA credit of $7,200 applied to account.",
            "confirm_resolution": f"✅ Ticket {ticket['id']} marked as RESOLVED. CSAT survey sent.",
            "request_more_info": "📋 Additional information request sent to customer. Awaiting reply.",
            "close_ticket": f"⚠️ Ticket {ticket['id']} closed without full resolution confirmation.",
        }
        return responses.get(action, f"✅ Action '{action}' executed successfully.")

    def _build_observation(self, action: Optional[str], reward: float, info: str) -> Dict[str, Any]:
        """Build the observation dictionary."""
        if not self.task:
            return {"status": "not_initialized"}
        return {
            "task_id": self.task_id,
            "ticket": self.task["ticket"],
            "step": self.step_count,
            "last_action": action,
            "last_reward": reward,
            "cumulative_reward": round(self.cumulative_reward, 3),
            "info": info,
            "done": self.done,
            "knowledge_base": self.task["knowledge_base"],
            "available_actions": ACTION_DESCRIPTIONS,
            "suggested_next_actions": self._get_valid_next_actions(),
            "conversation_history": self.conversation_history[-6:],  # last 6 turns
            "env_response": self._simulate_env_response(action) if action else "Awaiting first action.",
        }
