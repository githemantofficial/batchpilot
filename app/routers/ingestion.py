import json
from io import BytesIO
from typing import Annotated
from zipfile import ZIP_DEFLATED, ZipFile

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from app.services.csv_processor import clean_csv
from app.services.csv_profiler import profile_csv

router = APIRouter(
    prefix="/ingest",
    tags=["Data Ingestion"],
)

MAX_UPLOAD_BYTES = 5 * 1024 * 1024


async def _read_csv_upload(file: UploadFile) -> tuple[str, bytes]:
    """Validate an uploaded CSV and return its filename and contents."""

    original_filename = file.filename or ""

    # Normalize the filename to prevent path components being retained.
    filename = original_filename.replace("\\", "/").split("/")[-1]

    if not filename.lower().endswith(".csv"):
        await file.close()

        raise HTTPException(
            status_code=415,
            detail="Unsupported file type. Please upload a CSV file.",
        )

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

    return filename, contents


@router.post("/csv")
async def ingest_csv(file: Annotated[UploadFile, File()]):
    """Accept a CSV file and return its data-quality profile."""

    # Reuse the common upload validation.
    filename, contents = await _read_csv_upload(file)

    try:
        profile = profile_csv(contents)

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return {
        "filename": filename,
        "profile": profile,
    }


@router.post("/process/csv")
async def process_csv_file(
    file: Annotated[UploadFile, File()]
):
    """
    Clean a CSV file and return a ZIP containing the dataset and report.
    """

    filename, contents = await _read_csv_upload(file)

    try:
        cleaned_csv, report = clean_csv(contents)

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    # Produce safe output filenames.
    source_stem = filename.rsplit(".", 1)[0]

    cleaned_filename = f"{source_stem}_cleaned.csv"

    report["source_filename"] = filename
    report["output_filename"] = cleaned_filename

    # Build a ZIP archive in memory instead of writing temporary files.
    archive_buffer = BytesIO()

    with ZipFile(
        archive_buffer,
        mode="w",
        compression=ZIP_DEFLATED,
    ) as archive:
        archive.writestr(
            cleaned_filename,
            cleaned_csv,
        )

        archive.writestr(
            "report.json",
            json.dumps(report, indent=2),
        )

    archive_buffer.seek(0)

    return StreamingResponse(
        archive_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": (
                'attachment; filename="batchpilot-results.zip"'
            ),
        },
    )