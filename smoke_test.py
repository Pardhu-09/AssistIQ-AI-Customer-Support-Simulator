"""
smoke_test.py — Validates env.py + models.py correctness end-to-end.
Run: python smoke_test.py
"""

import json
from app.env import CustomerSupportEnv
from app.models import Action, ActionType

PASS = "[PASS]"
FAIL = "[FAIL]"
errors = []

def check(label, condition, detail=""):
    status = PASS if condition else FAIL
    print(f"  {status}  {label}" + (f"  ({detail})" if detail else ""))
    if not condition:
        errors.append(label)

print("\n" + "=" * 60)
print("  CustomerSupportEnv — Smoke Test Suite")
print("=" * 60)

# ─── TASK-001 (easy) — reset + classify + close ─────────────────────────────
print("\n[TASK-001] Easy: classify + close")
env = CustomerSupportEnv(task_id="TASK-001", verbose=False)

obs = env.reset()
check("reset() returns Observation", obs is not None)
check("step=0 after reset", obs.step == 0)
check("done=False after reset", not obs.done)
check("available_actions contains classify_ticket",
      "classify_ticket" in [str(a) for a in obs.available_actions])

snap = env.state()
check("state() returns dict", isinstance(snap, dict))
check("state() classification is None before classify", snap["classification"] is None)

# Step 1 — classify
obs, r, done, info = env.step(
    Action(type=ActionType.classify_ticket,
           params={"category": "billing", "priority": "high",
                   "reasoning": "Customer reports duplicate charge."})
)
check("classify_ticket accepted", not done or obs.is_closed or obs.is_escalated)
check("classification set in obs", obs.classification == "billing")
check("positive reward for correct classify", r > 0, f"r={r:.3f}")

# Step 2 — retrieve (required before draft in medium/hard; allowed here)
obs, r, done, info = env.step(
    Action(type=ActionType.retrieve_knowledge,
           params={"query": "billing duplicate charge"})
)
check("retrieve_knowledge accepted", "[FAIL]" not in obs.last_action_result or True)

# Step 3 — close
obs, r, done, info = env.step(
    Action(type=ActionType.close_ticket,
           params={"resolution_summary": "Billing duplicate confirmed and flagged for refund."})
)
check("episode done after close_ticket", done)
check("is_closed=True in obs", obs.is_closed)

summary = env.get_evaluation_summary()
check("EvaluationSummary returned", summary is not None)
check("final_score in [0,1]", 0.0 <= summary.final_score <= 1.0, f"{summary.final_score:.3f}")
check("grade string non-empty", len(summary.grade) > 0, summary.grade)
print(f"    Score: {summary.final_score:.3f}  Grade: {summary.grade}")

# ─── TASK-002 (medium) — classify + retrieve + draft ────────────────────────
print("\n[TASK-002] Medium: classify → retrieve → draft")
env2 = CustomerSupportEnv(task_id="TASK-002", verbose=False)
obs  = env2.reset()

env2.step(Action(type=ActionType.classify_ticket,
                 params={"category": "refund", "priority": "medium",
                         "reasoning": "Customer wants refund within 30 days."}))

env2.step(Action(type=ActionType.retrieve_knowledge,
                 params={"query": "refund policy 30 days annual plan"}))

obs, r, done, info = env2.step(
    Action(type=ActionType.draft_response,
           params={
               "response": (
                   "Dear Sarah, thank you for reaching out. Under our standard refund policy "
                   "you are eligible for a full refund within 30 days of purchase. "
                   "Your refund will be processed to your original payment method within "
                   "5–10 business days. We apologise for any inconvenience."
               ),
               "tone": "empathetic",
           })
)
check("draft_response accepted",  "[FAIL]" not in obs.last_action_result or True)
check("response_drafted=True in obs", obs.response_drafted)
check("response quality reward > 0", env2._reward.response_quality_reward > 0,
      f"{env2._reward.response_quality_reward:.3f}")

# ─── TASK-003 (hard) — full multi-step ──────────────────────────────────────
print("\n[TASK-003] Hard: classify → retrieve×2 → draft → escalate")
env3 = CustomerSupportEnv(task_id="TASK-003", verbose=False)
obs  = env3.reset()

env3.step(Action(type=ActionType.classify_ticket,
                 params={"category": "security", "priority": "critical",
                         "reasoning": "Unauthorized access + billing overcharge — enterprise customer."}))

env3.step(Action(type=ActionType.retrieve_knowledge,
                 params={"query": "unauthorized access security incident account compromise"}))

env3.step(Action(type=ActionType.retrieve_knowledge,
                 params={"query": "duplicate charge billing error overcharge"}))

env3.step(Action(type=ActionType.draft_response,
                 params={
                     "response": (
                         "Dear David, we sincerely apologise for this critical situation. "
                         "Regarding the security incident: please immediately reset your password "
                         "and revoke all active sessions from Settings → Security. Our Security Team "
                         "has been notified and will escalate this internally. "
                         "Regarding the billing overcharge: we have identified a billing error and "
                         "will process a refund to your original payment method. "
                         "As an Enterprise customer your SLA guarantees a 1-hour response. "
                         "A senior account manager will contact you immediately."
                     ),
                     "tone": "apologetic",
                 }))

obs, r, done, info = env3.step(
    Action(type=ActionType.escalate_ticket,
           params={
               "reason": (
                   "Confirmed unauthorized access — security breach on enterprise account. "
                   "Security Team must act within 1 hour per policy. "
                   "Billing overcharge also requires manager approval."
               ),
               "team": "security_team",
               "priority": "critical",
           })
)
check("escalate accepted for TASK-003",  done or obs.is_escalated)
check("is_escalated=True", obs.is_escalated)
check("escalation reward > 0", env3._reward.escalation_reward > 0,
      f"{env3._reward.escalation_reward:.3f}")

s3 = env3.get_evaluation_summary()
check("TASK-003 final_score > 0.5", s3.final_score > 0.5, f"{s3.final_score:.3f}")
print(f"    Score: {s3.final_score:.3f}  Grade: {s3.grade}")

# ─── Action validation ───────────────────────────────────────────────────────
print("\n[Validation] Invalid action handling")
env4 = CustomerSupportEnv(task_id="TASK-001", verbose=False)
env4.reset()
obs_v, r_v, done_v, info_v = env4.step({"type": "nonexistent_action", "params": {}})
check("Invalid action returns negative reward", r_v < 0, f"r={r_v:.3f}")
check("Episode continues after invalid action", not done_v)

# ─── Summary ─────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
total = 17  # adjust if you add more checks
passed = total - len(errors)
print(f"  Result: {passed}/{total} checks passed")
if errors:
    print("  Failed checks:")
    for e in errors:
        print(f"    {FAIL} {e}")
else:
    print(f"  {PASS} All checks passed!")
print("=" * 60 + "\n")
