from enum import Enum
from pydantic import BaseModel


class AnalysisModule(str, Enum):
    structure = "structure"
    style = "style"
    clarity = "logic"


class TaskStatus(str, Enum):
    STARTED = "STARTED"
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


class AnalyzeResponse(BaseModel):
    task_id: str
    module: AnalysisModule
    filename: str
    message: str


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str = TaskStatus


class TaskResultResponce(BaseModel):
    task_id: str
    result: str
    # TODO: maybe more fields needed