import os
import shutil
import uuid

from celery.result import AsyncResult
from fastapi import APIRouter, UploadFile

from app.schemas import (
    AnalysisModule,
    AnalyzeResponse,
    TaskStatusResponse,
    TaskResultResponce,
    TaskStatus
)
from app.tasks import analyze_task
from app.celery_app import celery


router = APIRouter()


@router.post(path="/analyzers/{module}", status_code=202, tags=["Analyzer Module"])
async def analyze_file(module: AnalysisModule, file: UploadFile):
    # saving file
    folder_path = "/tmp/"
    file_path = os.path.join(folder_path, file.filename)
    with open(file_path, 'wb') as save_file:
        shutil.copyfileobj(file.file, save_file)

    celery_task = analyze_task.delay(module.value, file_path)
    
    return AnalyzeResponse(
        task_id=celery_task.id,
        module=module,
        filename=file_path,
        status=TaskStatus.STARTED,
        message="Task accepted"
    )


@router.get(path="/status/{task_id}", status_code=200, tags=["Task"])
def get_task_status(task_id: str):
    # TODO: checking task status in celery
    task_result = AsyncResult(task_id, app=celery)

    return TaskStatusResponse(
        task_id=task_result.task_id,
        status=TaskStatus(task_result.status) if task_result.status in TaskStatus.__members__ else TaskStatus.PENDING
    )


@router.get(path="/result/{task_id}", status_code=200, tags=["Task"])
def get_task_result(task_id: str):
    # TODO: getting result from celery
    task_result = AsyncResult(task_id, app=celery)
    
    return TaskResultResponce(
        task_id=task_result.task_id,
        result=task_result.result
    )

if __name__ == "__main__":
    pass