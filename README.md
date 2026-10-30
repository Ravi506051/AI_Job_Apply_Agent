# AI Job Apply Agent (approval-first starter)

A Streamlit app that reads a PDF resume, searches public job pages, scores role fit with Groq, drafts a cover letter, and tracks jobs you approve.

## Run locally (Python 3.11 recommended)

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
```

Create `.streamlit/secrets.toml` from `secrets.example.toml`, then add your own keys. Never commit real keys.

```bash
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Create a new GitHub repository and upload all files in this project.
2. Go to https://share.streamlit.io/ and select your repository.
3. Branch: `main`; Main file path: `app.py`.
4. In Advanced settings, choose Python 3.11 if available.
5. In Secrets, paste the contents of `secrets.example.toml` with your real keys.
6. Deploy.

## API keys

- Groq: https://console.groq.com/keys
- Tavily: https://app.tavily.com/

Check each provider's current free-tier limits and pricing before use.

## Current scope and limitations

- PDF text extraction (scanned PDFs need OCR first).
- Public web search results via Tavily; results may include irrelevant pages or duplicate listings.
- AI match score and cover-letter draft via Groq.
- SQLite tracker (ephemeral on some cloud deployments; use managed Postgres for durable multi-user/cloud storage).
- No universal auto-submit. This version intentionally does not submit applications or bypass CAPTCHA/login protections.

## Next phase: hosted browser worker

To add browser autofill, deploy a separate Playwright worker on a container-capable host (for example Render). Add authenticated job queue/API, persistent storage, and site-specific form adapters. Keep final submission behind an explicit user approval step. Do not put browser passwords or API keys in GitHub.
