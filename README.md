# structuring-and-evaluation-of-the-text-of-scientific-article

Stack:
- **Frontend**: streamlit
- **API**: FastAPI, uvicorn, pydantic
- **Task Queue Manager**: celery, redis
- **File parsing**: pymupdf4llm, chardet, python-docx
- **Model inference**: llama-cpp-python
- **Model**: YandexGPT-5-Lite-8B-instruct-GGUF

Build project:  
```
docker-compose up --build
```

After the successfull building of project go to http://localhost:8501/

You can upload your manuscript and perform a structure evaluation of the text. LLM will check the text for compliance with the IMRAD structure and write a report with recommendations for revision.
