"""
Naukri.com expected salary updater using Playwright.
Run on Ubuntu:
  python3 -m venv .venv
  source .venv/bin/activate
  pip install playwright
  playwright install chromium
  python naukri_salary_updater.py --email you@example.com --password secret --salary 1200000
"""

import argparse
import sys
from typing import List

from playwright.sync_api import Playwright, TimeoutError, sync_playwright

LOGIN_URL = "https://www.naukri.com/nlogin/login"
PROFILE_URL = "https://www.naukri.com/mnjuser/profile"


def first_working(page, selectors: List[str]):
    for selector in selectors:
        try:
            handle = page.locator(selector)
            if handle.first.is_visible(timeout=2000):
                return handle
        except Exception:
            continue
    raise TimeoutError(f"None of the selectors matched: {selectors}")


def login(page, email: str, password: str):
    page.goto(LOGIN_URL, wait_until="domcontentloaded")

    email_locators = [
        "#usernameField",
        "input[name='email']",
        "input[type='email']",
        "input[placeholder*='Email']",
        "input[placeholder*='Username']",
    ]
    password_locators = [
        "#passwordField",
        "input[name='PASSWORD']",
        "input[type='password']",
        "input[placeholder*='Password']",
    ]
    login_button_locators = [
        "button[type='submit']",
        "button:has-text('Login')",
        "button:has-text('log in')",
        "#loginButton",
    ]

    first_working(page, email_locators).fill(email)
    first_working(page, password_locators).fill(password)
    first_working(page, login_button_locators).click()

    page.wait_for_url("**naukri.com/**", timeout=20000)


def update_salary(page, salary: int):
    page.goto(PROFILE_URL, wait_until="domcontentloaded")

    edit_candidates = [
        "[data-section='salary'] button:has-text('Edit')",
        "section:has-text('Salary') button:has-text('Edit')",
        "button[title*='Salary']",
        "a:has-text('Edit Salary')",
        "button:has-text('Edit')",
    ]
    salary_input_candidates = [
        "input[name='annualSalary']",
        "input[name='annual_ctc']",
        "input[id*='salary']",
        "input[placeholder*='Salary']",
    ]
    save_candidates = [
        "button:has-text('Save')",
        "button:has-text('Update')",
        "button:has-text('Submit')",
    ]

    first_working(page, edit_candidates).click()
    salary_input = first_working(page, salary_input_candidates)
    salary_input.click()
    salary_input.fill(str(salary))
    first_working(page, save_candidates).click()

    page.wait_for_timeout(2000)


def run(playwright: Playwright, email: str, password: str, salary: int, headless: bool):
    browser = playwright.chromium.launch(headless=headless)
    context = browser.new_context()
    page = context.new_page()

    try:
        login(page, email, password)
        update_salary(page, salary)
        print("Salary update attempt completed. Verify in your profile.")
    finally:
        context.close()
        browser.close()


def parse_args():
    parser = argparse.ArgumentParser(description="Update expected annual salary on Naukri.com")
    parser.add_argument("--email", required=True, help="Naukri login email")
    parser.add_argument("--password", required=True, help="Naukri login password")
    parser.add_argument("--salary", required=True, type=int, help="Expected annual salary in INR (e.g., 1200000)")
    parser.add_argument("--headed", action="store_true", help="Run with visible browser for debugging")
    return parser.parse_args()


def main():
    args = parse_args()
    with sync_playwright() as playwright:
        try:
            run(playwright, args.email, args.password, args.salary, headless=not args.headed)
        except TimeoutError as exc:
            print(f"Timed out waiting for a page element: {exc}", file=sys.stderr)
            sys.exit(1)
        except Exception as exc:  # pragma: no cover
            print(f"Unexpected error: {exc}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
