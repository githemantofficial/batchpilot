import csv
import io
import json
import zipfile

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


# --------------------------------------------------
# Basic application tests
# --------------------------------------------------

def test_home_endpoint():
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "BatchPilot"
    assert data["status"] == "running"


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_version_endpoint():
    response = client.get("/version")

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "BatchPilot"
    assert data["version"] == "0.1.0"


# --------------------------------------------------
# CSV profiling tests
# --------------------------------------------------

def test_csv_ingestion_generates_profile():
    sample_csv = (
        "order_id,amount,region\n"
        "1,100,North\n"
        "2,,South\n"
        "2,,South\n"
        "3,300,East\n"
    )

    response = client.post(
        "/ingest/csv",
        files={
            "file": (
                "sales.csv",
                sample_csv.encode("utf-8"),
                "text/csv",
            )
        },
    )

    assert response.status_code == 200

    result = response.json()
    profile = result["profile"]

    assert result["filename"] == "sales.csv"
    assert profile["row_count"] == 4
    assert profile["column_count"] == 3
    assert profile["duplicate_rows"] == 1

    assert profile["missing_values"]["amount"] == 2
    assert profile["missing_values"]["region"] == 0

    assert profile["numeric_summary"]["amount"]["min"] == 100.0
    assert profile["numeric_summary"]["amount"]["max"] == 300.0
    assert profile["numeric_summary"]["amount"]["mean"] == 200.0


def test_csv_ingestion_rejects_non_csv_files():
    response = client.post(
        "/ingest/csv",
        files={
            "file": (
                "sales.txt",
                b"order_id,amount\n1,100\n",
                "text/plain",
            )
        },
    )

    assert response.status_code == 415


def test_csv_ingestion_rejects_empty_files():
    response = client.post(
        "/ingest/csv",
        files={
            "file": (
                "empty.csv",
                b"",
                "text/csv",
            )
        },
    )

    assert response.status_code == 400


# --------------------------------------------------
# CSV processing tests
# --------------------------------------------------

def test_csv_processing_removes_duplicates_and_returns_report():
    sample_csv = (
        "order_id,amount,region\n"
        "1,100,North\n"
        "2,,South\n"
        "2,,South\n"
        "3,300,East\n"
    )

    response = client.post(
        "/ingest/process/csv",
        files={
            "file": (
                "sales.csv",
                sample_csv.encode("utf-8"),
                "text/csv",
            )
        },
    )

    assert response.status_code == 200

    assert response.headers["content-type"].startswith(
        "application/zip"
    )

    with zipfile.ZipFile(
        io.BytesIO(response.content)
    ) as archive:
        assert set(archive.namelist()) == {
            "sales_cleaned.csv",
            "report.json",
        }

        cleaned_csv = archive.read(
            "sales_cleaned.csv"
        ).decode("utf-8")

        report = json.loads(
            archive.read("report.json").decode("utf-8")
        )

    cleaned_rows = list(
        csv.DictReader(io.StringIO(cleaned_csv))
    )

    assert len(cleaned_rows) == 3

    assert report["input_rows"] == 4
    assert report["output_rows"] == 3
    assert report["duplicates_removed"] == 1

    assert report["missing_values_before"]["amount"] == 2
    assert report["missing_values_after"]["amount"] == 1


def test_csv_processing_rejects_non_csv_files():
    response = client.post(
        "/ingest/process/csv",
        files={
            "file": (
                "sales.txt",
                b"order_id,amount\n1,100\n",
                "text/plain",
            )
        },
    )

    assert response.status_code == 415


def test_csv_processing_rejects_empty_files():
    response = client.post(
        "/ingest/process/csv",
        files={
            "file": (
                "empty.csv",
                b"",
                "text/csv",
            )
        },
    )

    assert response.status_code == 400