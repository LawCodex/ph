#!/usr/bin/env python3
"""Fetch Philippine legislation from The LawPhil Project (lawphil.net).

Step 1: list every instrument via the public JSON listing API that the LawPhil
        browse pages themselves use (https://lawphil.net/api/public/<module>).
Step 2: download each instrument's HTML page (or its PDF when no HTML exists)
        into a local cache (default: ../../_raw/ph/), skipping files already cached.

Politeness: descriptive User-Agent, <= 3 concurrent requests, a delay between
requests per worker, retries with exponential backoff. lawphil.net has no
robots.txt (HTTP 404, checked 2026-10-12), so there is no Crawl-delay to obey.

Usage: python ph_fetch.py [--raw DIR] [--modules republic,acts,...] [--lists-only]
"""
import argparse
import json
import os
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import requests

UA = "LawCodex/1.0 (+https://github.com/LawCodex)"
BASE = "https://lawphil.net"

# module -> (number key, base path, year-subdir prefix or None for flat)
MODULES = {
    "republic": ("ra_number", "/statutes/repacts", "ra"),
    "commonwealth": ("ca_number", "/statutes/comacts", "ca"),
    "bataspambansa": ("bp_number", "/statutes/bataspam", "bp"),
    "presidential": ("pd_number", "/statutes/presdecs", None),
    "execord": ("execord_number", "/executive/execord", "eo"),
    "acts": ("act_number", "/statutes/acts", "act"),
}

# Constitutions (static pages)
EXTRA_PAGES = {
    "consti/cons1987.html": "/consti/cons1987.html",
    "consti/cons1986.html": "/consti/cons1986.html",
    "consti/cons1973.html": "/consti/cons1973.html",
    "consti/cons1943.html": "/consti/cons1943.html",
    "consti/cons1935.html": "/consti/cons1935.html",
    "consti/consmalo.html": "/consti/consmalo.html",
}

_local = threading.local()


def session():
    s = getattr(_local, "s", None)
    if s is None:
        s = requests.Session()
        s.headers["User-Agent"] = UA
        _local.s = s
    return s


def get(url, delay=0.4, tries=6):
    for i in range(tries):
        try:
            r = session().get(url, timeout=60)
            time.sleep(delay)
            if r.status_code == 200:
                return r
            if r.status_code == 404:
                return r
            if r.status_code in (429, 500, 502, 503, 504):
                time.sleep(5 * (2 ** i))
                continue
            return r
        except requests.RequestException as e:
            print(f"  retry {i} {url}: {e}", file=sys.stderr)
            time.sleep(5 * (2 ** i))
    return None


def extract_year(path):
    m = re.search(r"(\d{4})(?=\.\w+$)", path)
    return m.group(1) if m else ""


def html_url(mod, url):
    if not url:
        return None
    if url.startswith("http"):
        return url
    _, base, prefix = MODULES[mod]
    if prefix is None:
        return f"{BASE}{base}/{url}"
    return f"{BASE}{base}/{prefix}{extract_year(url)}/{url}"


def pdf_url(mod, row):
    if not row.get("pdf_availability") or not row.get("pdf_path"):
        return None
    p = row["pdf_path"]
    _, base, prefix = MODULES[mod]
    if prefix is None:
        return f"{BASE}{base}/pdf/{p}"
    return f"{BASE}{base}/{prefix}{extract_year(p)}/pdf/{p}"


def fetch_list(mod, raw):
    out = os.path.join(raw, "lists", f"{mod}.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    rows, page, last = [], 1, 1
    while page <= last:
        r = get(f"{BASE}/api/public/{mod}?rows=100&sort=oldest&page={page}&search=", delay=1.0)
        d = r.json()
        rows.extend(d["data"])
        last = d["last_page"]
        page += 1
    for row in rows:
        row["_html"] = html_url(mod, row.get("url"))
        row["_pdf"] = pdf_url(mod, row)
    with open(out, "w") as f:
        json.dump(rows, f, ensure_ascii=False, indent=0)
    print(f"{mod}: {len(rows)} rows", flush=True)
    return rows


def cache_path(raw, url):
    rel = url.replace(BASE + "/", "").replace("https://", "").replace("http://", "")
    return os.path.join(raw, "pages", rel)


def download(raw, url):
    p = cache_path(raw, url)
    if os.path.exists(p) or os.path.exists(p + ".404"):
        return "cached"
    r = get(url)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    if r is None:
        return "fail"
    if r.status_code == 404:
        open(p + ".404", "w").close()
        return "404"
    if r.status_code != 200:
        return f"http{r.status_code}"
    tmp = p + ".part"
    with open(tmp, "wb") as f:
        f.write(r.content)
    os.replace(tmp, p)
    return "ok"


def main():
    ap = argparse.ArgumentParser()
    here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument("--raw", default=os.path.join(here, "..", "..", "_raw", "ph"))
    ap.add_argument("--modules", default=",".join(MODULES))
    ap.add_argument("--lists-only", action="store_true")
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--relist", action="store_true")
    a = ap.parse_args()
    raw = os.path.abspath(a.raw)

    urls = [BASE + v for v in EXTRA_PAGES.values()]
    for mod in a.modules.split(","):
        lp = os.path.join(raw, "lists", f"{mod}.json")
        if os.path.exists(lp) and not a.relist:
            rows = json.load(open(lp))
        else:
            rows = fetch_list(mod, raw)
        for row in rows:
            if row["_html"]:
                urls.append(row["_html"])
            elif row["_pdf"]:
                urls.append(row["_pdf"])
    if a.lists_only:
        return
    print(f"{len(urls)} documents to fetch", flush=True)
    stats = {}
    done = 0
    with ThreadPoolExecutor(a.workers) as ex:
        for res in ex.map(lambda u: download(raw, u), urls):
            stats[res] = stats.get(res, 0) + 1
            done += 1
            if done % 500 == 0:
                print(done, stats, flush=True)
    print("done", stats, flush=True)


if __name__ == "__main__":
    main()
