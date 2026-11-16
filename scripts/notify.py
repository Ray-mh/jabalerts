"""Telegram notifications."""
import html
import json
import os
import urllib.request

SOURCE_LABEL = {"phd": "🎓 PhD", "linkedin": "🔵 LinkedIn", "indeed": "🟣 Indeed"}
DUTCH_LABEL = {
    "required": "🔴 هلندی الزامی",
    "plus": "🟡 هلندی امتیاز است",
    "english": "🟢 فقط انگلیسی",
    "unknown": "⚪ زبان نامشخص",
}


def format_job(job):
    e = html.escape
    lines = [
        f"{SOURCE_LABEL.get(job['section'], job['section'])}  ·  <b>{job['score']}٪ تطابق</b>",
        f"<b>{e(job['title'])}</b>",
    ]
    where = " — ".join(x for x in [job.get("organization"), job.get("location")] if x)
    if where:
        lines.append(e(where))
    lines.append(DUTCH_LABEL.get(job.get("dutch", "unknown"), "⚪"))
    if job.get("deadline"):
        lines.append(f"⏳ مهلت: {e(job['deadline'])}")
    if job.get("reason"):
        lines.append("")
        lines.append(e(job["reason"]))
    if job.get("url"):
        lines.append("")
        lines.append(f'<a href="{e(job["url"], quote=True)}">مشاهده‌ی آگهی ←</a>')
    return "\n".join(lines)


def send(text):
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    if not token or not chat_id:
        print("Telegram not configured; skipping notification.")
        return False
    body = json.dumps({
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }).encode("utf-8")
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=body, method="POST", headers={"content-type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"Telegram error: {e}")
        return False
