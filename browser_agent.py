"""Local, visible Playwright helper for job applications.

It can prefill confidently labelled fields. Submission is disabled by default and,
when explicitly enabled, requires the user to type SUBMIT after reviewing the page.
Use only on employer portals that permit this kind of browser automation.
"""
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

SUBMIT_LABELS = [
    re.compile(r"^submit application$", re.I),
    re.compile(r"^submit$", re.I),
    re.compile(r"^apply now$", re.I),
]

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

def find_submit_button(page):
    matches = []
    for label in SUBMIT_LABELS:
        try:
            locator = page.get_by_role("button", name=label)
            for index in range(min(locator.count(), 3)):
                item = locator.nth(index)
                if item.is_visible() and item.is_enabled():
                    matches.append(item)
        except Exception:
            pass
    # Avoid clicking when a page has ambiguous or duplicate submit controls.
    return matches[0] if len(matches) == 1 else None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="Official job application URL")
    parser.add_argument("--profile", default="profile.json")
    parser.add_argument("--resume", default="")
    parser.add_argument("--allow-submit", action="store_true",
                        help="Enable one final submission after a typed confirmation")
    parser.add_argument("--browser-profile", default=".job-agent-browser",
                        help="Local browser profile directory; keeps login session on this computer")
    args = parser.parse_args()

    if not args.url.startswith("https://"):
        raise SystemExit("Only HTTPS application URLs are allowed.")
    profile_path = Path(args.profile)
    if not profile_path.is_file():
        raise SystemExit(f"Profile file not found: {profile_path}")
    profile = json.loads(profile_path.read_text(encoding="utf-8"))

    filled, manual = [], []
    with sync_playwright() as playwright:
        context = playwright.chromium.launch_persistent_context(
            user_data_dir=args.browser_profile,
            headless=False,
            accept_downloads=False,
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(args.url, wait_until="domcontentloaded", timeout=60000)

        print("\nIf login or OTP is required, complete it manually in the browser.")
        input("After the application form is visible, press Enter here to autofill...")

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
        print("\nReview every field, resume, job title, eligibility answer and declaration.")
        print("Do not submit if any answer is unknown, inaccurate, or the portal disallows automation.")

        if args.allow_submit:
            button = find_submit_button(page)
            if button is None:
                print("No unique supported submit button found; nothing was submitted.")
            else:
                confirmation = input(
                    "\nTo submit THIS application now, type SUBMIT exactly. "
                    "Anything else cancels: "
                )
                if confirmation == "SUBMIT":
                    button.click()
                    page.wait_for_timeout(1500)
                    print("Submit button clicked. Check the page for the employer's confirmation.")
                else:
                    print("Cancelled. Nothing was submitted.")
        else:
            print("Submission is disabled. Re-run with --allow-submit only if this portal permits automation.")

        input("Press Enter to close the browser...")
        context.close()

if __name__ == "__main__":
    main()
