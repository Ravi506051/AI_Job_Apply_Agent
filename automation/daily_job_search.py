"""Daily public job discovery for GitHub Actions. No applications are submitted."""
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import requests
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[1]
PROFILE = json.loads((ROOT / "candidate_profile.json").read_text(encoding="utf-8"))
OUT = ROOT / "jobs_feed.json"
MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
TAVILY_KEY = os.environ["TAVILY_API_KEY"]
GROQ_KEY = os.environ["GROQ_API_KEY"]

def search(query):
    response = requests.post(
        "https://api.tavily.com/search",
        json={"api_key": TAVILY_KEY, "query": query, "search_depth": "advanced",
              "max_results": 8, "include_answer": False},
        timeout=45,
    )
    response.raise_for_status()
    return response.json().get("results", [])

def main():
    queries = [
        '"Data Analyst Intern" remote India paid 2026 apply',
        '"Data Science Intern" OR "Machine Learning Intern" remote India stipend apply',
        '"AI/ML Intern" OR "Python Developer Intern" India remote careers',
        'entry level data analyst Python SQL jobs India remote careers',
    ]
    seen, jobs = set(), []
    for query in queries:
        for item in search(query):
            url = item.get("url", "").strip()
            if not url or url in seen:
                continue
            host = urlparse(url).netloc.lower()
            if not host or any(x in host for x in ("youtube.com", "facebook.com", "instagram.com")):
                continue
            seen.add(url)
            jobs.append({
                "title": item.get("title", "Job listing")[:240],
                "url": url,
                "snippet": item.get("content", "")[:1800],
                "source": host,
            })
    client = OpenAI(api_key=GROQ_KEY, base_url="https://api.groq.com/openai/v1")
    scored = []
    for offset in range(0, len(jobs), 8):
        batch = jobs[offset:offset+8]
        prompt = {
            "candidate": PROFILE,
            "jobs": batch,
            "instructions": (
                "Rank and assess each public job listing against the candidate profile. "
                "Return JSON array only, one object per input with keys title,url,company,location,"
                "employment_type,pay,match_score,reason,eligibility_notes. Score 0-100. "
                "Never invent pay, company or eligibility; use 'Not disclosed'/'Unknown'. "
                "Do not mark a listing verified or open unless the supplied snippet establishes it. "
                "Exclude obviously unrelated listings. Preserve each input URL exactly."
            )
        }
        result = client.chat.completions.create(
            model=MODEL,
            messages=[{"role":"user","content":json.dumps(prompt)}],
            temperature=0.1,
        ).choices[0].message.content.strip()
        result = re.sub(r"^\x60{3}(?:json)?\s*|\s*\x60{3}$", "", result)
        try:
            rows = json.loads(result)
            if isinstance(rows, list):
                scored.extend(rows)
        except json.JSONDecodeError:
            continue
    scored = [x for x in scored if isinstance(x, dict) and x.get("url") and int(x.get("match_score", 0) or 0) >= 35]
    scored.sort(key=lambda x: int(x.get("match_score", 0) or 0), reverse=True)
    payload = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "count": len(scored),
        "notice": "AI-ranked public search results. Verify details on the employer's official careers page before applying.",
        "jobs": scored[:30],
    }
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(payload['jobs'])} ranked job results to {OUT}")

if __name__ == "__main__":
    main()
