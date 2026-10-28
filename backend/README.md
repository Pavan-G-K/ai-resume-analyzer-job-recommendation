# Backend API

FastAPI service for resume text extraction, skill detection, resume feedback, and TF-IDF-based job matching.

## Setup (Python 3.10+)

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API docs: http://127.0.0.1:8000/docs

Supported resume files: PDF, DOCX, TXT (maximum 8 MB). This is a demo matching engine, not an employment or ATS guarantee.
