#!/usr/bin/env python3
"""Haalt Two Rivers Marathon-nieuws op en schrijft data/news.json.

Volgorde: eerst de (WordPress-)feed van de officiele site, daarna Google News RSS
als fallback. Als niets lukt blijft het bestaande bestand staan.
"""
import email.utils, html, json, re, sys, time, urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data" / "news.json"
FEEDS = [
    ("tworiversmarathon.nl", "https://tworiversmarathon.nl/category/nieuws/feed/"),
    ("tworiversmarathon.nl", "https://tworiversmarathon.nl/feed/"),
    ("Google News", "https://news.google.com/rss/search?q=%22Two+Rivers+Marathon%22+Zaltbommel&hl=nl&gl=NL&ceid=NL:nl"),
]
UA = {"User-Agent": "Mozilla/5.0 (compatible; marathon-dashboard/1.0)"}


def clean(text, n=280):
    text = html.unescape(re.sub(r"<[^>]+>", " ", text or ""))
    text = re.sub(r"\s+", " ", text).strip()
    return text[:n] + ("…" if len(text) > n else "")


def parse_date(s):
    try:
        return time.strftime("%Y-%m-%d", email.utils.parsedate_to_datetime(s).timetuple())
    except Exception:
        return None


def fetch(name, url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        root = ET.fromstring(r.read())
    items = []
    for it in root.iter("item"):
        title = clean(it.findtext("title"), 200)
        if name == "Google News" and "two rivers" not in title.lower():
            continue
        src = it.find("source")
        items.append({
            "title": title,
            "url": re.sub(r"\?utm_[^#]*", "", it.findtext("link") or ""),
            "date": parse_date(it.findtext("pubDate") or ""),
            "summary": clean(it.findtext("description")),
            "source": src.text if src is not None and src.text else name,
        })
    return items


def main():
    for name, url in FEEDS:
        try:
            items = fetch(name, url)
        except Exception as e:  # netwerk, 404, geen XML
            print(f"{url}: {e}")
            continue
        if items:
            items.sort(key=lambda i: i["date"] or "", reverse=True)
            DATA.write_text(json.dumps({"updated": time.strftime("%Y-%m-%dT%H:%M:%S"), "source": name,
                                        "items": items[:20]}, ensure_ascii=False, indent=1))
            print(f"{len(items)} nieuwsitems van {name}")
            return 0
    print("Geen nieuws opgehaald; bestaand bestand behouden.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
