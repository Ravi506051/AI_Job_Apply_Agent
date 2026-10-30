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
- There is no universal auto-apply. Final submission stays with the user.

Never store passwords, session cookies, API keys or private applicant data in this repository.
