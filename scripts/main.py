"""Job Radar — reads job-alert emails, scores each job against the CV, publishes matches.

Sources (all arrive as alert emails in a dedicated Gmail inbox):
  - AcademicTransfer / EURAXESS alerts  -> PhD tab
  - LinkedIn job alerts                 -> LinkedIn tab
  - Indeed job alerts                   -> Indeed tab

Usage:
  python scripts/main.py                 normal run
  python scripts/main.py --dry-run       no Telegram, no saving
  python scripts/main.py --test-telegram send one test message and exit
"""
import hashlib
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import llm  # noqa: E402
import mail  # noqa: E402
import notify  # noqa: E402
from textutil import html_to_text  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
JOBS_FILE = ROOT / "docs" / "data" / "jobs.json"
STATE_FILE = ROOT / "data" / "state.json"
CONFIG = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))

URL_RE = re.compile(r"<(https?://[^>\s]+)>|(https?://[^\s<>\"')\]]+)")

ID_PATTERNS = {
    "linkedin": re.compile(r"linkedin\.com/(?:comm/)?jobs/view/(?:[^/?]*-)?(\d{6,})"),
    "indeed": re.compile(r"[?&]jk=([0-9a-f]{16})"),
    "academictransfer": re.compile(r"academictransfer\.com/(?:en/|nl/)?(?:jobs|vacatures)/(\d+)"),
    "euraxess": re.compile(r"euraxess\.ec\.europa\.eu/jobs/(\d+)"),
}


# ---------------------------------------------------------------- helpers
def now_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_json(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")


def detect_source(msg):
    blob = (msg["from"] + " " + msg["subject"] + " " + msg["body"][:20000]).lower()
    if "linkedin.com" in blob and "jobs" in blob:
        return "linkedin"
    if "indeed." in blob:
        return "indeed"
    if "academictransfer" in blob:
        return "academictransfer"
    if "euraxess" in blob:
        return "euraxess"
    return None


def shorten_links(body):
    """Replace long URLs with [L1], [L2]… so the model reads less and can't mangle them."""
    links = {}

    def repl(m):
        url = urllib.parse.unquote(m.group(1) or m.group(2))
        ref = f"L{len(links) + 1}"
        links[ref] = url
        return f"[{ref}]"

    return URL_RE.sub(repl, body), links


def canonical(url, source):
    url = urllib.parse.unquote(url or "")
    for name, pat in ID_PATTERNS.items():
        m = pat.search(url)
        if not m:
            continue
        jid = m.group(1)
        if name == "linkedin":
            return f"linkedin:{jid}", f"https://www.linkedin.com/jobs/view/{jid}/"
        if name == "indeed":
            return f"indeed:{jid}", f"https://nl.indeed.com/viewjob?jk={jid}"
        if name == "euraxess":
            return f"euraxess:{jid}", f"https://euraxess.ec.europa.eu/jobs/{jid}"
        if name == "academictransfer":
            clean = url.split("?")[0]
            return f"academictransfer:{jid}", clean
    return None, url


def fallback_key(source, title, org):
    raw = f"{source}|{(title or '').lower().strip()}|{(org or '').lower().strip()}"
    return f"{source}:t{hashlib.sha1(raw.encode()).hexdigest()[:12]}"


def fetch_page_text(url, limit=12000):
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (personal job-alert reader; one request per vacancy)",
            "Accept-Language": "en,nl;q=0.8",
        })
        with urllib.request.urlopen(req, timeout=25) as resp:
            raw = resp.read(2_000_000).decode("utf-8", "replace")
        return html_to_text(raw)[:limit]
    except Exception as e:
        print(f"  could not fetch {url}: {e}")
        return ""


# ---------------------------------------------------------------- AI steps
EXTRACT_SYSTEM = """You read job-alert emails and list every individual job/vacancy in them.
Return ONLY JSON: {"jobs":[{"title":"","organization":"","location":"","snippet":"","link_ref":"L3"}]}
- link_ref is the [Lx] marker of the link that opens that specific job (not unsubscribe/settings/search links).
- snippet: any description text shown for that job in the email (may be empty).
- Ignore ads, "jobs you may like" headers, footers and navigation. If there are no jobs, return {"jobs":[]}."""

SCORE_SYSTEM_TMPL = """You are a careful career advisor. Compare one job/PhD vacancy with the candidate profile.
Return ONLY JSON:
{{"score":0-100,"is_phd":true/false,"dutch":"required|plus|english|unknown","deadline":"YYYY-MM-DD or null","reason":"..."}}

score = how well the candidate fits AND would realistically be a strong applicant (skills, experience, field, level).
  85-100 excellent fit · 70-84 good fit · 50-69 partial · below 50 weak. Be honest, not generous.
  If only a title is available, judge from the title and be a bit conservative.
is_phd = true only for PhD / doctoral candidate / promovendus positions.
dutch = "required" if Dutch is required/expected (also when the vacancy text itself is written in Dutch and
  does not say English is fine), "plus" if Dutch is an advantage, "english" if clearly English-only, else "unknown".
  The candidate's Dutch level: {dutch_level}.
reason = 1–2 short sentences in {lang}: why it fits or not, naming the concrete overlap or gap."""


def extract_jobs(msg, source):
    text, links = shorten_links(msg["body"])
    user = f"SOURCE: {source}\nSUBJECT: {msg['subject']}\n\nEMAIL:\n{text[:18000]}"
    data = llm.ask_json(CONFIG["model_extract"], EXTRACT_SYSTEM, user, max_tokens=3000)
    jobs = []
    for j in data.get("jobs", []):
        if not j.get("title"):
            continue
        j["url_raw"] = links.get((j.get("link_ref") or "").strip("[]"), "")
        jobs.append(j)
    return jobs


def score_job(profile, job, details):
    system = SCORE_SYSTEM_TMPL.format(dutch_level=CONFIG["dutch_level"], lang=CONFIG["reason_language"])
    user = (
        f"CANDIDATE PROFILE:\n{profile}\n\n"
        f"VACANCY:\nTitle: {job.get('title')}\nOrganization: {job.get('organization')}\n"
        f"Location: {job.get('location')}\nSource: {job.get('source')}\n"
        f"Text:\n{details or job.get('snippet') or '(only the title is known)'}"
    )
    return llm.ask_json(CONFIG["model_score"], system, user, max_tokens=600)


# ---------------------------------------------------------------- main
def run(dry_run=False):
    profile = os.environ.get("CV_PROFILE", "").strip()
    if not profile and (ROOT / "profile.txt").exists():
        profile = (ROOT / "profile.txt").read_text(encoding="utf-8")
    if not profile:
        sys.exit("No CV profile found (set the CV_PROFILE secret).")

    user, pw = os.environ.get("GMAIL_ADDRESS", ""), os.environ.get("GMAIL_APP_PASSWORD", "")
    if not user or not pw:
        sys.exit("GMAIL_ADDRESS / GMAIL_APP_PASSWORD are not set.")

    state = load_json(STATE_FILE, {"emails": {}, "jobs": {}})
    store = load_json(JOBS_FILE, {"updated": None, "jobs": []})
    known_published = {j["key"] for j in store["jobs"]}

    messages = mail.fetch_recent(user, pw, days=CONFIG["lookback_days"])
    print(f"{len(messages)} emails in the last {CONFIG['lookback_days']} days")

    new_published = []
    for msg in messages:
        if state["emails"].get(msg["key"]) == "done":
            continue
        source = detect_source(msg)
        if not source:
            state["emails"][msg["key"]] = "done"
            continue
        print(f"- [{source}] {msg['subject'][:80]}")
        try:
            jobs = extract_jobs(msg, source)
        except Exception as e:
            print(f"  extract failed: {e}")
            tries = state["emails"].get(msg["key"], 0)
            state["emails"][msg["key"]] = "done" if isinstance(tries, int) and tries >= 2 else (tries + 1 if isinstance(tries, int) else 1)
            continue

        for job in jobs:
            key, url = canonical(job.get("url_raw"), source)
            key = key or fallback_key(source, job.get("title"), job.get("organization"))
            if key in state["jobs"] or key in known_published:
                continue
            job["source"] = source
            details = ""
            if source in ("academictransfer", "euraxess") and CONFIG.get("academic_page_fetch") and url:
                details = fetch_page_text(url)
            try:
                s = score_job(profile, job, details)
            except Exception as e:
                print(f"  score failed for {job.get('title')}: {e}")
                continue
            score = int(s.get("score", 0))
            state["jobs"][key] = score
            is_phd = bool(s.get("is_phd"))

            if source in ("academictransfer", "euraxess"):
                if not is_phd:
                    continue
                section, threshold = "phd", CONFIG["phd_threshold"]
            else:
                section, threshold = source, CONFIG["threshold"]
            print(f"  {score:>3}  {section:<8} {job.get('title')[:70]}")
            if score < threshold:
                continue

            item = {
                "key": key,
                "section": section,
                "title": job.get("title", "").strip(),
                "organization": (job.get("organization") or "").strip(),
                "location": (job.get("location") or "").strip(),
                "url": url,
                "score": score,
                "dutch": s.get("dutch") if s.get("dutch") in notify.DUTCH_LABEL else "unknown",
                "deadline": s.get("deadline") if s.get("deadline") not in (None, "null", "") else None,
                "reason": (s.get("reason") or "").strip(),
                "info": "full" if details or job.get("snippet") else "title-only",
                "found": now_iso(),
            }
            new_published.append(item)
            known_published.add(key)

        state["emails"][msg["key"]] = "done"

    # notify
    for item in new_published:
        if item["dutch"] == "required" and not CONFIG.get("notify_dutch_required", True):
            continue
        if dry_run:
            print("\n--- would send ---\n" + notify.format_job(item))
        else:
            notify.send(notify.format_job(item))

    # save
    store["jobs"] = (new_published + store["jobs"])[: CONFIG["max_jobs_kept"]]
    store["updated"] = now_iso()
    # keep state small: forget emails/jobs beyond the most recent entries
    state["emails"] = dict(list(state["emails"].items())[-3000:])
    state["jobs"] = dict(list(state["jobs"].items())[-8000:])
    if not dry_run:
        save_json(JOBS_FILE, store)
        save_json(STATE_FILE, state)
    print(f"done: {len(new_published)} new matches")


if __name__ == "__main__":
    if "--test-telegram" in sys.argv:
        ok = notify.send("✅ Job Radar وصل شد! از این به بعد شغل‌ها و دکتراهای مناسب اینجا میان.")
        sys.exit(0 if ok else 1)
    run(dry_run="--dry-run" in sys.argv)
