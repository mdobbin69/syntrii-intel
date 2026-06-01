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
# RESEARCH PROMPT
# ─────────────────────────────────────────────

def build_prompt() -> str:
    today      = date.today()
    week_start = (today - timedelta(days=7)).strftime("%B %d")
    week_end   = today.strftime("%B %d, %Y")

    return f"""
Today is {week_end}. You are a senior intelligence analyst for Syntrii — a digital utility 
platform purpose-built for the global gaming, entertainment, and hospitality sector. 
Syntrii operates across three pillars: Platforms & Products, Strategic Advisory, and 
Growth & Innovation.

Search the web and produce a structured WEEKLY intelligence briefing covering the past 
7 days ({week_start} – {week_end}). 

The report has four sections. Cover the most significant 5–6 stories per section. 
For each story write 2–3 concise sentences, a Source URL, and a "Syntrii Angle" — 
one line on commercial or strategic relevance to Syntrii's pipeline 
(Mounties Group AU, Solaire Philippines, Angel Gaming, Okada, Bally's Corporation) 
or platform positioning.

---

## SECTION 1 — PLATFORMS & PRODUCTS
*Competitive and technology intelligence to keep Syntrii's platform relevant and defensible.*

Search for and cover:
- Cashless gaming technology deployments globally — who is going live, with what vendor, 
  in which jurisdiction
- Loyalty, CRM, and CDP platform moves: new features, partnerships, client wins/losses.
  Focus vendors: Konami (SYNKROS/SynkVision), IGT, Everi, Scientific Games, NRT, 
  Aristocrat, Paysign, Sightline, Actenum, Optimove, Salesforce Gaming
- Global gaming technology vendor landscape — track moves from all of the following:
    · Angel Gaming — smart table technology, middleware, connector layer deployments,
      any new operator wins, product launches, or partnership announcements
    · Walker Digital Table Systems (WDTS) — table game technology, any licensing deals,
      new deployments, acquisition interest, or patent activity
    · Light & Wonder (formerly Scientific Games) — systems division, OpenGaming platform,
      loyalty and cashless moves, any operator wins or losses
    · Konami Gaming — SYNKROS, SynkVision, SYNK31, Money Klip; new installs, 
      product announcements, or operator contract news
    · Aristocrat Technologies — NRT cashless, loyalty platform, systems acquisitions,
      any moves into the digital utility or middleware space
    · Everi Holdings — digital, fintech, loyalty and cashless wallet moves, 
      any M&A or partnership activity
    · IGT (International Game Technology) — resort wallet, loyalty, systems news,
      any operator wins or product developments
    · Bally's Corporation — technology platform, digital integration, loyalty stack,
      any systems vendor relationships, procurement news, or tech transformation updates
    · LGT (Lightning Gaming Technologies) — any product launches, partnership news,
      or operator deployments
    · Any emerging or challenger vendors positioning in the connector/middleware layer —
      this is Syntrii's core territory; flag any vendor claiming to be the "integration 
      layer" or "digital utility" between gaming systems
- Middleware, connector, and integration layer announcements — who is positioning as the 
  connective tissue between GMS, loyalty, payments, and compliance systems
- Blockchain, digital identity, and wallet technology in regulated gaming environments
- AI and machine learning applications in loyalty personalisation, player development, 
  or gaming compliance
- Australia 2028 reform implementation signals — regulator guidance, vendor certification 
  news, club procurement decisions

---

## SECTION 2 — STRATEGIC ADVISORY
*Regulatory, operator, and policy intelligence to keep Syntrii credible and ahead of clients.*

Search for and cover:
- Regulatory announcements and consultations:
  Australia: AUSTRAC, NICC (NSW Independent Casino Commission), ClubsNSW, AGCO, 
  state gaming regulators, Responsible Gambling reforms
  Philippines: PAGCOR — new regulations, licensing, AML enforcement
  Asia-Pacific: MAS Singapore, DICJ Macau, any new IR regulatory frameworks
  Global: FATF AML/CTF updates, KYC/CDD obligations, responsible gambling technology mandates
- Operator news — strategy, results, leadership, technology investments:
  Australia: Mounties Group, Crown, Star, SkyCity, ALH Group
  Southeast Asia: Solaire, Okada, Marina Bay Sands, Resorts World Sentosa, Melco
  Global: MGM, Wynn, Las Vegas Sands, Hard Rock, Bally's Corporation
- Industry editorial and thought leadership worth noting:
  Inside Asian Gaming, GamblingInsider, CalvinAyre, Club Management Australia
- Conference and event intelligence: G2E, ICE, ASEAN Gaming Summit, ClubsNSW Annual

---

## SECTION 3 — GROWTH & INNOVATION / VENTURES
*Deal flow, emerging technology, and market entry signals.*

Search for and cover:
- Gaming technology M&A and venture funding — who is raising, who is being acquired, 
  at what multiples, and what it signals about sector consolidation
- New market openings and IR licensing progress: Japan, Thailand, UAE, Saudi Arabia, 
  Vietnam, South Korea — any regulatory milestones or operator announcements
- Emerging technology moves relevant to Syntrii's roadmap: digital wallets, biometric 
  identity, embedded finance, open banking applied to gaming
- Adjacent sector entrants: fintech, regtech, or identity verification vendors making 
  moves into the gaming compliance or loyalty space
- Innovation from non-gaming sectors with direct applicability: what is retail loyalty, 
  sports betting, or financial services doing that gaming hasn't adopted yet?
- Potential partnership or acquisition targets that could strengthen Syntrii's platform 
  or accelerate market entry

---

## SECTION 4 — CONTENT VELOCITY SIGNALS
*Each of the top 3 stories from above that represent the strongest opportunity for 
Syntrii thought leadership — a LinkedIn post, IAG article pitch, or client briefing hook.*

For each, provide:
- The story headline
- A suggested Syntrii content angle (1–2 sentences on how Matt or Laurent could own 
  the narrative from a platform or advisory perspective)
- Suggested format: LinkedIn post / IAG article / client briefing note

---

FORMAT INSTRUCTIONS (CRITICAL — follow exactly):
- Your ENTIRE response must be raw HTML. Start your response with an HTML tag (e.g. <h2>).
- Do NOT wrap output in markdown code fences. Do NOT write ```html or ``` anywhere.
- Do NOT include any preamble, commentary, or text before or after the HTML.
- Use <h2> for section headers, <h3> for story headlines
- Wrap each story's Syntrii Angle in: <div class="angle"><strong>Syntrii Angle:</strong> ...</div>
- Wrap each Source in: <p class="source"><strong>Source:</strong> <a href="URL">Publication Name</a></p>
- Keep the total report to the top 22–25 most significant stories across all sections
- Be concise and commercial — this is for a CCO and CEO, not an academic

RECENCY INSTRUCTIONS (CRITICAL):
- Every story MUST be from the past 7 days ({week_start} – {week_end}). 
- Do NOT include any story published before {week_start}.
- If a topic has no new developments this week, skip it — do not recycle older stories.
- Prioritise stories you have not covered in prior weekly digests. If a story has been 
  running for more than one week (e.g. an ongoing enforcement action), only include it 
  if there is a materially NEW development this week (new filing, new statement, new data).
- Search specifically for news from the past 7 days using date-filtered queries where possible.
"""

# ─────────────────────────────────────────────
# FETCH DIGEST FROM CLAUDE
# ─────────────────────────────────────────────

def fetch_digest() -> str:
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": build_prompt()}],
    )

    html_content = ""
    for block in response.content:
        if block.type == "text":
            html_content += block.text

    # Strip markdown code fences if Claude wraps output despite instructions
    import re
    html_content = re.sub(r"^```(?:html)?\s*", "", html_content.strip(), flags=re.IGNORECASE)
    html_content = re.sub(r"\s*```$", "", html_content.strip())

    return html_content

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
#   ~$0.25–0.50 per run (more searches, larger output)
#   ~$1–2/month total
#   GitHub Actions: free on private repos (2,000 mins/month)
# ─────────────────────────────────────────────────────────
