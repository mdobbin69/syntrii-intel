#!/usr/bin/env python3
"""Syntrii Weekly Intelligence Digest — v3 clean"""

import anthropic, smtplib, os, time
from datetime import date, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

RECIPIENT_EMAILS  = ["matt@syntrii.com", "laurent@syntrii.com"]
SENDER_EMAIL      = os.environ.get("DIGEST_SENDER_EMAIL")
SENDER_PASSWORD   = os.environ.get("DIGEST_SENDER_PASSWORD")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
SMTP_HOST, SMTP_PORT = "smtp.gmail.com", 587

# ── Dates ────────────────────────────────────────────────

def dates():
    today = date.today()
    return (today - timedelta(days=7)).strftime("%B %d"), today.strftime("%B %d, %Y")

# ── Prompts ──────────────────────────────────────────────

def prompt_research_1():
    s, e = dates()
    return f"""Today is {e}. You are a senior intelligence analyst for Syntrii.
Search the web for significant gaming industry news from {s}–{e}.
Max 6 searches. Output bullet notes only — no HTML. Include source name and URL per item.

Searches 1-3 → PLATFORMS & PRODUCTS: cashless gaming (IGT, Everi, Aristocrat, Konami),
loyalty/CRM/CDP (Xtremepush, Optimove, Light & Wonder), middleware/integration vendors,
AI in gaming loyalty or compliance, Australia 2028 cashless reform.

Searches 4-6 → STRATEGIC ADVISORY: AUSTRAC/Mounties Group, ClubsNSW/NICC updates,
PAGCOR/Solaire/Okada, Star Entertainment/Crown/SkyCity, FATF/MAS Singapore/DICJ Macau."""

def prompt_research_2():
    s, e = dates()
    return f"""Today is {e}. You are a senior intelligence analyst for Syntrii.
Search the web for significant gaming industry news from {s}–{e}.
Max 6 searches. Output bullet notes only — no HTML. Include source name and URL per item.

Searches 1-3 → GROWTH & INNOVATION: gaming tech M&A and venture funding, new IR markets
(Japan, Thailand, UAE, Saudi Arabia, Vietnam), digital wallets and biometrics in gaming,
fintech/regtech vendors entering gaming compliance or loyalty.

Searches 4-6 → CONTENT VELOCITY: identify 3 strongest stories for Syntrii thought
leadership (LinkedIn / Inside Asian Gaming / client briefing). Note why and suggested format."""

def prompt_write_1(raw):
    return f"""You are writing a weekly intelligence email for Syntrii's CCO and CEO.
Clients: Mounties Group AU, Solaire Philippines, Okada Manila, Angel Gaming, Bally's.

Using ONLY the notes below, output clean HTML for Section 1 and Section 2. No markdown, no preamble.

Per story:
<h3>Headline</h3>
<p>2-3 sentences on what happened and why it matters.</p>
<div class="angle"><strong>Syntrii Angle:</strong> 2-3 sentences on relevance to Syntrii.</div>
<p class="source"><strong>Source:</strong> <a href="URL">Publication</a></p>

4 stories per section. Use <h2> for section titles.
Section 1 title MUST be "Platforms & Products".
Section 2 title MUST be "Strategic Advisory".

RESEARCH NOTES:
{raw}"""

def prompt_write_2(raw):
    return f"""You are writing a weekly intelligence email for Syntrii's CCO and CEO.
Clients: Mounties Group AU, Solaire Philippines, Okada Manila, Angel Gaming, Bally's.

Using ONLY the notes below, output clean HTML for Section 3 and Section 4. No markdown, no preamble.

Section 3 — title MUST be "Growth & Innovation / Ventures". 3 stories. EVERY story MUST follow this exact pattern:
<h3>Headline</h3>
<p>2-3 sentences on what happened and why it matters.</p>
<div class="angle"><strong>Syntrii Angle:</strong> 2-3 sentences on relevance to Syntrii's clients or platform.</div>
<p class="source"><strong>Source:</strong> <a href="URL">Publication</a></p>
Section 4 — title MUST be "Content Velocity Signals". Wrap entire section in <div class="velocity">, 3 items each with:
<h3>Story headline</h3>
<p>How Matt or Laurent owns this narrative publicly.</p>
<p><strong>Format:</strong> LinkedIn post / IAG article / client briefing note</p>

Use <h2> for section titles.

RESEARCH NOTES:
{raw}"""

# ── API calls ────────────────────────────────────────────

def call_api(create_fn, retries=5):
    wait = 30
    for attempt in range(retries):
        try:
            r = create_fn()
            return "".join(b.text for b in r.content if b.type == "text")
        except anthropic.RateLimitError:
            if attempt < retries - 1:
                print(f"  Rate limit — waiting {wait}s...")
                time.sleep(wait)
                wait += 30
            else:
                raise

def search(prompt):
    c = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    return call_api(lambda: c.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=4000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": prompt}],
    ))

def write(prompt):
    c = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    return call_api(lambda: c.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=6000,
        messages=[{"role": "user", "content": prompt}],
    ))

# ── Digest ───────────────────────────────────────────────

def fetch_digest():
    print("  [1/4] Researching Sections 1 & 2...")
    r1 = search(prompt_research_1())
    print("  [2/4] Writing Sections 1 & 2...")
    h1 = write(prompt_write_1(r1))
    print("  [3/4] Researching Sections 3 & 4...")
    r2 = search(prompt_research_2())
    print("  [4/4] Writing Sections 3 & 4...")
    h2 = write(prompt_write_2(r2))
    return h1 + "\n" + h2

# ── Email ────────────────────────────────────────────────

def build_email(body):
    s, e = dates()
    today = date.today()
    ws = (today - timedelta(days=7)).strftime("%d %b")
    we = today.strftime("%d %b %Y")
    return f"""<html><head><style>
body{{font-family:'Segoe UI',Arial,sans-serif;color:#111;max-width:820px;margin:0 auto;padding:24px}}
.hdr{{background:#1A3A3F;padding:20px 24px;margin-bottom:8px}}
.hdr h1{{margin:0;color:#fff;font-size:22px;font-weight:600}}
.hdr h1 span{{color:#C9A227}}
.sub{{background:#429DA6;color:#EAF5F6;padding:8px 24px;font-size:13px;margin-bottom:28px}}
h2{{color:#1A3A3F;border-bottom:2px solid #429DA6;padding-bottom:6px;margin-top:36px;font-size:16px;text-transform:uppercase}}
h3{{color:#429DA6;margin-bottom:4px;font-size:15px}}
p{{line-height:1.65;margin:6px 0;font-size:14px}}
.angle{{background:#EAF5F6;border-left:4px solid #C9A227;padding:8px 14px;margin:10px 0 4px;font-size:13px;color:#1A3A3F}}
.source{{font-size:12px;color:#888;margin:2px 0 18px}}
.source a{{color:#429DA6;text-decoration:none}}
.velocity{{background:#1A3A3F;color:#EAF5F6;padding:16px 20px;margin-top:36px}}
.velocity h2{{color:#C9A227;border-bottom:1px solid #429DA6;font-size:15px}}
.velocity h3{{color:#fff;font-size:14px}}
.velocity p{{font-size:13px;color:#EAF5F6}}
.ftr{{margin-top:40px;padding-top:16px;border-top:1px solid #ddd;font-size:11px;color:#aaa}}
</style></head><body>
<div class="hdr"><h1>Syntrii <span>Weekly Intelligence</span></h1></div>
<div class="sub">Week of {ws} – {we} &nbsp;·&nbsp; Platforms &amp; Products &nbsp;·&nbsp; Strategic Advisory &nbsp;·&nbsp; Growth &amp; Innovation</div>
{body}
<div class="ftr">Produced by Syntrii Intelligence &nbsp;·&nbsp; hello@syntrii.com &nbsp;·&nbsp; syntrii.com<br><em>One Digital Utility. Infinite Applications.</em></div>
</body></html>"""

def send_email(html):
    today = date.today()
    ws = (today - timedelta(days=7)).strftime("%d %b")
    we = today.strftime("%d %b %Y")
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Syntrii Weekly Intelligence — {ws}–{we}"
    msg["From"]    = SENDER_EMAIL
    msg["To"]      = ", ".join(RECIPIENT_EMAILS)
    msg.attach(MIMEText(html, "html"))
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
        s.starttls()
        s.login(SENDER_EMAIL, SENDER_PASSWORD)
        s.sendmail(SENDER_EMAIL, RECIPIENT_EMAILS, msg.as_string())
    print(f"✅ Sent to {', '.join(RECIPIENT_EMAILS)}")

# ── Main ─────────────────────────────────────────────────

def main():
    print("🔍 Fetching weekly intelligence...")
    digest = fetch_digest()
    print("📧 Sending email...")
    send_email(build_email(digest))

if __name__ == "__main__":
    main()
