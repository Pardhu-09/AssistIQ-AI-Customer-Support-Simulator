# 🤖 AI Customer Support Operations Simulator

> **An OpenEnv-Compatible, Production-Grade AI Environment for Hackathons**

[![OpenEnv](https://img.shields.io/badge/OpenEnv-v1.0-6366f1?style=flat-square)](https://openenv.ai)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?style=flat-square)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square)](https://python.org)

---

## 🎯 What is This?

A **real-world AI Customer Support Operations Simulator** built on the **OpenEnv** framework. It simulates an enterprise AI agent that handles escalating support tickets — from simple password resets to full-scale production outage responses.

The environment is fully **RL-compatible** with a multi-criteria reward system. A **modern dark-mode SaaS dashboard** visualizes every step the agent takes in real time.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🎯 **Live Agent Visualization** | Watch every `action → observation → reward` in real time |
| 📊 **Reward Progress Dashboard** | Live Chart.js graph of cumulative reward over steps |
| 🧠 **Explainable AI Panel** | See *why* the agent chose each action |
| 🎫 **Ticket Simulation Panel** | Real customer tickets with full history |
| ⚡ **Multi-Task Runner** | One-click run across all 3 tasks with score comparison |
| 🧪 **Debug Mode** | Full internal state inspector for judges |
| 🎮 **Manual Control** | Execute any action yourself via the UI |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Browser / User                       │
│                  frontend/index.html                      │
│         (Tailwind CSS + Chart.js + Vanilla JS)           │
└────────────────────────┬────────────────────────────────┘
                         │ REST API (JSON)
┌────────────────────────▼────────────────────────────────┐
│                   FastAPI Server                         │
│                   app/main.py                            │
│  POST /reset  POST /step  GET /state  GET /tasks        │
│  GET /logs    GET /actions  GET /health                  │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│              OpenEnv Environment                         │
│              app/env.py                                  │
│  reset()  step()  state()  _calculate_reward()           │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│              Task Definitions                            │
│              app/tasks.py                                │
│  Easy: Password Reset                                    │
│  Medium: Billing Dispute                                 │
│  Hard: Critical Service Outage                           │
└─────────────────────────────────────────────────────────┘
```

### How the UI Connects to OpenEnv

1. User selects a task in the **Task Selector** panel
2. Clicking **Reset Task** → `POST /reset` → initializes the OpenEnv environment
3. The **Auto-Run** button drives the AI agent step by step → `POST /step` per action
4. Each step response updates the **Live Timeline**, **XAI Panel**, and **Reward Graph**
5. `GET /state` is polled after each step to update the **Reward Breakdown** sidebar
6. `GET /logs` streams `[START]` / `[STEP]` / `[END]` entries to the **Logs Panel**

---

## 📁 Project Structure

```
project-root/
├── app/
│   ├── __init__.py        # Package marker
│   ├── env.py             # OpenEnv environment (reset/step/state + rewards)
│   ├── tasks.py           # 3 task definitions with tickets & KB
│   ├── models.py          # Pydantic request/response schemas
│   └── main.py            # FastAPI server + static file serving
│
├── frontend/
│   └── index.html         # Full SPA dashboard (Tailwind CDN + Chart.js)
│
├── inference.py           # AI agent with OpenAI SDK + deterministic fallback
├── openenv.yaml           # OpenEnv configuration
├── requirements.txt       # Python dependencies
├── Dockerfile             # Single-container build for HF Spaces
├── .dockerignore
└── README.md
```

---

## 🎮 Tasks

### 🟢 Easy — Password Reset Request
- **Ticket**: Customer locked out before a meeting
- **Expected sequence**: classify → lookup → verify_identity → send_password_reset → confirm
- **Max steps**: 6

### 🟡 Medium — Billing Dispute Resolution
- **Ticket**: Premium customer double-charged $99.99
- **Expected sequence**: classify → lookup → query_billing → verify_duplicate → refund → confirm
- **Max steps**: 10

### 🔴 Hard — Critical Service Outage (P0)
- **Ticket**: Enterprise CTO with $5k/min revenue loss, API Gateway down
- **Expected sequence**: classify → lookup → check_status → acknowledge → L2 → L3 → logs → root_cause → hotfix → verify → incident_report → confirm
- **Max steps**: 15

---

## 📊 Reward System

```python
reward = (
    + 0.40  # correctness: right action in right order
    + 0.10  # partial:     right action, wrong order
    + 0.30  # escalation:  required escalation completed (hard task)
    + 0.10  # quality:     reasoning provided
    - 0.05  # efficiency:  step count approaching max
)

penalties = (
    - 0.50  # hallucination: invalid action used
    - 0.20  # redundancy:    same action repeated
)

completion_bonus = correct_ratio × 1.0 + step_efficiency × 0.5
```

---

## 🚀 Running Locally

### Prerequisites
```bash
python -m pip install -r requirements.txt
```

### Start the Server
```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 7860
```

Open **http://127.0.0.1:7860** in your browser (the FastAPI server serves `frontend/index.html`).

### Windows (PowerShell) Quick Start
```powershell
cd "C:\Users\pardhu\OneDrive\ドキュメント\Problem Statement"
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 7860
```

Then in a second PowerShell window:

```powershell
cd "C:\Users\pardhu\OneDrive\ドキュメント\Problem Statement"
python inference.py --task easy --base-url http://127.0.0.1:7860
```

### Run the Inference Agent
```bash
# Deterministic (no API key needed)
python inference.py

# With OpenAI (GPT-4o-mini)
OPENAI_API_KEY=sk-... python inference.py

# Single task
python inference.py --task hard
```

#### Note (Windows console encoding)
If your terminal crashes with `UnicodeEncodeError` while printing symbols (e.g., ✅/❌), run in Windows Terminal or set UTF-8 encoding. This repo also configures UTF-8 output in `inference.py` to avoid that failure mode.

---

## 🐳 Docker

```bash
# Build
docker build -t ai-support-ops .

# Run
docker run -p 7860:7860 ai-support-ops

# With OpenAI key
docker run -p 7860:7860 -e OPENAI_API_KEY=sk-... ai-support-ops
```

---

## 🤗 HuggingFace Spaces

Deploy as a **Docker Space** on HuggingFace:
1. Create a new Space → SDK: **Docker**
2. Push this repository
3. Add `OPENAI_API_KEY` as a Space Secret (optional)
4. The app will be live at `https://huggingface.co/spaces/YOUR_NAME/ai-support-ops`

---

## 🔌 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/reset` | Start a new episode: `{"task_id": "easy"}` |
| `POST` | `/step` | Execute action: `{"action": "classify_ticket", "reasoning": "..."}` |
| `GET` | `/state` | Full environment state + debug info |
| `GET` | `/tasks` | List all tasks with metadata |
| `GET` | `/logs` | Structured [START]/[STEP]/[END] logs |
| `GET` | `/actions` | All valid agent actions + descriptions |
| `GET` | `/health` | Health check for container orchestrators |

---

## 💡 Example Workflow

```
1. User opens http://localhost:7860
2. Selects "Hard" task (Critical Outage)
3. Clicks "Reset Task" → Environment initializes
4. Clicks "Auto-Run Task" → Agent executes 12 steps
5. Dashboard shows:
   - Live timeline: each action with reward
   - XAI panel: why each action was chosen
   - Reward graph: cumulative score rising
   - Debug panel: internal state (valid next actions, etc.)
6. Final score displayed in Analytics → Task Comparison
7. Click "Multi-Task Runner" → Runs easy+medium+hard automatically
8. Analytics tab shows comparative bar chart
```

---

## 🧠 Explainable AI

The **XAI Panel** (right sidebar) shows:
- **Action Taken**: The specific action the agent chose
- **Why This Action?**: The agent's reasoning string
- **Outcome**: The environment's response
- **Step Reward**: Exact reward for this step

This makes the agent's decision-making fully transparent to judges and users.

---

## 🔮 Bonus Features Implemented

- ✅ **Memory-based reasoning** — Conversation history passed back to LLM
- ✅ **Auto-optimization** — Deterministic fallback uses optimal action sequences
- ✅ **Deterministic graders** — Reproducible scoring regardless of LLM variation
- ✅ **Debug mode** — Full internal state visible via toggle button

---

*Built for hackathon judges who love both clean code AND beautiful UIs.* 🏆
#   A s s i s t I Q - A I - C u s t o m e r - S u p p o r t - S i m u l a t o r 
 
 