from typing import Any, Dict, Optional
from pydantic import BaseModel

class TaskRequest(BaseModel):
  user_id: str
  user_prompt: str

class TaskResponse(BaseModel):
  task_id: int
  status: str
  message: str
  cloud_output: str
  edge_execution: Dict[str, Any]
  metrics: Dict[str, Any]

  
