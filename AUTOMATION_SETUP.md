# Browser automation setup

This project uses a human-reviewed browser autofill workflow. It can open an official application URL and fill common profile fields where labels are confidently detected. The user must review every field and click Submit manually.

It must never bypass CAPTCHA, automate OTP, or submit applications without explicit user approval.

## Local setup

1. Use Python 3.11 or newer.
2. Install dependencies: `pip install -r requirements.txt`.
3. Install Chromium: `playwright install chromium`.
4. Create a local profile JSON from `profile.example.json` and enter accurate details only.
5. Run the browser helper against an official application URL and review all fields.

Never commit passwords, session cookies, API keys, or other secrets.
