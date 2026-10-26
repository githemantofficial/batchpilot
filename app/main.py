from fastapi import FastAPI

from app.routers.ingestion import router as ingestion_router

app = FastAPI(
    title="BatchPilot",
    description="A data ingestion and processing platform.",
    version="0.1.0",
)


app.include_router(ingestion_router)


@app.get("/")
def home():
    """Return basic information about BatchPilot."""
    return {
        "name": "BatchPilot",
        "message": "Data ingestion and processing platform",
        "status": "running",
    }


@app.get("/health", tags=["Operations"])
def health_check():
    """Check whether the application is responding."""
    return {
        "status": "healthy",
    }


@app.get("/version", tags=["Operations"])
def get_version():
    """Return the current application version."""
    return {
        "name": app.title,
        "version": app.version,
    }