import time
import uuid
from fastapi import APIRouter, UploadFile
from ..schemas import (
    AnalysisModule,
    TaskStatus,
    AnalyzeResponse,
    TaskStatusResponse,
    TaskResultResponce
)


router = APIRouter()


@router.post(path="/analyzers/{module}", status_code=202, tags=["Analyzer Module"])
async def analyze_file(module: AnalysisModule, file: UploadFile):
    # TODO: creation of task_id and sending task to the celery
    task_id = str(uuid.uuid4())
    
    return AnalyzeResponse(
        task_id=task_id,
        module=module,
        filename=file.filename,
        message="Task accepted"
    )


@router.get(path="/status/{task_id}", status_code=200, tags=["Task"])
def get_task_status(task_id: str):
    # TODO: checking task status in celery
    time.sleep(3)
    return TaskStatusResponse(
        task_id=task_id,
        status="SUCCESS"
    )


@router.get(path="/result/{task_id}", status_code=200, tags=["Task"])
def get_task_result(task_id: str):
    # TODO: getting result from celery
    time.sleep(1)
    return TaskResultResponce(
        task_id=task_id,
        result="Result of the task is here"
    )