#!/usr/bin/env python3
"""
Syntrii Weekly Intelligence Digest
A single aggregated weekly report covering all three Syntrii pillars:
  1. Platforms & Products — competitive and technology intelligence
  2. Strategic Advisory   — regulatory, operator, and policy signals
  3. Growth & Innovation  — M&A, ventures, new markets, emerging tech

Delivered every Monday morning (AEST) via email.

Architecture: 4 API calls total
  Call 1 — Research Sections 1 & 2 (web search, raw intel output)
  Call 2 — Write Sections 1 & 2 HTML (no web search, pure writing)
  Call 3 — Research Sections 3 & 4 (web search, raw intel output)
  Call 4 — Write Sections 3 & 4 HTML (no web search, pure writing)

This separation ensures web search overhead never competes with HTML output tokens.

Setup instructions at the bottom of this file.
"""

import anthropic
import smtplib
import os
import time
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

SENDER_EMAIL    = os.environ.get("DIGEST_SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("DIGEST_SENDER_PASSWORD")
SMTP_HOST       = "smtp.gmail.com"
SMTP_PORT       = 587

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

# ─────────────────────────────────────────────
# STEP 1 — RESEARCH PROMPTS (web search enabled)
# These calls gather raw intel only — no HTML output
# ─────────────────────────────────────────────

def build_research_prompt_part1() -> str:
    today      = date.today()
    week_start = (today - timedelta(days=7)).strftime("%B %d")
    week_end   = today.strftime("%B %d, %Y")

    return f"""
Today is {week_end}. You are a senior intelligence analyst for Syntrii — a digital utility 
platform for the global gaming, entertainment, and hospitality sector.

Search the web and gather the most significant news from {week_start} – {week_end} 
across the following topics. Output raw research notes only — bullet points, no HTML.
Aim for 3 strong stories per topic area. Include source URLs.

TOPIC A — PLATFORMS & PRODUCTS:
- Cashless gaming deployments: IGT, Everi, Aristocrat NRT, Konami, Paysign, Sightline, Acres
- Loyalty/CRM/CDP moves: Xtremepush, Optimove, Light & Wonder, Angel Gaming, Bally's, WDTS
- Middleware or integration layer vendor moves in gaming
- AI applied to gaming loyalty or compliance
- Australia 2028 cashless reform signals

TOPIC B — STRATEGIC ADVISORY:
- AUSTRAC, ClubsNSW, NICC regulatory updates; Mounties Group news
- PAGCOR licensing, AML, KYC, e-wallet rules; Solaire, Okada news
- Star Entertainment, Crown, SkyCity operator news
- FATF, MAS Singapore, DICJ Macau updates
- G2E Asia, ICE, ASEAN Gaming Summit news
"""


def build_research_prompt_part2() -> str:
    today      = date.today()
    week_start = (today - timedelta(days=7)).strftime("%B %d")
    week_end   = today.strftime("%B %d, %Y")

    return f"""
Today is {week_end}. You are a senior intelligence analyst for Syntrii — a digital utility 
platform for the global gaming, entertainment, and hospitality sector.

Search the web and gather the most significant news from {week_start} – {week_end} 
across the following topics. Output raw research notes only — bullet points, no HTML.
Aim for 3 strong stories per topic area. Include source URLs.

TOPIC C — GROWTH & INNOVATION / VENTURES:
- Gaming technology M&A and venture funding — deals, valuations, consolidation
- New IR market progress: Japan, Thailand, UAE, Saudi Arabia, Vietnam, South Korea
- Digital wallets, biometrics, embedded finance applied to gaming
- Fintech or regtech vendors entering gaming compliance or loyalty

TOPIC D — CONTENT VELOCITY:
- From all topics above, identify the 3 stories with the strongest thought leadership 
  potential for Syntrii — where Matt or Laurent could own the narrative publicly.
"""

# ─────────────────────────────────────────────
# STEP 2 — WRITING PROMPTS (no web search)
# These calls take raw intel and produce clean HTML
# ─────────────────────────────────────────────

def build_writing_prompt_part1(research: str) -> str:
    return f"""
You are formatting a weekly intelligence briefing for Syntrii's CCO and CEO.

Below is raw research intel. Convert it into clean HTML for SECTION 1 and SECTION 2.

RULES:
- Exactly 3 stories per section
- Each story: 2 sentences maximum
- Syntrii Angle: 1 sentence, max 15 words
- Output HTML only — no markdown, no preamble, no commentary
- Use <h2> for section titles, <h3> for story headlines

HTML pattern per story:
<h3>[Headline]</h3>
<p>[Max 2 sentences.]</p>
<div class="angle"><strong>Syntrii Angle:</strong> [max 15 words]</div>
<p class="source"><strong>Source:</strong> <a href="URL">Publication</a></p>

Syntrii's key clients: Mounties Group AU, Solaire Philippines, Okada Manila, Angel Gaming, Bally's Corporation.

---

RAW RESEARCH:
{research}

---

Now produce:
<h2>Section 1 — Platforms & Products</h2>
[3 stories from Topic A]

<h2>Section 2 — Strategic Advisory</h2>
[3 stories from Topic B]
"""


def build_writing_prompt_part2(research: str) -> str:
    return f"""
You are formatting a weekly intelligence briefing for Syntrii's CCO and CEO.

Below is raw research intel. Convert it into clean HTML for SECTION 3 and SECTION 4.

RULES:
- Exactly 3 stories in Section 3
- Each story: 2 sentences maximum
- Syntrii Angle: 1 sentence, max 15 words
- Section 4: exactly 3 items, 1 sentence each
- Output HTML only — no markdown, no preamble, no commentary
- Use <h2> for section titles, <h3> for story headlines
- Wrap ALL of Section 4 in <div class="velocity">...</div>

Section 3 HTML pattern per story:
<h3>[Headline]</h3>
<p>[Max 2 sentences.]</p>
<div class="angle"><strong>Syntrii Angle:</strong> [max 15 words]</div>
<p class="source"><strong>Source:</strong> <a href="URL">Publication</a></p>

Section 4 HTML pattern per item (inside <div class="velocity">):
<h3>[Story headline]</h3>
<p>[1 sentence: how Matt or Laurent owns this narrative.]</p>
<p><strong>Format:</strong> [LinkedIn post / IAG article / client briefing note]</p>

Syntrii's key clients: Mounties Group AU, Solaire Philippines, Okada Manila, Angel Gaming, Bally's Corporation.

---

RAW RESEARCH:
{research}

---

Now produce:
<h2>Section 3 — Growth & Innovation / Ventures</h2>
[3 stories from Topic C]

<div class="velocity">
<h2>Section 4 — Content Velocity Signals</h2>
[3 items from Topic D]
</div>
"""

# ─────────────────────────────────────────────
# API HELPERS
# ─────────────────────────────────────────────

def research(prompt: str) -> str:
    """Call with web search enabled — returns raw intel text."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(b.text for b in response.content if b.type == "text")


def write_html(prompt: str) -> str:
    """Call with no tools — pure HTML writing from provided research."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(b.text for b in response.content if b.type == "text")


# ─────────────────────────────────────────────
# FETCH DIGEST — 4 calls with pauses
# ─────────────────────────────────────────────

def fetch_digest() -> str:
    print("  → [1/4] Researching Sections 1 & 2...")
    raw1 = research(build_research_prompt_part1())

    print("  → Pausing 65 seconds (rate limit)...")
    time.sleep(65)

    print("  → [2/4] Writing Sections 1 & 2 HTML...")
    html1 = write_html(build_writing_prompt_part1(raw1))

    print("  → Pausing 65 seconds (rate limit)...")
    time.sleep(65)

    print("  → [3/4] Researching Sections 3 & 4...")
    raw2 = research(build_research_prompt_part2())

    print("  → Pausing 65 seconds (rate limit)...")
    time.sleep(65)

    print("  → [4/4] Writing Sections 3 & 4 HTML...")
    html2 = write_html(build_writing_prompt_part2(raw2))

    return html1 + "\n" + html2

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

        .header    {{ background: #1A3A3F; padding: 20px 24px; margin-bottom: 8px; }}
        .header h1 {{ margin: 0; color: #ffffff; font-size: 22px; font-weight: 600;
                      letter-spacing: 0.5px; }}
        .header h1 span {{ color: #C9A227; }}
        .subhead   {{ background: #429DA6; color: #EAF5F6; padding: 8px 24px;
                      font-size: 13px; margin-bottom: 28px; }}

        h2         {{ color: #1A3A3F; border-bottom: 2px solid #429DA6;
                      padding-bottom: 6px; margin-top: 36px; font-size: 16px;
                      text-transform: uppercase; letter-spacing: 0.5px; }}
        h3         {{ color: #429DA6; margin-bottom: 4px; font-size: 15px; }}
        p          {{ line-height: 1.65; margin: 6px 0; font-size: 14px; }}

        .angle     {{ background: #EAF5F6; border-left: 4px solid #C9A227;
                      padding: 8px 14px; margin: 10px 0 4px 0; font-size: 13px;
                      color: #1A3A3F; }}

        .source    {{ font-size: 12px; color: #888; margin: 2px 0 18px 0; }}
        .source a  {{ color: #429DA6; text-decoration: none; }}

        .velocity  {{ background: #1A3A3F; color: #EAF5F6; padding: 16px 20px;
                      margin-top: 36px; }}
        .velocity h2 {{ color: #C9A227; border-bottom: 1px solid #429DA6;
                        font-size: 15px; }}
        .velocity h3 {{ color: #ffffff; font-size: 14px; }}
        .velocity p  {{ font-size: 13px; color: #EAF5F6; }}

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
#   ~$0.80–1.20 per run (4 API calls)
#   ~$3–5/month total
#   Run time: ~8–10 minutes (includes 3x 65-second pauses)
#   GitHub Actions: free on private repos (2,000 mins/month)
# ─────────────────────────────────────────────────────────
