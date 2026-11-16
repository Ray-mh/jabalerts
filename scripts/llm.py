"""Minimal Claude API client (standard library only)."""
import json
import os
import time
import urllib.error
import urllib.request

API_URL = "https://api.anthropic.com/v1/messages"


class LLMError(Exception):
    pass


def ask(model, system, user, max_tokens=2000):
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        raise LLMError("ANTHROPIC_API_KEY is not set")
    body = json.dumps({
        "model": model,
        "max_tokens": max_tokens,
        "system": system,
        "messages": [{"role": "user", "content": user}],
    }).encode("utf-8")
    last = None
    for attempt in range(4):
        req = urllib.request.Request(API_URL, data=body, method="POST", headers={
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        })
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            return "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:300]
            last = f"HTTP {e.code}: {detail}"
            if e.code in (429, 500, 502, 503, 504, 529):
                time.sleep(5 * (attempt + 1))
                continue
            raise LLMError(last)
        except (urllib.error.URLError, TimeoutError) as e:
            last = str(e)
            time.sleep(5 * (attempt + 1))
    raise LLMError(f"Claude API failed after retries: {last}")


def ask_json(model, system, user, max_tokens=2000):
    text = ask(model, system, user, max_tokens)
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise LLMError(f"No JSON in model reply: {text[:200]}")
    return json.loads(text[start:end + 1])
