"""Read recent job-alert emails from Gmail over IMAP (app password)."""
import email
import hashlib
import imaplib
from datetime import datetime, timedelta, timezone
from email.header import decode_header, make_header

from textutil import html_to_text, tidy


def _decode(value):
    try:
        return str(make_header(decode_header(value or "")))
    except Exception:
        return value or ""


def _body(msg):
    html_part, text_part = None, None
    for part in msg.walk():
        if part.get_content_maintype() == "multipart":
            continue
        if part.get("Content-Disposition", "").lower().startswith("attachment"):
            continue
        ctype = part.get_content_type()
        try:
            payload = part.get_payload(decode=True)
            if payload is None:
                continue
            charset = part.get_content_charset() or "utf-8"
            content = payload.decode(charset, errors="replace")
        except Exception:
            continue
        if ctype == "text/html" and html_part is None:
            html_part = content
        elif ctype == "text/plain" and text_part is None:
            text_part = content
    if html_part:
        return html_to_text(html_part, keep_links=True)
    return tidy(text_part or "")


def parse_message(raw_bytes):
    msg = email.message_from_bytes(raw_bytes)
    msg_id = msg.get("Message-ID") or ""
    subject = _decode(msg.get("Subject"))
    sender = _decode(msg.get("From"))
    date = msg.get("Date") or ""
    body = _body(msg)
    key = hashlib.sha1((msg_id or subject + date).encode("utf-8", "ignore")).hexdigest()[:16]
    return {"key": key, "subject": subject, "from": sender, "date": date, "body": body}


def fetch_recent(user, app_password, days=3, mailbox="INBOX"):
    since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%d-%b-%Y")
    conn = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    try:
        conn.login(user, app_password.replace(" ", ""))
        conn.select(mailbox, readonly=True)  # read-only: never marks your mail as read
        status, data = conn.search(None, "SINCE", since)
        if status != "OK":
            return []
        messages = []
        for num in data[0].split():
            status, parts = conn.fetch(num, "(BODY.PEEK[])")
            if status != "OK" or not parts or not isinstance(parts[0], tuple):
                continue
            messages.append(parse_message(parts[0][1]))
        return messages
    finally:
        try:
            conn.logout()
        except Exception:
            pass
