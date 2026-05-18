#!/usr/bin/env python3
"""
Syntrii Weekly Intelligence Digest
A single aggregated weekly report covering all three Syntrii pillars:
  1. Platforms & Products — competitive and technology intelligence
  2. Strategic Advisory   — regulatory, operator, and policy signals
  3. Growth & Innovation  — M&A, ventures, new markets, emerging tech

Delivered every Monday morning (AEST) via email.

Architecture (Tier 2 API):
  Call 1 — Research Sections 1 & 2 (web search, raw intel)
  Call 2 — Write Sections 1 & 2 HTML (no web search)
  Call 3 — Research Sections 3 & 4 (web search, raw intel)
  Call 4 — Write Sections 3 & 4 HTML (no web search)

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
# RESEARCH PROMPTS — web search, raw intel output
# ─────────────────────────────────────────────

def build_research_prompt_part1() -> str:
    today      = date.today()
    week_start = (today - timedelta(days=7)).strftime("%B %d")
    week_end   = today.strftime("%B %d, %Y")

    return f"""
Today is {week_end}. You are a senior intelligence analyst for Syntrii — a digital utility 
platform purpose-built for the global gaming, entertainment, and hospitality sector.
Syntrii's key clients and pipeline: Mounties Group AU, Solaire Philippines, Okada Manila, 
Angel Gaming, Bally's Corporation.

Search the web and gather the most significant news from {week_start} – {week_end} 
across the following topics. Output raw research notes — bullet points, no HTML.
Find 5 strong stories per topic area. Include source name and URL for each story.

TOPIC A — PLATFORMS & PRODUCTS:
- Cashless gaming technology deployments globally: IGT, Everi, Aristocrat NRT, Konami 
  Money Klip, Paysign, Sightline, Acres Manufacturing — who is going live, where, with what
- Loyalty, CRM, and CDP platform moves: Xtremepush, Optimove, Light & Wonder, Fast Track,
  Salesforce Gaming — new features, partnerships, operator wins/losses
- Vendor landscape: Angel Gaming, Walker Digital Table Systems (WDTS), Bally's Corporation,
  LGT — any product launches, operator wins, partnership announcements
- Middleware and integration layer: any vendor positioning as the connective tissue between
  GMS, loyalty, payments, and compliance systems
- AI applied to gaming loyalty personalisation, player development, or compliance
- Australia 2028 cashless reform: regulator guidance, vendor certification, club procurement

TOPIC B — STRATEGIC ADVISORY:
- AUSTRAC regulatory updates, enforcement actions, AML/CTF reform implementation
- Mounties Group — any news related to AUSTRAC proceedings or compliance
- ClubsNSW, NICC, state gaming regulators — policy announcements
- PAGCOR — licensing, AML enforcement, KYC rules, e-wallet decisions, advertising bans
- Solaire Resort, Okada Manila — strategy, results, technology investments, compliance moves
- Star Entertainment, Crown, SkyCity — governance, results, regulatory news
- FATF AML/CTF updates, MAS Singapore, DICJ Macau — any new IR frameworks
- G2E Asia, ICE, ASEAN Gaming Summit — conference news and announcements
"""


def build_research_prompt_part2() -> str:
    today      = date.today()
    week_start = (today - timedelta(days=7)).strftime("%B %d")
    week_end   = today.strftime("%B %d, %Y")

    return f"""
Today is {week_end}. You are a senior intelligence analyst for Syntrii — a digital utility 
platform purpose-built for the global gaming, entertainment, and hospitality sector.
Syntrii's key clients and pipeline: Mounties Group AU, Solaire Philippines, Okada Manila, 
Angel Gaming, Bally's Corporation.

Search the web and gather the most significant news from {week_start} – {week_end} 
across the following topics. Output raw research notes — bullet points, no HTML.
Find 5 strong stories per topic area. Include source name and URL for each story.

TOPIC C — GROWTH & INNOVATION / VENTURES:
- Gaming technology M&A and venture funding — who is raising, who is being acquired,
  at what multiples, and what it signals about sector consolidation
- New IR market openings: Japan, Thailand, UAE, Saudi Arabia, Vietnam, South Korea —
  regulatory milestones, operator announcements, licensing progress
- Emerging technology: digital wallets, biometric identity, embedded finance, open banking
  applied to gaming environments
- Adjacent sector entrants: fintech, regtech, or identity verification vendors moving into
  gaming compliance or loyalty
- Innovation from retail loyalty, sports betting, or financial services applicable to gaming
- Potential partnership or acquisition targets relevant to Syntrii's platform

TOPIC D — CONTENT VELOCITY:
- From all research above, identify the 5 stories with the strongest thought leadership
  potential for Syntrii — where Matt or Laurent could own the narrative publicly via
  LinkedIn, Inside Asian Gaming, or a client briefing note.
- For each, note: why it matters to Syntrii's positioning and suggested content format.
"""

# ─────────────────────────────────────────────
# WRITING PROMPTS — no web search, pure HTML
# ─────────────────────────────────────────────

def build_writing_prompt_part1(raw_research: str) -> str:
    return f"""
You are producing a weekly intelligence email for Syntrii's CCO and CEO.

Using ONLY the research notes below, write clean HTML for SECTION 1 and SECTION 2.
Do not search for additional information. Do not add commentary or preamble.
Output HTML only — no markdown, no code fences.

FORMAT PER STORY:
<h3>[Headline]</h3>
<p>[2–3 concise sentences covering what happened, who is involved, and why it matters.]</p>
<div class="angle"><strong>Syntrii Angle:</strong> [2–3 sentences on commercial or strategic 
relevance to Syntrii's pipeline: Mounties Group AU, Solaire Philippines, Okada Manila, 
Angel Gaming, Bally's Corporation, or Syntrii's platform positioning.]</div>
<p class="source"><strong>Source:</strong> <a href="URL">Publication Name</a></p>

Use <h2> for section titles. Write 4–5 stories per section. Pick the most significant.

---

RAW RESEARCH NOTES:
{raw_research}

---

Now produce the following two sections in full:

<h2>Section 1 — Platforms &amp; Products</h2>
[4–5 stories from Topic A]

<h2>Section 2 — Strategic Advisory</h2>
[4–5 stories from Topic B]
"""


def build_writing_prompt_part2(raw_research: str) -> str:
    return f"""
You are producing a weekly intelligence email for Syntrii's CCO and CEO.

Using ONLY the research notes below, write clean HTML for SECTION 3 and SECTION 4.
Do not search for additional information. Do not add commentary or preamble.
Output HTML only — no markdown, no code fences.

SECTION 3 FORMAT PER STORY:
<h3>[Headline]</h3>
<p>[2–3 concise sentences covering what happened, who is involved, and why it matters.]</p>
<div class="angle"><strong>Syntrii Angle:</strong> [2–3 sentences on commercial or strategic 
relevance to Syntrii's pipeline: Mounties Group AU, Solaire Philippines, Okada Manila, 
Angel Gaming, Bally's Corporation, or Syntrii's platform positioning.]</div>
<p class="source"><strong>Source:</strong> <a href="URL">Publication Name</a></p>

SECTION 4 FORMAT — wrap the entire section in <div class="velocity">:
<h3>[Story headline]</h3>
<p>[2 sentences: the Syntrii content angle — how Matt or Laurent owns this narrative 
from a platform or advisory perspective.]</p>
<p><strong>Format:</strong> [LinkedIn post / IAG article / client briefing note]</p>

Use <h2> for section titles. Write 4–5 stories in Section 3. Write 3 items in Section 4.

---

RAW RESEARCH NOTES:
{raw_research}

---

Now produce the following two sections in full:

<h2>Section 3 — Growth &amp; Innovation / Ventures</h2>
[4–5 stories from Topic C]

<div class="velocity">
<h2>Section 4 — Content Velocity Signals</h2>
[3 items from Topic D]
</div>
"""

# ─────────────────────────────────────────────
# API HELPERS — with rate limit retry
# ─────────────────────────────────────────────

def api_call_with_retry(create_fn, max_retries: int = 5) -> str:
    """Call the Anthropic API, retrying with backoff on rate limit errors."""
    wait = 30
    for attempt in range(max_retries):
        try:
            response = create_fn()
            return "".join(b.text for b in response.content if b.type == "text")
        except anthropic.RateLimitError:
            if attempt < max_retries - 1:
                print(f"  → Rate limit hit. Waiting {wait}s before retry {attempt + 2}/{max_retries}...")
                time.sleep(wait)
                wait += 30
            else:
                raise


def research(prompt: str) -> str:
    """Web search call — gathers raw intel."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    return api_call_with_retry(lambda: client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": prompt}],
    ))


def write_html(prompt: str) -> str:
    """Writing call — no web search, pure HTML from research notes."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    return api_call_with_retry(lambda: client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8000,
        messages=[{"role": "user", "content": prompt}],
    ))

# ─────────────────────────────────────────────
# FETCH DIGEST — 4 calls
# ─────────────────────────────────────────────

def fetch_digest() -> str:
    print("  → [1/4] Researching Sections 1 & 2 (Platforms, Advisory)...")
    raw1 = research(build_research_prompt_part1())

    print("  → [2/4] Writing Sections 1 & 2 HTML...")
    html1 = write_html(build_writing_prompt_part1(raw1))

    print("  → [3/4] Researching Sections 3 & 4 (Growth, Content Velocity)...")
    raw2 = research(build_research_prompt_part2())

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
# REQUIRES: Anthropic API Tier 2 ($40 total spend)
#   → console.anthropic.com/settings/billing
#   Tier 2 gives 1M input tokens/min and 16K output tokens/min on Sonnet —
#   sufficient for all 4 API calls without rate limit issues.
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
#   ~$1.50–2.00 per run (4 API calls, 8k tokens each)
#   ~$6–8/month total
#   Run time: ~3–5 minutes
#   GitHub Actions: free on private repos (2,000 mins/month)
# ─────────────────────────────────────────────────────────
