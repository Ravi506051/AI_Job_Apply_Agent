# AI Job Apply Agent

An AI-assisted job discovery and application-support tool. The project reads a resume, finds public job listings, estimates role fit, drafts application material and helps track opportunities. Any browser-based form assistance is designed to remain user-reviewed and user-approved.

## Main capabilities
- Extract information from a PDF resume.
- Discover job listings from configured public sources.
- Rank opportunities against a candidate profile.
- Draft tailored cover letters and application notes.
- Track discovered roles and application status.
- Provide an optional browser helper for form assistance with explicit user confirmation.

## Technology
Python · Streamlit · Groq API · Playwright · GitHub Actions

## Run locally
```bash
git clone https://github.com/Ravi506051/AI_Job_Apply_Agent.git
cd AI_Job_Apply_Agent
python -m venv .venv
# Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
playwright install chromium
streamlit run app.py
```
Configure required API keys using the secrets mechanism documented in the repository. Never commit real credentials.

## Scheduled discovery
The repository includes a GitHub Actions workflow for scheduled job discovery. Configure the required repository secrets in GitHub Actions settings and review the workflow file for its schedule, data sources and output format before enabling it.

## Human approval and safety
- Treat role-fit scores as recommendations, not guarantees.
- Verify job details and eligibility on the employer's official site.
- Review every field before submitting an application.
- Never submit an application without explicit user approval.
- Protect resume data and avoid logging personal information.
- Respect website terms, rate limits and robots policies.

## Future improvements
Add stronger duplicate detection, explainable role matching, application status analytics, test coverage and safer browser-session handling.

## Maintainer
**Ravi Kumar Rao** · [GitHub](https://github.com/Ravi506051)
