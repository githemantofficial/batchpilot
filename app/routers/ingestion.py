from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.csv_profiler import profile_csv

router = APIRouter(
    prefix="/ingest",
    tags=["Data Ingestion"],
)

MAX_UPLOAD_BYTES = 5 * 1024 * 1024


@router.post("/csv")
async def ingest_csv(file: Annotated[UploadFile, File()]):
    """
    Accept a CSV file and return its data-quality profile.
    """

    filename = file.filename or ""

    # Check the file extension.
    if not filename.lower().endswith(".csv"):
        await file.close()

        raise HTTPException(
            status_code=415,
            detail="Unsupported file type. Please upload a CSV file.",
        )

    # Read at most 5 MB plus one byte to detect oversized uploads.
    try:
        contents = await file.read(MAX_UPLOAD_BYTES + 1)
    finally:
        await file.close()

    if not contents:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty.",
        )

    if len(contents) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail="File is too large. Maximum size is 5 MB.",
        )

    try:
        profile = profile_csv(contents)

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    # Return only the filename, not a client-supplied filesystem path.
    safe_filename = filename.replace("\\", "/").split("/")[-1]

    return {
        "filename": safe_filename,
        "profile": profile,
    }