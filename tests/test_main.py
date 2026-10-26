from fastapi.testclient import TestClient

from app.main import app

# Create a client for testing the FastAPI application.
client = TestClient(app)


# --------------------------------------------------
# Original application tests
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
# CSV ingestion tests
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