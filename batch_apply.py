"""Review-first batch runner for the AI Job Apply Agent.

Reads ranked jobs from jobs_feed.json and opens one official HTTPS listing at a
time in a visible local browser. It never submits automatically. Each application
requires a separate, explicit SUBMIT confirmation after manual review.
"""
import argparse
import json
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

FIELDS = {
    "full_name": [r"full name", r"your name", r"name"],
    "first_name": [r"first name", r"given name"],
    "last_name": [r"last name", r"family name", r"surname"],
    "email": [r"email", r"e-mail"],
    "phone": [r"phone", r"mobile", r"telephone"],
    "location": [r"city", r"location", r"current address"],
    "linkedin": [r"linkedin"],
    "github": [r"github"],
    "portfolio": [r"portfolio", r"personal website"],
    "summary": [r"cover letter", r"summary", r"about you", r"why.*role"],
}

def safe_url(value):
    try:
        parsed = urlparse(value)
        return parsed.scheme == "https" and bool(parsed.netloc)
    except Exception:
        return False

def fill_one(page, patterns, value):
    if not value:
        return False
    for pattern in patterns:
        # Prefer accessible labels and placeholders; avoid guessing by position.
        for getter in (
            lambda: page.get_by_label(__import__("re").compile(pattern, __import__("re").I)),
            lambda: page.get_by_placeholder(__import__("re").compile(pattern, __import__("re").I)),
        ):
            try:
                locator = getter()
                if locator.count() == 1 and locator.is_visible() and locator.is_enabled():
                    locator.fill(str(value), timeout=1800)
                    return True
            except Exception:
                pass
    return False

def main():
    ap = argparse.ArgumentParser(description="Open and prepare a shortlist of applications for your review.")
    ap.add_argument("--feed", default="jobs_feed.json")
    ap.add_argument("--profile", default="profile.json")
    ap.add_argument("--resume", default="")
    ap.add_argument("--top", type=int, default=5, help="Maximum number of listings to review (1-10)")
    ap.add_argument("--allow-submit", action="store_true", help="Enable per-job explicit submission confirmation")
    ap.add_argument("--browser-profile", default=".job-agent-browser")
    args = ap.parse_args()

    if not 1 <= args.top <= 10:
        raise SystemExit("--top must be between 1 and 10. Keep batches small and review each job.")
    feed_path, profile_path = Path(args.feed), Path(args.profile)
    if not feed_path.is_file() or not profile_path.is_file():
        raise SystemExit("Missing jobs feed or profile. Check --feed and --profile.")
    feed = json.loads(feed_path.read_text(encoding="utf-8"))
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    jobs = [j for j in feed.get("jobs", []) if safe_url(j.get("url", ""))]
    jobs.sort(key=lambda j: int(j.get("match_score", 0) or 0), reverse=True)
    jobs = jobs[:args.top]
    if not jobs:
        raise SystemExit("No valid HTTPS job URLs found in the feed.")

    print(f"Found {len(jobs)} ranked listings. Each one requires your review.")
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=args.browser_profile, headless=False
        )
        page = context.pages[0] if context.pages else context.new_page()
        try:
            for number, job in enumerate(jobs, 1):
                print("\n" + "=" * 68)
                print(f"{number}/{len(jobs)} | {job.get('title', 'Job')} | Match {job.get('match_score', '—')}%")
                print(f"Source: {job.get('company', 'Unknown')} | {job.get('location', 'Unknown')}")
                print(job.get("url"))
                decision = input("Open this listing? Type OPEN (anything else skips): ").strip()
                if decision != "OPEN":
                    continue
                page.goto(job["url"], wait_until="domcontentloaded", timeout=60000)
                print("Complete login/OTP yourself if required. Confirm this is the employer's real application form.")
                input("When the application form is visible, press Enter to fill common fields...")
                filled, manual = [], []
                for key, patterns in FIELDS.items():
                    if fill_one(page, patterns, profile.get(key, "")):
                        filled.append(key)
                    elif profile.get(key):
                        manual.append(key)
                if args.resume:
                    try:
                        upload = page.locator('input[type="file"]')
                        if upload.count() == 1:
                            upload.set_input_files(str(Path(args.resume).expanduser().resolve()))
                            filled.append("resume")
                        else:
                            manual.append("resume upload")
                    except Exception:
                        manual.append("resume upload")
                print("Autofilled:", ", ".join(filled) or "none")
                print("Manual review:", ", ".join(manual) or "No unmatched profile fields detected")
                print("Check every answer, especially eligibility, dates, salary, work authorization and declarations.")
                if args.allow_submit:
                    confirmation = input("After reviewing, type SUBMIT to click the visible submit button once: ").strip()
                    if confirmation == "SUBMIT":
                        import re
                        candidates = []
                        for label in (r"^submit application$", r"^submit$", r"^apply now$"):
                            loc = page.get_by_role("button", name=re.compile(label, re.I))
                            for ix in range(loc.count()):
                                item = loc.nth(ix)
                                if item.is_visible() and item.is_enabled():
                                    candidates.append(item)
                        if len(candidates) == 1:
                            candidates[0].click()
                            print("Button clicked. Verify the employer's confirmation on the page.")
                        else:
                            print("No unique supported submit button; nothing was clicked.")
                    else:
                        print("Skipped submission.")
                else:
                    print("Submission disabled. Use --allow-submit only where the employer permits browser automation.")
                input("Press Enter to continue to the next listing...")
        finally:
            context.close()

if __name__ == "__main__":
    main()
