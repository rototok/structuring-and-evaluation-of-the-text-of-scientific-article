import time

from app.celery_app import celery


@celery.task(bind=True)
def analyze_task(self, module: str, file_path: str):
    try:
        time.sleep(3) # for testing purposes

        result = f"Analysis completed for module: {module, file_path}"

        return result

    except Exception as e:
        raise e