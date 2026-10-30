import os, json, sqlite3
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from openai import OpenAI
import requests

load_dotenv()
st.set_page_config(page_title="AI Job Apply Agent", page_icon="🎯", layout="wide")

def secret(name, default=""):
    try:
        return st.secrets.get(name, os.getenv(name, default))
    except Exception:
        return os.getenv(name, default)

GROQ_API_KEY = secret("GROQ_API_KEY")
TAVILY_API_KEY = secret("TAVILY_API_KEY")
MODEL = secret("GROQ_MODEL", "llama-3.3-70b-versatile")
DB = "applications.db"

def db():
    con = sqlite3.connect(DB)
    con.execute("""CREATE TABLE IF NOT EXISTS applications
        (id INTEGER PRIMARY KEY, company TEXT, role TEXT, location TEXT,
         url TEXT UNIQUE, match_score INTEGER, status TEXT, added_at TEXT)""")
    con.commit()
    return con

def extract_pdf(upload):
    reader = PdfReader(upload)
    return "\n".join(page.extract_text() or "" for page in reader.pages).strip()

def groq_client():
    if not GROQ_API_KEY:
        st.error("GROQ_API_KEY missing. Add it in Streamlit Secrets.")
        st.stop()
    return OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")

def ask_ai(system, prompt):
    response = groq_client().chat.completions.create(
        model=MODEL,
        messages=[{"role":"system","content":system},{"role":"user","content":prompt}],
        temperature=0.2
    )
    return response.choices[0].message.content

def search_jobs(query, location, limit):
    if not TAVILY_API_KEY:
        st.error("TAVILY_API_KEY missing. Add it in Streamlit Secrets.")
        st.stop()
    payload = {
        "api_key": TAVILY_API_KEY,
        "query": f"{query} jobs {location} fresher internship careers apply",
        "search_depth": "advanced",
        "max_results": limit,
        "include_answer": False
    }
    r = requests.post("https://api.tavily.com/search", json=payload, timeout=45)
    r.raise_for_status()
    return r.json().get("results", [])

def parse_json(text):
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0]
    start, end = text.find("{"), text.rfind("}")
    return json.loads(text[start:end+1])

st.title("🎯 AI Job Apply Agent")
st.caption("Resume-based job discovery • AI matching • tailored application drafts • approval-first workflow")

with st.sidebar:
    st.header("Your job preferences")
    roles = st.text_area("Target roles", "Data Analyst Intern, Data Science Intern, Machine Learning Intern, AI/ML Intern, Python Developer")
    location = st.text_input("Location", "India / Remote")
    min_stipend = st.text_input("Minimum stipend", "₹10,000/month")
    limit = st.slider("Search results", 5, 20, 10)
    st.info("The agent prepares applications. You review every form and submit it yourself.")

resume = st.file_uploader("Upload your latest resume (PDF)", type=["pdf"])
if resume:
    try:
        resume_text = extract_pdf(resume)
        if len(resume_text) < 100:
            st.warning("Very little text extracted. Your PDF may be scanned; use an OCR-readable PDF.")
        st.success(f"Resume read: {len(resume_text)} characters")
        with st.expander("Preview extracted resume text"):
            st.text(resume_text[:5000])
        st.session_state["resume_text"] = resume_text
    except Exception as e:
        st.error(f"Could not read PDF: {e}")

if "resume_text" not in st.session_state:
    st.info("Upload your PDF resume to begin.")
else:
    if st.button("🔎 Find matching jobs", type="primary", use_container_width=True):
        with st.spinner("Searching public job pages..."):
            try:
                results = search_jobs(roles, location, limit)
                st.session_state["raw_jobs"] = results
            except Exception as e:
                st.error(f"Job search failed: {e}")

    for i, job in enumerate(st.session_state.get("raw_jobs", [])):
        title = job.get("title", "Job listing")
        url = job.get("url", "")
        content = job.get("content", "")
        with st.expander(f"{title} — {job.get('url','')[:90]}"):
            st.write(content[:1800])
            st.link_button("Open original job posting", url)
            if st.button("🤖 Analyse resume match", key=f"analyse_{i}"):
                prompt = f"""Compare this resume to this job. Return ONLY JSON with keys:
score (integer 0-100), role, company, location, reasons (array of 3 short strings),
missing_skills (array), eligibility_concerns (array), cover_letter (string).
Do not invent experience, qualifications, projects, dates or skills. If unknown, say unknown.
RESUME:
{st.session_state['resume_text'][:12000]}
JOB TITLE: {title}
JOB URL: {url}
JOB DESCRIPTION:
{content[:9000]}"""
                try:
                    with st.spinner("Analysing fit and drafting cover letter..."):
                        data = parse_json(ask_ai("You are a careful career assistant. Be truthful and conservative.", prompt))
                    st.session_state[f"analysis_{i}"] = data
                except Exception as e:
                    st.error(f"AI analysis failed: {e}")
            data = st.session_state.get(f"analysis_{i}")
            if data:
                st.metric("Resume match", f"{data.get('score', 0)}%")
                st.write("**Why it matches**")
                for x in data.get("reasons", []): st.write(f"- {x}")
                if data.get("missing_skills"): st.write("**Skill gaps:** " + ", ".join(data["missing_skills"]))
                if data.get("eligibility_concerns"): st.warning(" | ".join(data["eligibility_concerns"]))
                st.text_area("Draft cover letter", data.get("cover_letter", ""), key=f"letter_{i}", height=180)
                approved = st.checkbox("I reviewed this job and want to save it", key=f"approve_{i}")
                if approved and st.button("Save to application tracker", key=f"save_{i}"):
                    con = db()
                    try:
                        con.execute("INSERT OR IGNORE INTO applications(company,role,location,url,match_score,status,added_at) VALUES(?,?,?,?,?,?,?)",
                            (data.get("company","Unknown"), data.get("role",title), data.get("location",location), url,
                             int(data.get("score",0)), "Ready for manual application", datetime.now().isoformat(timespec="minutes")))
                        con.commit()
                        st.success("Saved to tracker.")
                    finally: con.close()

st.divider()
st.subheader("📋 Application tracker")
con = db()
rows = con.execute("SELECT company,role,location,match_score,status,url,added_at FROM applications ORDER BY id DESC").fetchall()
con.close()
if rows:
    for company, role, loc, score, status, url, added in rows:
        st.write(f"**{role}** — {company} | Match: {score}% | {status}")
        st.caption(f"{loc} · {added}")
        st.link_button("Open application page", url)
else:
    st.caption("No jobs saved yet.")

st.warning("This starter searches public web results and drafts applications. It does not bypass CAPTCHAs, log into job sites, or submit applications automatically. Browser auto-fill requires a separately hosted Playwright worker and site-specific field mappings.")
