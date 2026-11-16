"""HTML -> plain text helpers (standard library only)."""
import html
import re
from html.parser import HTMLParser

_BLOCK = {"p", "div", "br", "tr", "li", "h1", "h2", "h3", "h4", "h5", "h6", "table", "section", "article"}
_SKIP = {"script", "style", "head", "noscript", "svg"}


class _Extractor(HTMLParser):
    def __init__(self, keep_links):
        super().__init__(convert_charrefs=True)
        self.keep_links = keep_links
        self.out = []
        self.skip = 0
        self.href_stack = []

    def handle_starttag(self, tag, attrs):
        if tag in _SKIP:
            self.skip += 1
        if tag in _BLOCK:
            self.out.append("\n")
        if tag == "a":
            href = dict(attrs).get("href") or ""
            self.href_stack.append(href)

    def handle_endtag(self, tag):
        if tag in _SKIP and self.skip:
            self.skip -= 1
        if tag == "a" and self.href_stack:
            href = self.href_stack.pop()
            if self.keep_links and href.startswith("http"):
                self.out.append(f" <{href}> ")
        if tag in _BLOCK:
            self.out.append("\n")

    def handle_data(self, data):
        if not self.skip:
            self.out.append(data)


def html_to_text(raw_html, keep_links=False):
    p = _Extractor(keep_links)
    try:
        p.feed(raw_html)
        p.close()
    except Exception:
        pass
    text = html.unescape("".join(p.out))
    return tidy(text)


def tidy(text):
    text = text.replace("\r", "")
    text = re.sub(r"[ \t ​‌]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
