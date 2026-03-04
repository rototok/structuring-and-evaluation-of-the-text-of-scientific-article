from .api import analyzers
from fastapi import FastAPI


app = FastAPI(
    title="Academic Writing Assistant API",
    description="Backend API for LLM-based academic writing analysis",
    version="0.1.0"
)

# including end-points from analyzers
app.include_router(analyzers.router)

@app.get("/", tags=["Health"])
def healthcheck():
    return {
        "status": "Backend is running",
        "service": "Academic Writing Assistant API"
    }