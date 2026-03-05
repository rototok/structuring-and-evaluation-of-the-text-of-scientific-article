import time

from app.celery_app import celery
from services import file_parser


@celery.task(bind=True)
def analyze_task(self, module: str, file_path: str):
    try:
        time.sleep(3) # for testing purposes
        text = file_parser.parse(file_path)

        match(module):
            case "structure":
                # TODO: structure analysis module call
                pass
            case "style":
                # TODO: style analysis module call
                pass
            case "logic":
                # TODO: readability and logic analysis module call
                pass

        result = f"Analysis completed for module: {module}\nResult:\n{text}"

        return result

    except Exception as e:
        raise e