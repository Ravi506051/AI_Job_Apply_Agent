"""Human-reviewed Playwright autofill helper. Never submits applications."""
import argparse
import json
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

FIELDS = {
    "first_name": [r"first name", r"given name"],
    "last_name": [r"last name", r"family name", r"surname"],
    "full_name": [r"full name", r"your name"],
    "email": [r"email", r"e-mail"],
    "phone": [r"phone", r"mobile", r"telephone"],
    "location": [r"city", r"location", r"current address"],
    "linkedin": [r"linkedin"],
    "github": [r"github"],
    "portfolio": [r"portfolio", r"website"],
    "summary": [r"cover letter", r"summary", r"about you", r"why.*role"],
}

def fill_field(page, patterns, value):
    if not value:
        return False
    for pattern in patterns:
        try:
            field = page.get_by_label(re.compile(pattern, re.I)).first
            if field.count() and field.is_visible() and field.is_enabled():
                field.fill(str(value), timeout=1500)
                return True
        except Exception:
            continue
    return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="Official job application URL")
    parser.add_argument("--profile", default="profile.json")
    parser.add_argument("--resume", default="")
    args = parser.parse_args()

    profile = json.loads(Path(args.profile).read_text(encoding="utf-8"))
    filled, manual = [], []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(args.url, wait_until="domcontentloaded", timeout=60000)

        for key, patterns in FIELDS.items():
            if fill_field(page, patterns, profile.get(key, "")):
                filled.append(key)
            elif profile.get(key):
                manual.append(key)

        if args.resume:
            try:
                upload = page.locator('input[type="file"]').first
                if upload.count():
                    upload.set_input_files(str(Path(args.resume).expanduser().resolve()))
                    filled.append("resume")
                else:
                    manual.append("resume upload")
            except Exception:
                manual.append("resume upload")

        print("\nAutofill report")
        print("Filled:", ", ".join(filled) or "No fields confidently detected")
        print("Manual review:", ", ".join(manual) or "None detected")
        print("\nReview all fields. Handle CAPTCHA, OTP, login and eligibility questions yourself.")
        print("This tool NEVER clicks Submit. Submit manually only after checking every answer.")
        input("Press Enter to close the browser...")
        browser.close()

if __name__ == "__main__":
    main()
