# AI Job Apply Agent

An AI-assisted job search and application workspace built with Streamlit. It can read a resume, discover and rank opportunities, draft application material, and track progress, with human review for application submission.

## Capabilities

- Resume parsing and candidate-profile review.
- Job discovery using configured providers.
- Role-fit ranking and application-material drafts.
- Application tracking and optional browser-assisted form filling.
- Batch discovery and scheduled GitHub Actions configuration.

## Run locally

~~~bash
git clone https://github.com/Ravi506051/AI_Job_Apply_Agent.git
cd AI_Job_Apply_Agent
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
~~~

Configure provider credentials through Streamlit secrets using .streamlit/secrets.example.toml as a guide. Review AUTOMATION_SETUP.md before enabling browser assistance. The repository also includes profile.example.json, candidate_profile.json, jobs_feed.json, and scripts for batch and browser workflows; inspect their configuration before running them.

## Application review and privacy

Treat match scores and generated text as suggestions. Verify each job, eligibility requirement, resume attachment, and form field. Keep final submission under user control and follow each site's terms, rate limits, and authentication requirements. Never commit API keys, session cookies, or private candidate data.

## Maintainer

Ravi Kumar Rao · [GitHub](https://github.com/Ravi506051)
