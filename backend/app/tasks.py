from app.celery_app import celery
from modules.structure_module import run as run_structure
from services import file_parser


@celery.task(bind=True)
def analyze_task(self, module: str, file_path: str):
    try:
        text = file_parser.parse(file_path)

        match(module):
            case "structure":
                result = run_structure(text)
            case "style":
                # TODO: style analysis module call
                pass
            case "logic":
                # TODO: readability and logic analysis module call
                pass

        return result

    except Exception as e:
        raise e