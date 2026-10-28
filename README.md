# CareerLens AI — Resume Analyzer & Job Recommendation Platform

A full-stack portfolio MVP that extracts resume text, detects skills, provides resume structure feedback, and recommends roles using TF-IDF text similarity plus skill overlap.

## Tech stack
- **Frontend:** React, Vite, Lucide icons, responsive CSS
- **Backend:** Python, FastAPI
- **NLP / matching:** scikit-learn TF-IDF + cosine similarity, skill keyword extraction
- **Resume parsing:** pypdf, python-docx

## Requirements
- Python 3.10 or newer
- Node.js 18 or newer

## Run locally (two terminals)

### 1. Start the backend
```bash
cd backend
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# If PowerShell blocks activation, use: .venv\Scripts\python.exe -m pip install -r requirements.txt
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Backend runs at `http://127.0.0.1:8000`; API docs at `http://127.0.0.1:8000/docs`.

### 2. Start the frontend in a second terminal
```bash
cd frontend
npm install
npm run dev
```
Open the local URL Vite prints (usually `http://localhost:5173`). Keep both terminals running.

## Features
- Upload PDF, DOCX, or TXT resume (8 MB maximum)
- Extract text and detect a set of common technical skills
- Resume structure checks for contact, skills, education, experience/projects
- Actionable resume suggestions and approximate strength indicator
- Job recommendations ranked by TF-IDF similarity and skill overlap
- Matched and missing skills per role
- Custom job-description matching endpoint
- Responsive dashboard and FastAPI interactive API documentation

## API endpoints
- `GET /api/health` — backend status
- `GET /api/jobs` — sample role catalogue
- `POST /api/analyze` — multipart resume upload
- `POST /api/analyze-text` — analyze raw resume text as JSON `{ "text": "..." }`
- `POST /api/match-custom` — compare resume text with a job description

## Important limitations
The included job catalogue is **sample data**, not live vacancies. Matching and resume-strength scores are heuristic estimates for learning and demonstration, not an ATS guarantee or a hiring decision. The app does not persist uploaded resumes; keep the demo local and avoid uploading sensitive personal information to untrusted deployments. Scanned PDFs may need OCR, which is not included in this MVP.

## Suggested future upgrades
1. Add authentication and user profiles.
2. Store job listings in PostgreSQL and import verified live vacancies through permitted APIs.
3. Add OCR for scanned resumes and robust section parsing.
4. Add a feedback loop and evaluate ranking against labelled examples.
5. Deploy with environment-based API URLs, rate limits, logging, and privacy controls.
