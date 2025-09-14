# qrparser

A Python microservice for extracting QR codes from PDF files.  
Stateless, modular, built with OOP principles and Python best practices.  
No dependencies on external web services.

## Structure
- `src/qrparser/` — package code (config, core, services, web)
- `tests/` — test suite (pytest)
- consistent styles: `.editorconfig`, `.gitattributes`, `.gitignore`

## Requirements
- Python 3.11+

## Quick Start (local, Windows PowerShell)
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
# (optional) install pytest for running tests:
python -m pip install -U pip
python -m pip install pytest
pytest -q
```
## Run with Docker Compose
``` bash
# Clone the repository
git clone https://github.com/NlightN22/qrparser.git
cd qrparser

# Build and start the service
docker compose up -d
```
The service will be available at:
http://localhost:8000

Health check: http://localhost:8000/health

API docs (Swagger UI): http://localhost:8000/docs

API docs (ReDoc): http://localhost:8000/redoc