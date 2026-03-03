import time
import uuid
from fastapi import APIRouter, UploadFile, File


router = APIRouter()

@router.post(path="/analyzers/{module}", status_code=202, tags=["Analyzer Module"])
async def analyze_file(module: str, file: UploadFile = File(...)):
    # TODO: нужно 
    task_id = str(uuid.uuid4())
    
    return {
        "task_id": task_id,
        "module": module
    }


@router.get(path="/status/{task_id}", status_code=200, tags=["Task"])
def get_status(task_id):
    time.sleep(3)
    return {
        "status": "SUCCESS"
    }


@router.get(path="/result/{task_id}", status_code=200, tags=["Task"])
def get_result(task_id):
    time.sleep(1)
    return {
        "result": "task completed successfully."
    }