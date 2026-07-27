"""
Checks ticket.cineplexbd.com for Spider-Man: Brand New Day tickets going on
sale, and sends an email + push notification the moment they do.

Runs headless via Playwright because the site is a JS-rendered app -- a plain
HTTP request only returns an empty page shell.
"""
import json
import os
import smtplib
from email.mime.text import MIMEText

import requests
from playwright.sync_api import sync_playwright

STATE_FILE = "state.json"
URL = "https://ticket.cineplexbd.com/home"

# Add/remove keywords if the site spells the title differently
MOVIE_KEYWORDS = ["spider-man", "spider man", "brand new day"]

# Dhaka-area Star Cineplex branches (edit this list if branches change)
DHAKA_THEATERS = [
    "bashundhara", "shimanto", "sks tower", "mohakhali", "mirpur",
    "military museum", "uttara", "centrepoint", "dhanmondi", "narayanganj",
]

BOOKABLE_WORDS = [
    "buy ticket", "buy now", "book now", "book ticket", "select seat", "book tickets",
]


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"notified": False}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def get_rendered_text():
    """Load the page in a real (headless) browser and return its visible text."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(URL, wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(3000)  # let the SPA finish rendering
        text = page.inner_text("body")
        browser.close()
        return text


def check_bookable(text):
    """
    Look for the movie title in the rendered text, then check whether a
    'buy/book' style call-to-action appears near it (vs. just a "coming soon"
    listing). Returns (bookable: bool, status: str, matched_theaters: list).
    """
    lower = text.lower()
    windows = []
    for kw in MOVIE_KEYWORDS:
        start = 0
        while True:
            i = lower.find(kw, start)
            if i == -1:
                break
            windows.append(lower[max(0, i - 400): i + 400])
            start = i + 1

    if not windows:
        return False, "not_listed_yet", []

    for window in windows:
        has_cta = any(bw in window for bw in BOOKABLE_WORDS)
        matched = [t for t in DHAKA_THEATERS if t in window]
        if has_cta:
            return True, "bookable", matched

    return False, "listed_but_not_bookable", []


def send_email(subject, body):
    user = os.environ["GMAIL_USER"]
    pw = os.environ["GMAIL_APP_PASSWORD"]
    to = os.environ["TO_EMAIL"]
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = to
    with smtplib.SMTP("smtp.gmail.com", 587) as s:
        s.starttls()
        s.login(user, pw)
        s.send_message(msg)


def send_push(message):
    topic = os.environ.get("NTFY_TOPIC")
    if not topic:
        return
    requests.post(
        f"https://ntfy.sh/{topic}",
        data=message.encode("utf-8"),
        headers={"Title": "Spider-Man tickets are LIVE!", "Priority": "urgent", "Tags": "spider,ticket"},
        timeout=15,
    )


def main():
    state = load_state()
    text = get_rendered_text()
    bookable, status, theaters = check_bookable(text)
    print(f"Status: {status} | matched Dhaka theaters in nearby text: {theaters}")

    if bookable and not state.get("notified"):
        subject = "Spider-Man: Brand New Day tickets are LIVE on Cineplex!"
        body = (
            "Tickets for Spider-Man: Brand New Day just went live on "
            "ticket.cineplexbd.com. Go book now:\n\nhttps://ticket.cineplexbd.com/home"
        )
        try:
            send_email(subject, body)
            print("Email sent.")
        except Exception as e:
            print("Email failed:", e)
        try:
            send_push(body)
            print("Push sent.")
        except Exception as e:
            print("Push failed:", e)

        state["notified"] = True

    save_state(state)


if __name__ == "__main__":
    main()
