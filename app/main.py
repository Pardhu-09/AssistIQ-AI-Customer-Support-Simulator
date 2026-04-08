"""
FastAPI server for the AI Customer Support Operations Simulator.
Provides REST endpoints for environment control and frontend serving.
"""
import os
import json
import datetime
from typing import List, Dict, Any
from fastapi import FastAPI, Body, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.env import CustomerSupportEnv
from app.models import (
    StepRequest, StepResponse,
    ResetRequest, ResetResponse,
    StateResponse, LogEntry
)
from app.tasks import TASKS, VALID_ACTIONS, ACTION_DESCRIPTIONS

# ── App setup ────────────────────────────────────────────────────────────────

app = FastAPI(
    title="AI Customer Support Operations Simulator",
    description=(
        "An OpenEnv-compatible environment for training and evaluating AI agents "
        "on real-world customer support tasks."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Global state ──────────────────────────────────────────────────────────────

env = CustomerSupportEnv()
logs: List[Dict[str, Any]] = []


def _ts() -> str:
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def _add_log(entry: Dict[str, Any]):
    entry["timestamp"] = _ts()
    logs.append(entry)
    # Keep last 500 log entries
    if len(logs) > 500:
        logs.pop(0)


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.post("/reset")
def reset(request: dict = Body(default={})):
    """Reset the environment to the beginning of a specified task."""
    task_id = request.get("task_id", list(TASKS.keys())[0])
    obs = env.reset(task_id)
    task_meta = TASKS[task_id]

    _add_log({
        "type": "[START]",
        "task_id": task_id,
        "task_name": task_meta["name"],
        "difficulty": task_meta["difficulty"],
        "message": f"Episode started for task: {task_meta['name']}",
    })

    return {
        "observation": obs,
        "task": {
            "id": task_meta["id"],
            "name": task_meta["name"],
            "difficulty": task_meta["difficulty"]
        }
    }


@app.post("/step", response_model=StepResponse, summary="Execute one agent step")
def step(request: StepRequest):
    """Execute one step in the environment with a chosen action."""
    if not env._initialized:
        raise HTTPException(status_code=400, detail="Environment not initialized. Call /reset first.")

    if env.done:
        raise HTTPException(status_code=400, detail="Episode is done. Call /reset to start a new one.")

    obs, reward, done, info = env.step(request.action, request.reasoning)

    log_entry = {
        "type": "[STEP]",
        "step": env.step_count,
        "task_id": env.task_id,
        "action": request.action,
        "reasoning": request.reasoning or "",
        "reward": round(reward, 3),
        "cumulative_reward": round(env.cumulative_reward, 3),
        "done": done,
        "info": info,
    }
    _add_log(log_entry)

    if done:
        _add_log({
            "type": "[END]",
            "task_id": env.task_id,
            "total_steps": env.step_count,
            "final_reward": round(env.cumulative_reward, 3),
            "reward_breakdown": {k: round(v, 3) for k, v in env.reward_breakdown.items()},
            "resolved": info.get("resolved", False) if isinstance(info, dict) else False,
            "message": "Episode complete.",
        })

    return StepResponse(observation=obs, reward=reward, done=done, info=info)


@app.get("/state", response_model=StateResponse, summary="Get the full environment state")
def state():
    """Retrieve the complete current environment state, including debug info."""
    if not env._initialized:
        raise HTTPException(status_code=400, detail="Environment not initialized. Call /reset first.")

    s = env.state()
    return StateResponse(
        task_id=s["task_id"],
        step_count=s["step_count"],
        cumulative_reward=s["cumulative_reward"],
        done=s["done"],
        conversation_history=s["conversation_history"],
        current_observation=s["current_observation"],
        reward_breakdown=s["reward_breakdown"],
        debug_info=s["debug_info"],
    )


@app.get("/tasks", summary="List all available tasks")
def get_tasks():
    """Return metadata for all available tasks."""
    return {
        task_id: {
            "id": t["id"],
            "name": t["name"],
            "difficulty": t["difficulty"],
            "description": t["description"],
            "max_steps": t["max_steps"],
            "ticket": t["ticket"],
        }
        for task_id, t in TASKS.items()
    }


@app.get("/logs", summary="Get the structured episode logs")
def get_logs(last: int = 100):
    """Return the last N log entries in [START]/[STEP]/[END] format."""
    return {"logs": logs[-last:], "total": len(logs)}


@app.get("/actions", summary="List all valid agent actions")
def get_actions():
    """Return all valid actions with their descriptions."""
    return {"actions": ACTION_DESCRIPTIONS}


@app.get("/health", summary="Health check")
def health():
    """Simple health check endpoint for Docker/HF Spaces."""
    return {"status": "ok", "service": "AI Customer Support Operations Simulator", "version": "1.0.0"}


# ── Frontend static file serving ──────────────────────────────────────────────

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")

if os.path.isdir(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/", include_in_schema=False)
    def serve_frontend():
        index_path = os.path.join(FRONTEND_DIR, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return JSONResponse({"message": "Frontend not built yet. API is running."})

    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_spa(full_path: str):
        file_path = os.path.join(FRONTEND_DIR, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        index_path = os.path.join(FRONTEND_DIR, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        raise HTTPException(status_code=404, detail="Not found")
