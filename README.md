# AI Job Apply Agent (user-approved application workflow)

A Streamlit app that reads a PDF resume, searches public job pages, scores role fit with Groq, drafts a cover letter, and tracks jobs. A separate local Playwright helper can open an application page, prefill confidently labelled fields, and optionally click one unambiguous submit button only after the user reviews the page and types an explicit confirmation.

## Run locally (Python 3.11 recommended)

```bash
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
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

## Local browser autofill and optional user-confirmed submission

1. Copy `profile.example.json` to `profile.json` and enter accurate personal details. Keep `profile.json` private; do not commit it.
2. Open an official job application URL and run the following in a local terminal:

```bash
python browser_agent.py --url "https://the-official-application-url" --profile profile.json --resume "C:\\path\\to\\resume.pdf"
```

The helper opens a visible Chromium browser using a local browser profile. If login or OTP is required, complete it manually in the browser. The local browser profile may retain your login session on this computer; protect it and do not upload it.

The helper fills only common fields it can confidently identify. It leaves unknown or unlabelled fields for you. Review the entire application, including eligibility, work authorization, sponsorship, salary, dates, and legal declarations.

**Submission is disabled by default.** On a portal whose terms permit this automation, you may explicitly enable the optional submit step:

```bash
python browser_agent.py --url "https://the-official-application-url" --profile profile.json --resume "C:\\path\\to\\resume.pdf" --allow-submit
```

After filling, the browser pauses for review. It will click a uniquely identified supported submit button only if you type `SUBMIT` exactly in the terminal. Otherwise it cancels. Check the employer page afterward for its actual confirmation. This is not a guarantee that every portal's form or submit control is supported.

CAPTCHA and OTP are not bypassed; handle them yourself. Never submit guessed or false answers. Do not use this helper on portals that prohibit automated browser interaction, and do not use it for mass applications.

## Review-first batch application assistant

After the daily workflow has created `jobs_feed.json`, you can open a small ranked batch locally:

```bash
python batch_apply.py --top 5 --profile profile.json --resume "C:\\path\\to\\resume.pdf"
```

For each listing, type `OPEN` to open it, complete login/OTP yourself, and press Enter when the real application form is visible. The helper fills only confidently labelled/placeholder fields and attaches your resume when there is one unambiguous file input. It pauses for you to review each job before moving on.

Submission remains off by default. If—and only if—the employer portal permits browser automation, you may enable a per-application confirmation:

```bash
python batch_apply.py --top 5 --profile profile.json --resume "C:\\path\\to\\resume.pdf" --allow-submit
```

You must type `SUBMIT` separately for each application after reviewing it. The helper will click only one uniquely identified supported submit button. It will not bypass CAPTCHA, OTP, login, or portal restrictions; unknown questions remain manual. Keep batches small and never submit inaccurate or guessed answers.

## API keys

- Groq: https://console.groq.com/keys
- Tavily: https://app.tavily.com/

Check provider pricing and limits before use.

## Current limitations

- Public job search results may be irrelevant or duplicated.
- Scanned PDFs may need OCR before text extraction works.
- SQLite storage may be ephemeral on some cloud deployments.
- Browser autofill and optional submission run locally on your computer, not on the hosted Render app.
- Job sites use different form layouts. Only common labelled fields and a small set of submit button labels are supported; some fields will need manual entry.
- The helper does not bypass CAPTCHA, OTP, login, access controls, or portal restrictions.
- Daily discovery runs through GitHub Actions, not a continuously running Render worker. The dashboard feed updates after each successful scheduled run.
- The automated discovery profile contains role/skill preferences, not the user's full resume. Interactive resume matching uses the PDF uploaded during the current app session.
- There is no universal auto-apply: each employer portal must be checked for compatibility and permitted use.

Never store passwords, session cookies, API keys or private applicant data in this repository.

## Application Safety Checklist

- Verify each job listing on the employer's official careers page before acting on it.
- Review the resume, cover letter, and every prefilled application field for accuracy.
- Keep profile files, resume copies containing personal details, and API credentials out of version control.
- Require explicit user review and confirmation before any application is submitted.
- Log application status without storing unnecessary sensitive personal information.

The job-fit score and generated application text are decision-support drafts. They can be incomplete or inaccurate, so the applicant should verify eligibility, role details, and all submitted information.

## Project Development Notes

Keep application submission user-approved: show the job URL, matched resume evidence, and drafted answers for review; never submit applications or expose personal data without explicit confirmation.

For reproducibility, record source versions, environment and dependency versions, configuration, and actual test outputs. Clearly label sample data and illustrative results; never commit secrets or private data.

### Technical Deep Dive

The application workflow separates job discovery, profile-to-role matching, draft generation, application tracking, and local browser assistance. Treat job-fit scores as ranking signals, not proof of eligibility. Verify each listing on the employer's official careers page and validate every prefilled field against the user's current resume and profile before any submission.

Suggested engineering checks: deduplicate listings by canonical URL, store API keys and applicant details outside version control, keep browser automation visible, handle CAPTCHA/OTP manually, and require explicit per-application review and confirmation. Never infer answers for legal, work-authorization, or eligibility questions.

## Application Safety and Verification

- Treat job search results and AI fit scores as recommendations, not confirmation that a vacancy is active or that an applicant is eligible.
- Verify each role on the employer's official careers page before sharing personal information or applying.
- Review every prefilled field, resume attachment, eligibility response, salary expectation, and legal declaration yourself.
- Keep browser profiles, resume files, personal profile JSON, and API credentials private; never commit them to the repository.
- Respect each job portal's terms, rate limits, CAPTCHA/OTP requirements, and explicit user-consent requirements. Submission should remain a deliberate user-controlled action.

## Automation Reliability and Responsible Job Applications

- Keep job discovery, eligibility matching, resume tailoring, and application submission as separate workflow stages.
- Require user review and explicit approval before submitting an application or sharing personal information.
- Validate job URLs, required fields, deadlines, and duplicate applications before proceeding.
- Store account credentials and API keys securely outside the repository; never commit passwords, tokens, or private resume data.
- Track each application's source, role, company, submission status, and timestamp without overstating automation success.
