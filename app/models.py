"""
Pydantic models for the AI Customer Support Operations Simulator API.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


class StepRequest(BaseModel):
    """Request body for the /step endpoint."""
    action: str = Field(..., description="The action taken by the agent.")
    reasoning: Optional[str] = Field(
        None, description="Agent's explanation for why it chose this action."
    )


class StepResponse(BaseModel):
    """Response from the /step endpoint."""
    observation: Dict[str, Any] = Field(..., description="The new environment state after the action.")
    reward: float = Field(..., description="Reward earned for this step.")
    done: bool = Field(..., description="Whether the episode has ended.")
    info: Dict[str, Any] = Field(default_factory=dict, description="Additional debug info.")


class ResetRequest(BaseModel):
    """Request body for the /reset endpoint."""
    task_id: str = Field(..., description="The task to reset the environment to. Options: easy, medium, hard.")


class ResetResponse(BaseModel):
    """Response from the /reset endpoint."""
    observation: Dict[str, Any] = Field(..., description="The initial environment observation.")
    task: Dict[str, Any] = Field(..., description="Metadata about the current task.")
    message: str = "Environment reset successfully."


class TaskInfo(BaseModel):
    """Metadata for a single task."""
    id: str
    name: str
    difficulty: str
    description: str
    max_steps: int
    ticket: Dict[str, Any]


class LogEntry(BaseModel):
    """A single log entry."""
    type: str  # START, STEP, END
    step: Optional[int] = None
    task_id: Optional[str] = None
    action: Optional[str] = None
    reasoning: Optional[str] = None
    reward: Optional[float] = None
    cumulative_reward: Optional[float] = None
    observation: Optional[Dict[str, Any]] = None
    done: Optional[bool] = None
    message: Optional[str] = None
    timestamp: Optional[str] = None


class StateResponse(BaseModel):
    """Full environment state."""
    task_id: str
    step_count: int
    cumulative_reward: float
    done: bool
    conversation_history: List[Dict[str, str]]
    current_observation: Dict[str, Any]
    reward_breakdown: Dict[str, float]
    debug_info: Dict[str, Any]
