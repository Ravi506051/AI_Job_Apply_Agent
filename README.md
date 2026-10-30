# AI Job Apply Agent (approval-first)

A Streamlit app that reads a PDF resume, searches public job pages, scores role fit with Groq, drafts a cover letter, and tracks jobs. A separate Playwright helper can open an application page and prefill common fields for manual review.

## Run locally (Python 3.11 recommended)

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
streamlit run app.py
```

Create `.streamlit/secrets.toml` from `secrets.example.toml` and add your own API keys. Never commit real keys.

## Daily automated job discovery

A GitHub Actions workflow searches public job pages every day at 7:00 PM India time (13:30 UTC), removes duplicate URLs, asks Groq to rank listings against the non-personal candidate profile in `candidate_profile.json`, and publishes up to 30 results to `jobs_feed.json`. The Streamlit dashboard reads this feed automatically.

### One-time setup

1. Open the repository on GitHub → **Settings → Secrets and variables → Actions**.
2. Add repository secrets named `GROQ_API_KEY` and `TAVILY_API_KEY`. Use the same providers as the Streamlit app; secret values are not committed.
3. Open **Actions → Daily job discovery → Run workflow** to test the first run. Later runs are scheduled daily.
4. Open the Streamlit dashboard and refresh after the workflow completes.

The workflow uses public search snippets; it cannot guarantee that a vacancy is still open or that every detail is correct. Verify the employer's official careers page before applying. It does not submit applications.

## Browser autofill helper (local)

1. Copy `profile.example.json` to `profile.json` and enter accurate personal details. Keep `profile.json` private; do not commit it.
2. Open an official job application URL and run:

```bash
python browser_agent.py --url "https://the-official-application-url" --profile profile.json --resume "C:\\path\\to\\resume.pdf"
```

The helper opens a visible Chromium browser and fills only common fields it can confidently identify. Review every field and complete any missing information yourself.

**It never clicks Submit.** CAPTCHA, OTP, login, legal declarations, work authorization and sponsorship questions require your direct attention. Never provide false or guessed answers.

## API keys

- Groq: https://console.groq.com/keys
- Tavily: https://app.tavily.com/

Check provider pricing and limits before use.

## Current limitations

- Public job search results may be irrelevant or duplicated.
- Scanned PDFs may need OCR before text extraction works.
- SQLite storage may be ephemeral on some cloud deployments.
- Browser autofill is a local helper, not a hosted always-on worker. Job sites use different form layouts, so some fields will need manual entry.
- Daily discovery runs through GitHub Actions, not a continuously running Render worker. The dashboard feed updates after each successful scheduled run.
- The automated discovery profile contains role/skill preferences, not the user's full resume. The interactive resume matching feature still uses the PDF uploaded during the current app session.
- There is no universal auto-apply. Final submission stays with the user.

Never store passwords, session cookies, API keys or private applicant data in this repository.
