from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pypdf import PdfReader
from docx import Document
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from io import BytesIO
import re

app = FastAPI(title="AI Resume Analyzer & Job Recommendation API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

JOBS = [
 {"id":1,"title":"Junior Python Developer","company":"NovaTech Solutions","location":"Bengaluru, India","type":"Full-time","skills":["Python","SQL","Git","REST API","FastAPI"],"description":"Build backend services using Python, FastAPI, SQL databases and REST APIs. Collaborate with engineers and use Git for version control.","level":"Entry level"},
 {"id":2,"title":"Java Full Stack Developer Intern","company":"BlueOrbit Labs","location":"Remote / India","type":"Internship","skills":["Java","Spring Boot","React","JavaScript","SQL","REST API"],"description":"Develop full stack applications with Java, Spring Boot, React, JavaScript and SQL. Build REST APIs and write maintainable code.","level":"Internship"},
 {"id":3,"title":"Machine Learning Intern","company":"Aster AI","location":"Hyderabad, India","type":"Internship","skills":["Python","Machine Learning","Scikit-learn","Pandas","NumPy","Statistics"],"description":"Prepare datasets and train machine learning models using Python, scikit-learn, pandas and NumPy. Evaluate model performance and communicate findings.","level":"Internship"},
 {"id":4,"title":"Data Analyst Intern","company":"InsightWorks","location":"Remote / India","type":"Internship","skills":["SQL","Python","Excel","Power BI","Tableau","Statistics"],"description":"Analyze business data, create dashboards, write SQL queries and present insights using Python, Excel, Power BI or Tableau.","level":"Internship"},
 {"id":5,"title":"Frontend Developer Intern","company":"PixelForge","location":"Bengaluru, India","type":"Internship","skills":["HTML","CSS","JavaScript","React","Git","REST API"],"description":"Create responsive user interfaces using HTML, CSS, JavaScript and React. Integrate APIs and collaborate through Git.","level":"Internship"},
 {"id":6,"title":"AI Application Developer","company":"Cognition Works","location":"Pune, India","type":"Full-time","skills":["Python","LLM","RAG","FastAPI","Vector Database","Prompt Engineering"],"description":"Build AI applications with large language models, retrieval augmented generation, vector databases, prompt engineering and FastAPI.","level":"Entry level"},
 {"id":7,"title":"Backend Developer Intern","company":"StackSpring","location":"Remote / India","type":"Internship","skills":["Java","Spring Boot","SQL","Docker","REST API","Git"],"description":"Implement backend services and REST endpoints using Java and Spring Boot, connect SQL databases, and use Docker and Git.","level":"Internship"},
 {"id":8,"title":"Cybersecurity Analyst Trainee","company":"ShieldGrid","location":"Chennai, India","type":"Full-time","skills":["Networking","Linux","SIEM","Python","Incident Response","Security"],"description":"Review security alerts, investigate logs, understand networking and Linux, and support incident response with scripting skills.","level":"Trainee"}
]

SKILL_BANK = sorted({s for job in JOBS for s in job["skills"]} | {"C++","C","OOP","Data Structures","Algorithms","MongoDB","PostgreSQL","MySQL","AWS","Azure","Kubernetes","Machine Learning","Deep Learning","TensorFlow","PyTorch","NLP","Flask","Node.js","TypeScript","Communication","Problem Solving","Agile","Linux","Cybersecurity","HTML","CSS","JavaScript","React","Java","Python","SQL"}, key=len, reverse=True)

class TextRequest(BaseModel):
    text: str

class CustomJobRequest(BaseModel):
    resume_text: str
    job_description: str

def extract_text(filename: str, data: bytes) -> str:
    ext = filename.lower().rsplit('.', 1)[-1] if '.' in filename else ''
    try:
        if ext == 'pdf':
            reader = PdfReader(BytesIO(data))
            return '\n'.join(page.extract_text() or '' for page in reader.pages)
        if ext == 'docx':
            doc = Document(BytesIO(data))
            return '\n'.join(p.text for p in doc.paragraphs)
        if ext == 'txt':
            return data.decode('utf-8', errors='ignore')
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not read resume: {exc}")
    raise HTTPException(status_code=400, detail="Upload a PDF, DOCX, or TXT file.")

def find_skills(text: str):
    lower = re.sub(r'[^a-z0-9+#.\s-]', ' ', text.lower())
    found = []
    for skill in SKILL_BANK:
        pattern = r'(?<![a-z0-9])' + re.escape(skill.lower()) + r'(?![a-z0-9])'
        if re.search(pattern, lower) and skill.lower() not in [x.lower() for x in found]:
            found.append(skill)
    return found

def score_texts(resume: str, description: str) -> int:
    if not resume.strip() or not description.strip(): return 0
    matrix = TfidfVectorizer(stop_words='english', ngram_range=(1,2)).fit_transform([resume, description])
    return round(float(cosine_similarity(matrix[0:1], matrix[1:2])[0][0]) * 100)

def analyze(resume: str):
    if len(resume.strip()) < 30:
        raise HTTPException(status_code=400, detail="The resume text is too short. Upload a fuller resume.")
    skills = find_skills(resume)
    matches = []
    for job in JOBS:
        overlap = [s for s in job['skills'] if s.lower() in {x.lower() for x in skills}]
        similarity = score_texts(resume, job['description'] + ' Skills: ' + ', '.join(job['skills']))
        skill_score = round(len(overlap) / max(len(job['skills']), 1) * 100)
        score = round(similarity * 0.55 + skill_score * 0.45)
        missing = [s for s in job['skills'] if s.lower() not in {x.lower() for x in skills}]
        matches.append({**job, 'match_score': score, 'matched_skills': overlap, 'missing_skills': missing})
    matches.sort(key=lambda j: j['match_score'], reverse=True)
    words = re.findall(r"\b[\w+#.-]+\b", resume)
    sections = {"contact": bool(re.search(r'\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b', resume)), "skills": bool(re.search(r'\bskills?\b', resume, re.I)), "education": bool(re.search(r'education|university|college|degree|bachelor|master', resume, re.I)), "experience_or_projects": bool(re.search(r'experience|internship|projects?', resume, re.I))}
    tips = []
    if not sections['contact']: tips.append("Add a professional email address in your contact section.")
    if not sections['skills']: tips.append("Add a clearly labelled Skills section with relevant technical skills.")
    if not sections['education']: tips.append("Include your education, degree, institution and expected graduation year.")
    if not sections['experience_or_projects']: tips.append("Add projects, internships or practical experience with measurable outcomes.")
    if len(words) < 120: tips.append("Consider adding more specific project details, tools used and results; this resume appears quite short.")
    if not tips: tips.append("Tailor your summary and project bullets to each job, using concrete outcomes and relevant keywords.")
    return {"word_count":len(words), "skills":skills, "sections":sections, "resume_strength": min(100, max(25, 35 + len(skills)*5 + sum(sections.values())*6)), "suggestions":tips, "recommendations":matches[:6]}

@app.get("/api/health")
def health(): return {"status":"ok", "service":"AI Resume Analyzer API"}

@app.get("/api/jobs")
def jobs(): return JOBS

@app.post("/api/analyze")
async def analyze_resume(file: UploadFile = File(...)):
    data = await file.read()
    if len(data) > 8 * 1024 * 1024: raise HTTPException(status_code=413, detail="File size must be 8 MB or less.")
    resume = extract_text(file.filename or '', data)
    result = analyze(resume)
    result['filename'] = file.filename
    return result

@app.post("/api/analyze-text")
def analyze_resume_text(payload: TextRequest): return analyze(payload.text)

@app.post("/api/match-custom")
def match_custom(payload: CustomJobRequest):
    resume_skills = find_skills(payload.resume_text)
    job_skills = find_skills(payload.job_description)
    matched = [s for s in job_skills if s.lower() in {x.lower() for x in resume_skills}]
    missing = [s for s in job_skills if s.lower() not in {x.lower() for x in resume_skills}]
    return {"match_score": score_texts(payload.resume_text, payload.job_description), "resume_skills": resume_skills, "job_skills": job_skills, "matched_skills": matched, "missing_skills": missing}
