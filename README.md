# BatchPilot

### Python-Based Data Ingestion and Processing Platform

BatchPilot is a Python application that accepts CSV files, generates
data-quality profiles, removes duplicate records, and produces
cleaned datasets with processing reports.

The project is being developed to demonstrate Python application
development, Docker containerization, CI/CD automation, and cloud deployment.

## Features

- REST API built with FastAPI
- CSV ingestion and validation
- Data profiling with Pandas
- Missing-value and duplicate detection
- CSV cleaning and processing reports
- ZIP downloads containing processed data and reports
- Automated tests using pytest
- Code-quality checks using Ruff
- Docker image with a health check
- Multi-service deployment configuration using Docker Compose

## Technology Stack

- Python
- FastAPI
- Pandas
- Docker
- Docker Compose
- pytest
- Ruff

Planned extensions include Jenkins CI/CD, container security scanning,
and AWS deployment.

## Run Locally

Create and activate a virtual environment:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1