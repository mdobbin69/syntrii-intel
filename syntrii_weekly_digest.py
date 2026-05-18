#!/usr/bin/env python3
"""
Syntrii Weekly Intelligence Digest
A single aggregated weekly report covering all three Syntrii pillars:
  1. Platforms & Products — competitive and technology intelligence
  2. Strategic Advisory   — regulatory, operator, and policy signals
  3. Growth & Innovation  — M&A, ventures, new markets, emerging tech

Delivered every Monday morning (AEST) via email.

Setup instructions at the bottom of this file.
"""

import anthropic
import time
import smtplib
import os
from datetime import date, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ─────────────────────────────────────────────
# CONFIGURATION — edit these before first run
# ─────────────────────────────────────────────

RECIPIENT_EMAILS = [
    "matt@syntrii.com",
    "laurent@syntrii.com",
]

SENDER_EMAIL    = os.environ.get("DIGEST_SENDER_EMAIL")    # e.g. digest@gmail.com
SENDER_PASSWORD = os.environ.get("DIGEST_SENDER_PASSWORD") # Gmail App Password
SMTP_HOST       = "smtp.gmail.com"
SMTP_PORT       = 587

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

# ─────────────────────────────────────────────
# RESEARCH PROMPTS — split across two API calls
# to ensure all four sections complete fully
# ─────────────────────────────────────────────

def build_prompt_part1() -> str:
    today      = date.today()
    week_start = (today - timedelta(days=7)).strftime("%B %d")
    week_end   = today.strftime("%B %d, %Y")

    return f"""
Today is {week_end}. You are a senior intelligence analyst for Syntrii — a digital utility 
platform for the global gaming, entertainment, and hospitality sector.

Search the web and produce SECTION 1 and SECTION 2 of a weekly briefing covering 
{week_start} – {week_end}.

STRICT OUTPUT RULES — failure to follow these will make the report unusable:
- EXACTLY 4 stories per section. No more, no fewer.
- EXACTLY 2 sentences per story body. No more.
- Syntrii Angle: one short clause (max 20 words).
- Source: publication name and URL only.
- Clean HTML output only — no markdown, no preamble, no commentary.
- Do NOT number stories or add any text outside the HTML structure below.

HTML structure for each story:
<h3>[Headline]</h3>
<p>[2 sentences max.]</p>
<div class="angle"><strong>Syntrii Angle:</strong> [max 20 words]</div>
<p class="source"><strong>Source:</strong> <a href="URL">Publication</a></p>

---

## SECTION 1 — PLATFORMS & PRODUCTS
Search for:
- Cashless gaming technology deployments globally
- Loyalty, CRM, CDP platform moves: IGT, Everi, Konami, Aristocrat, NRT, Paysign, 
  Sightline, Light & Wonder, Optimove
- Angel Gaming, Walker Digital Table Systems (WDTS), Bally's, LGT — any news
- Middleware/connector/integration layer vendors positioning in the gaming stack
- AI in loyalty personalisation or gaming compliance
- Australia 2028 cashless reform signals

## SECTION 2 — STRATEGIC ADVISORY
Search for:
- AUSTRAC, ClubsNSW, NICC, AGCO regulatory updates
- PAGCOR — licensing, AML, KYC, advertising, e-wallet rules
- MAS Singapore, DICJ Macau, FATF AML/CTF updates
- Mounties Group, Crown, Star, SkyCity operator news
- Solaire, Okada, Marina Bay Sands, Melco operator news
- G2E, ICE, ASEAN Gaming Summit conference news
"""


def build_prompt_part2() -> str:
    today      = date.today()
    week_start = (today - timedelta(days=7)).strftime("%B %d")
    week_end   = today.strftime("%B %d, %Y")

    return f"""
Today is {week_end}. You are a senior intelligence analyst for Syntrii — a digital utility 
platform for the global gaming, entertainment, and hospitality sector.

Search the web and produce SECTION 3 and SECTION 4 of a weekly briefing covering 
{week_start} – {week_end}.

STRICT OUTPUT RULES — failure to follow these will make the report unusable:
- EXACTLY 4 stories in Section 3. No more, no fewer.
- EXACTLY 2 sentences per story body. No more.
- Syntrii Angle: one short clause (max 20 words).
- Source: publication name and URL only.
- Section 4: exactly 3 items, 2 sentences each — no sources needed.
- Clean HTML output only — no markdown, no preamble, no commentary.

HTML structure for each Section 3 story:
<h3>[Headline]</h3>
<p>[2 sentences max.]</p>
<div class="angle"><strong>Syntrii Angle:</strong> [max 20 words]</div>
<p class="source"><strong>Source:</strong> <a href="URL">Publication</a></p>

Section 4 must be wrapped in <div class="velocity">...</div>
HTML structure for each Section 4 item:
<h3>[Story headline]</h3>
<p>[Syntrii content angle — 2 sentences on how Matt or Laurent owns this narrative.]</p>
<p><strong>Format:</strong> [LinkedIn post / IAG article / client briefing note]</p>

---

## SECTION 3 — GROWTH & INNOVATION / VENTURES
Search for:
- Gaming technology M&A and venture funding — deals, multiples, consolidation signals
- New IR market progress: Japan, Thailand, UAE, Saudi Arabia, Vietnam, South Korea
- Digital wallets, biometric identity, embedded finance applied to gaming
- Fintech or regtech vendors entering gaming compliance or loyalty
- Retail loyalty, sports betting, or financial services innovations applicable to gaming

## SECTION 4 — CONTENT VELOCITY SIGNALS
Pick the 3 strongest stories from Sections 1–3 for Syntrii thought leadership.
For each: headline, a 2-sentence content angle for Matt or Laurent, suggested format.
Wrap entire section in <div class="velocity">...</div>
"""

# ─────────────────────────────────────────────
# FETCH DIGEST FROM CLAUDE — two calls joined
# ─────────────────────────────────────────────

def fetch_section(prompt: str) -> str:
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8000,
        tools=[{
            "type": "web_search_20250305",
            "name": "web_search",
        }],
        messages=[{"role": "user", "content": prompt}],
    )

    html_content = ""
    for block in response.content:
        if block.type == "text":
            html_content += block.text

    return html_content


def fetch_digest() -> str:
    print("  → Researching Sections 1 & 2 (Platforms, Advisory)...")
    part1 = fetch_section(build_prompt_part1())

    print("  → Waiting 65 seconds to respect API rate limits...")
    time.sleep(65)

    print("  → Researching Sections 3 & 4 (Growth, Content Velocity)...")
    part2 = fetch_section(build_prompt_part2())

    return part1 + "\n" + part2

# ─────────────────────────────────────────────
# BUILD EMAIL
# ─────────────────────────────────────────────

def build_email(digest_html: str) -> str:
    today      = date.today()
    week_start = (today - timedelta(days=7)).strftime("%d %b")
    week_end   = today.strftime("%d %b %Y")

    return f"""
    <html>
    <head>
      <style>
        body       {{ font-family: 'Segoe UI', Arial, sans-serif; color: #111111;
                      max-width: 820px; margin: 0 auto; padding: 24px; }}

        /* Header */
        .header    {{ background: #1A3A3F; padding: 20px 24px; margin-bottom: 8px; }}
        .header h1 {{ margin: 0; color: #ffffff; font-size: 22px; font-weight: 600;
                      letter-spacing: 0.5px; }}
        .header h1 span {{ color: #C9A227; }}
        .subhead   {{ background: #429DA6; color: #EAF5F6; padding: 8px 24px;
                      font-size: 13px; margin-bottom: 28px; }}

        /* Section headers */
        h2         {{ color: #1A3A3F; border-bottom: 2px solid #429DA6;
                      padding-bottom: 6px; margin-top: 36px; font-size: 16px;
                      text-transform: uppercase; letter-spacing: 0.5px; }}

        /* Story headers */
        h3         {{ color: #429DA6; margin-bottom: 4px; font-size: 15px; }}

        /* Body text */
        p          {{ line-height: 1.65; margin: 6px 0; font-size: 14px; }}

        /* Syntrii angle callout */
        .angle     {{ background: #EAF5F6; border-left: 4px solid #C9A227;
                      padding: 8px 14px; margin: 10px 0 4px 0; font-size: 13px;
                      color: #1A3A3F; }}

        /* Source line */
        .source    {{ font-size: 12px; color: #888; margin: 2px 0 18px 0; }}
        .source a  {{ color: #429DA6; text-decoration: none; }}

        /* Content velocity section */
        .velocity  {{ background: #1A3A3F; color: #EAF5F6; padding: 16px 20px;
                      margin-top: 36px; }}
        .velocity h2 {{ color: #C9A227; border-bottom: 1px solid #429DA6;
                        font-size: 15px; }}
        .velocity h3 {{ color: #ffffff; font-size: 14px; }}
        .velocity p  {{ font-size: 13px; color: #EAF5F6; }}

        /* Footer */
        .footer    {{ margin-top: 40px; padding-top: 16px; border-top: 1px solid #ddd;
                      font-size: 11px; color: #aaa; }}
      </style>
    </head>
    <body>

      <div class="header">
        <h1>Syntrii <span>Weekly Intelligence</span></h1>
      </div>
      <div class="subhead">
        Week of {week_start} – {week_end} &nbsp;·&nbsp;
        Platforms &amp; Products &nbsp;·&nbsp; Strategic Advisory &nbsp;·&nbsp; Growth &amp; Innovation
      </div>

      {digest_html}

      <div class="footer">
        Produced by Syntrii Intelligence &nbsp;·&nbsp; hello@syntrii.com &nbsp;·&nbsp; syntrii.com<br>
        <em>One Digital Utility. Infinite Applications.</em>
      </div>

    </body>
    </html>
    """

# ─────────────────────────────────────────────
# SEND EMAIL
# ─────────────────────────────────────────────

def send_email(html_body: str):
    today      = date.today()
    week_start = (today - timedelta(days=7)).strftime("%d %b")
    week_end   = today.strftime("%d %b %Y")
    subject    = f"Syntrii Weekly Intelligence — {week_start}–{week_end}"

    msg            = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = SENDER_EMAIL
    msg["To"]      = ", ".join(RECIPIENT_EMAILS)

    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAILS, msg.as_string())

    print(f"✅ Weekly digest sent to {', '.join(RECIPIENT_EMAILS)}")

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    print("🔍 Researching weekly intelligence across all Syntrii pillars...")
    digest_html = fetch_digest()

    print("📧 Building and sending weekly digest email...")
    email_html = build_email(digest_html)
    send_email(email_html)

if __name__ == "__main__":
    main()


# ═══════════════════════════════════════════════════════════
# README — SETUP INSTRUCTIONS
# ═══════════════════════════════════════════════════════════
#
# STEP 1 — Anthropic API key
#   → console.anthropic.com → Settings → API Keys → Create Key
#
# STEP 2 — Gmail App Password
#   → Gmail → Manage Google Account → Security
#   → Enable 2-Step Verification if not already on
#   → App Passwords → Create → name it "Syntrii Digest"
#   → Copy the 16-char code
#
# STEP 3 — Install dependency (run once)
#   pip install anthropic
#
# STEP 4 — Test locally
#   export ANTHROPIC_API_KEY="sk-ant-..."
#   export DIGEST_SENDER_EMAIL="youraddress@gmail.com"
#   export DIGEST_SENDER_PASSWORD="xxxx xxxx xxxx xxxx"
#   python syntrii_weekly_digest.py
#
# STEP 5 — Automate via GitHub Actions (free)
#   → Create a private GitHub repo named e.g. syntrii-intel
#   → Upload this file to the repo root
#   → Create file: .github/workflows/weekly_digest.yml
#     (copy the YAML below)
#   → Add three repo secrets under Settings → Secrets → Actions:
#       ANTHROPIC_API_KEY
#       DIGEST_SENDER_EMAIL
#       DIGEST_SENDER_PASSWORD
#
# ── weekly_digest.yml ─────────────────────────────────────
#
# name: Syntrii Weekly Intelligence Digest
# on:
#   schedule:
#     - cron: '0 22 * * 0'   # 22:00 UTC Sunday = 8:00 AM AEST Monday
#   workflow_dispatch:         # manual trigger for testing
# jobs:
#   digest:
#     runs-on: ubuntu-latest
#     steps:
#       - uses: actions/checkout@v4
#       - uses: actions/setup-python@v5
#         with:
#           python-version: '3.11'
#       - run: pip install anthropic
#       - run: python syntrii_weekly_digest.py
#         env:
#           ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
#           DIGEST_SENDER_EMAIL: ${{ secrets.DIGEST_SENDER_EMAIL }}
#           DIGEST_SENDER_PASSWORD: ${{ secrets.DIGEST_SENDER_PASSWORD }}
#
# ─────────────────────────────────────────────────────────
# ESTIMATED COST
#   ~$0.50–0.80 per run (two API calls, 8k tokens each)
#   ~$2–3/month total
#   GitHub Actions: free on private repos (2,000 mins/month)
# ─────────────────────────────────────────────────────────
