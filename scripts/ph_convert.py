#!/usr/bin/env python3
"""Convert cached LawPhil pages (see ph_fetch.py) to LawCodex Markdown.

Usage: python ph_convert.py [--raw DIR] [--out DIR] [--modules ...]
"""
import argparse
import datetime
import json
import os
import re
import subprocess
import sys
import unicodedata

import html2text
from bs4 import BeautifulSoup, NavigableString

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ph_fetch import BASE, cache_path  # noqa: E402

RETRIEVED = os.environ.get("PH_RETRIEVED", datetime.date.today().isoformat())

# module -> (number key, directory, type, identifier prefix for filenames, label regex)
SERIES = {
    "republic": ("ra_number", "republic-acts", "act", "ra"),
    "commonwealth": ("ca_number", "commonwealth-acts", "act", "ca"),
    "bataspambansa": ("bp_number", "batas-pambansa", "act", "bp"),
    "presidential": ("pd_number", "presidential-decrees", "decree", "pd"),
    "execord": ("execord_number", "executive-orders", "executive_order", "eo"),
    "acts": ("act_number", "acts", "act", "act"),
}

CONSTITUTIONS = [
    # page, slug, title, date, status
    ("consti/cons1987.html", "1987-constitution", "The 1987 Constitution of the Republic of the Philippines",
     "1987-02-02", "in_force"),
    ("consti/cons1986.html", "1986-freedom-constitution", "1986 Provisional (Freedom) Constitution of the Republic of the Philippines",
     "1986-03-25", "repealed"),
    ("consti/cons1973.html", "1973-constitution", "The 1973 Constitution of the Republic of the Philippines",
     "1973-01-17", "repealed"),
    ("consti/cons1943.html", "1943-constitution", "The 1943 Constitution of the Republic of the Philippines",
     "1943-09-04", "repealed"),
    ("consti/cons1935.html", "1935-constitution", "The 1935 Constitution of the Philippines",
     "1935-05-14", "repealed"),
    ("consti/consmalo.html", "1899-malolos-constitution", "The Malolos Constitution (Political Constitution of 1899)",
     "1899-01-21", "repealed"),
]

# (module, number, slug, title) -- key codes, copied into codes/
CODES = [
    ("republic", "386", "civil-code", "Civil Code of the Philippines"),
    ("acts", "3815", "revised-penal-code", "The Revised Penal Code"),
    ("presidential", "442", "labor-code", "Labor Code of the Philippines"),
    ("execord", "209", "family-code", "The Family Code of the Philippines"),
    ("execord", "292", "administrative-code-of-1987", "Administrative Code of 1987"),
    ("republic", "8424", "national-internal-revenue-code", "National Internal Revenue Code of 1997 (Tax Reform Act of 1997)"),
    ("republic", "7160", "local-government-code", "Local Government Code of 1991"),
    ("republic", "11232", "revised-corporation-code", "Revised Corporation Code of the Philippines"),
    ("republic", "8293", "intellectual-property-code", "Intellectual Property Code of the Philippines"),
    ("republic", "10863", "customs-modernization-and-tariff-act", "Customs Modernization and Tariff Act"),
    ("batas pambansa", "881", "omnibus-election-code", "Omnibus Election Code of the Philippines"),
    ("presidential", "603", "child-and-youth-welfare-code", "The Child and Youth Welfare Code"),
    ("presidential", "612", "insurance-code", "The Insurance Code of the Philippines"),
    ("republic", "10607", "insurance-code-amended-2013", "Insurance Code (as amended by RA 10607)"),
    ("presidential", "1529", "property-registration-decree", "Property Registration Decree"),
    ("presidential", "1067", "water-code", "The Water Code of the Philippines"),
    ("presidential", "856", "code-on-sanitation", "Code on Sanitation of the Philippines"),
    ("presidential", "705", "revised-forestry-code", "Revised Forestry Code of the Philippines"),
    ("presidential", "1096", "national-building-code", "National Building Code of the Philippines"),
    ("presidential", "1083", "code-of-muslim-personal-laws", "Code of Muslim Personal Laws of the Philippines"),
    ("republic", "8550", "fisheries-code", "The Philippine Fisheries Code of 1998"),
    ("republic", "8799", "securities-regulation-code", "The Securities Regulation Code"),
    ("republic", "9520", "cooperative-code", "Philippine Cooperative Code of 2008"),
    ("republic", "6657", "comprehensive-agrarian-reform-law", "Comprehensive Agrarian Reform Law of 1988"),
    ("republic", "3844", "agricultural-land-reform-code", "Agricultural Land Reform Code"),
    ("republic", "6938", "cooperative-code-1990", "Cooperative Code of the Philippines (1990)"),
    ("republic", "9851", "ihl-crimes-act", "Philippine Act on Crimes Against International Humanitarian Law"),
    ("republic", "7942", "mining-act", "Philippine Mining Act of 1995"),
]
CODE_MODULE_ALIAS = {"batas pambansa": "bataspambansa"}

DIVISION_KW = ["BOOK", "PART", "TITLE", "SUBTITLE", "CHAPTER", "SUBCHAPTER", "ARTICLE", "SECTION", "SUB-SECTION",
               "SUBSECTION", "DIVISION", "PARAGRAPH"]
DIV_RANK = {k: i for i, k in enumerate(DIVISION_KW)}
NUM_TOKEN = r"(?:[IVXLCDM]+|\d+[A-Z]?(?:-[A-Z])?|ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT|NINE|TEN|ELEVEN|TWELVE|" \
            r"THIRTEEN|FOURTEEN|FIFTEEN|SIXTEEN|SEVENTEEN|EIGHTEEN|NINETEEN|TWENTY|I|[A-Z])"
DIV_RE = re.compile(r"^(?:(PRELIMINARY|FINAL|SPECIAL|GENERAL|TRANSITORY)\s+)?(" + "|".join(
    re.escape(k) for k in sorted(DIVISION_KW, key=len, reverse=True)) + r")\b\.?\s*(" + NUM_TOKEN + r")?\b", re.I)
PROV_RE = re.compile(
    r"^\s*\*\*\s*((?:Article|ARTICLE|Art\.|ART\.|Section|SECTION|Sec\.|SEC\.|Sec|SEC|Rule|RULE|Paragraph)"
    r"\s*\.?\s*[0-9]+[0-9A-Za-z\-\.\(\)]*?)\s*[\.\-:–—]?\s*\*\*\s*(.*)$")
PROV_RE2 = re.compile(
    r"^\s*((?:Article|ARTICLE|Art\.|ART\.|Section|SECTION|Sec\.|SEC\.)\s*[0-9]+[0-9A-Za-z\-]*\.)\s+(.*)$")

PROV_ANY = re.compile(
    r"^\s*(?P<open>\*\*|__)?\s*(?P<label>(?:Section|SECTION|Sec\.|SEC\.|Sec|SEC|Article|ARTICLE|Art\.|ART\.)"
    r"\s*[0-9]+(?:-?[A-Z](?![a-z]))?(?:-[0-9]+)?)\s*(?P<sep>\.|:|(?=\*\*))\s*(?P<close>\*\*|__)?")


def match_provision(body):
    m = PROV_ANY.match(body)
    if not m:
        return None
    rest = body[m.end():]
    if not m.group("open"):
        after = body[m.end("sep"):m.end("sep") + 1]
        if m.group("sep") != "." or after not in (" ", "_", "*", "\n", ""):
            return None
    first, _, tail = rest.partition("\n")
    if m.group("open") and not m.group("close") and first.count("**") % 2 == 1:
        first = first.replace("**", "", 1)
    rest = (first + ("\n" + tail if tail else "")).strip()
    label = normalize_ws(m.group("label"))
    return label, rest


C_MARK = "⟦C⟧"
BR_MARK = "⟦BR⟧"
TBL_MARK = "⟦TABLE%d⟧"


def slugify(s, maxlen=70):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s.lower()).strip("-")
    if len(s) > maxlen:
        s = s[:maxlen].rsplit("-", 1)[0]
    return s or "untitled"


def yq(s):
    s = (s or "").replace("\\", "\\\\").replace('"', '\\"')
    s = re.sub(r"\s+", " ", s).strip()
    return f'"{s}"'


def decode(raw):
    m = re.search(rb'charset=["\']?([\w-]+)', raw[:2000])
    enc = (m.group(1).decode().lower() if m else "windows-1252")
    if enc in ("iso-8859-1", "latin-1", "us-ascii", "ascii"):
        enc = "windows-1252"
    try:
        return raw.decode(enc)
    except (UnicodeDecodeError, LookupError):
        try:
            return raw.decode("utf-8")
        except UnicodeDecodeError:
            return raw.decode("windows-1252", "replace")


def is_centered(tag):
    if tag.name == "center":
        return True
    if (tag.get("align") or "").lower() == "center":
        return True
    cls = tag.get("class") or []
    if any(c in ("c", "cb", "center", "centered") for c in cls):
        return True
    st = (tag.get("style") or "").replace(" ", "").lower()
    return "text-align:center" in st


def clean_table(tbl):
    for t in tbl.find_all(True):
        attrs = {k: v for k, v in t.attrs.items() if k in ("colspan", "rowspan")}
        t.attrs = attrs
        if t.name in ("font", "span", "a", "dir", "center", "div", "p", "img"):
            if t.name == "img":
                t.decompose()
            elif t.name == "p":
                t.append(" ")
                t.unwrap()
            else:
                t.unwrap()
    tbl.attrs = {}
    html = str(tbl)
    html = re.sub(r"\s+", " ", html)
    html = re.sub(r"\s*(</?(?:table|tr|thead|tbody|tfoot)>)\s*", r"\n\1", html)
    html = re.sub(r"\s*(<t[dh][^>]*>)\s*", r"\n\1", html)
    html = re.sub(r"\s*(</t[dh]>)", r"\1", html)
    return html.strip()


def table_is_simple(tbl):
    if tbl.find("table"):
        return False
    rows = tbl.find_all("tr")
    if not rows:
        return False
    for c in tbl.find_all(["td", "th"]):
        if c.get("colspan") not in (None, "1") or c.get("rowspan") not in (None, "1"):
            return False
        if c.find(["p", "br", "ul", "ol", "dir"]) and len(c.get_text(strip=True)) > 0 and len(c.find_all(["p", "br"])) > 1:
            return False
    n = {len(r.find_all(["td", "th"], recursive=False)) for r in rows}
    return len(n) == 1 and next(iter(n)) > 1


def cell_text(c):
    t = c.get_text(" ", strip=True)
    t = re.sub(r"\s+", " ", t).replace("|", "\\|")
    return t


def table_markdown(tbl):
    rows = [[cell_text(c) for c in r.find_all(["td", "th"], recursive=False)] for r in tbl.find_all("tr")]
    rows = [r for r in rows if any(x for x in r)]
    if not rows:
        return ""
    out = ["| " + " | ".join(rows[0]) + " |", "|" + "---|" * len(rows[0])]
    for r in rows[1:]:
        out.append("| " + " | ".join(r) + " |")
    return "\n".join(out)


def extract_body(html):
    soup = BeautifulSoup(html, "lxml")
    title_tag = soup.find("title")
    page_title = title_tag.get_text(" ", strip=True) if title_tag else ""
    body = soup.find("blockquote") or soup.body or soup
    for t in body.find_all(["script", "style", "img", "hr", "noscript", "gcse:searchbox-only", "cite"]):  # <cite> holds LawPhil watermarks
        t.decompose()
    for a in body.find_all("a"):
        if "id" in (a.get("class") or []) or (a.get("href") or "").startswith("javascript:"):
            a.decompose()
        elif a.get("href", "").startswith("#top"):
            a.decompose()
    body.name = "div"
    for t in body.find_all(["blockquote", "dir", "menu"]):
        t.name = "div"
    return soup, body, page_title


def _inner_table(tbl, body):
    for p in tbl.parents:
        if p is body:
            return False
        if p.name == "table":
            return True
    return False


def body_to_markdown(body):
    tables = []
    # tables first (innermost-out handled by only top-level tables)
    for tbl in body.find_all("table"):
        if _inner_table(tbl, body):
            continue
        if table_is_simple(tbl):
            md = table_markdown(tbl)
        else:
            md = clean_table(tbl)
        tables.append(md)
        tbl.replace_with(NavigableString("\n\n" + (TBL_MARK % (len(tables) - 1)) + "\n\n"))
        # wrap as paragraph marker
    for tag in body.find_all(["p", "center", "div", "h1", "h2", "h3", "h4", "h5", "h6"]):
        if tag.name in ("center", "div") and tag.find(["p", "div", "table", "center", "h1", "h2", "h3", "h4"]):
            continue
        if is_centered(tag):
            for br in tag.find_all("br"):
                br.replace_with(NavigableString(" " + BR_MARK + " "))
            if tag.get_text(strip=True):
                tag.insert(0, NavigableString(C_MARK))
    h = html2text.HTML2Text()
    h.body_width = 0
    h.ignore_links = True
    h.ignore_images = True
    h.unicode_snob = True
    h.ignore_tables = False
    h.single_line_break = False
    h.ul_item_mark = "-"
    md = h.handle(str(body))
    for i, t in enumerate(tables):
        md = md.replace(TBL_MARK % i, "\n" + t + "\n")
    return md


def strip_emph(s):
    s = s.replace("**", "").replace("__", "")
    s = re.sub(r"(?<!\w)_(?=\S)|(?<=\S)_(?!\w)", "", s)
    return s.strip()


def normalize_ws(s):
    s = s.replace(" ", " ").replace("\t", " ")
    return re.sub(r"[ ]{2,}", " ", s).strip()


def build_document(md):
    """Turn html2text output with centring markers into structured markdown lines."""
    paras = re.split(r"\n\s*\n", md)
    out = []
    kinds = []  # list of (kind_rank) in order seen
    items = []  # (kind, payload)
    for p in paras:
        p = p.strip("\n")
        if not p.strip():
            continue
        if p.lstrip().startswith(("|", "<table")):
            items.append(("raw", p.strip()))
            continue
        lines = [normalize_ws(x) for x in p.split("\n")]
        text = " ".join(x for x in lines if x)
        if C_MARK in text:
            t = text.replace(C_MARK, "")
            parts = [strip_emph(x) for x in t.split(BR_MARK)]
            parts = [normalize_ws(x) for x in parts if strip_emph(x)]
            if not parts:
                continue
            m = DIV_RE.match(parts[0])
            first = parts[0]
            if m and len(first) < 200 and (m.group(3) or m.group(1) or first.strip(" .").upper() == m.group(2).upper()):
                kind = m.group(2).upper().replace("SUB-SECTION", "SUBSECTION")
                items.append(("div", (kind, " — ".join(parts))))
            else:
                items.append(("center", parts))
            continue
        text = text.replace(BR_MARK, " ")
        # restore hard line breaks inside paragraph
        body = "\n".join(x for x in lines if x).replace(BR_MARK, " ")
        pm = match_provision(body)
        if pm:
            items.append(("prov", pm))
            continue
        items.append(("para", body))

    # Merge caption-only centred paragraphs that follow a division heading
    merged = []
    for kind, payload in items:
        if kind == "center" and merged and merged[-1][0] == "div" and not merged[-1][2] \
                and " — " not in merged[-1][1][1] and len(payload) == 1 and len(payload[0]) < 300:
            k, txt = merged[-1][1]
            merged[-1] = ("div", (k, txt + " — " + " — ".join(payload)), True)
            continue
        merged.append((kind, payload, False))

    present = sorted({p[1][0] for p in merged if p[0] == "div"}, key=lambda k: DIV_RANK.get(k, 99))
    lvl = {k: min(2 + i, 6) for i, k in enumerate(present)}
    prov_level = min(2 + len(present), 6)
    for kind, payload, _ in merged:
        if kind == "div":
            k, txt = payload
            out.append("#" * lvl[k] + " " + txt)
        elif kind == "prov":
            label, rest = payload
            if prov_level <= 6 and len(present) < 5:
                out.append("#" * prov_level + " " + label)
            else:
                out.append("###### " + label)
            if rest:
                out.append(rest)
        elif kind == "center":
            out.append("  \n".join(payload))
        else:
            out.append(payload)
    text = "\n\n".join(out)
    text = re.sub(r"(?<=\s)(?:__|\*\*\*\*|\*\*\s*\*\*)(?=\s)", "", text)
    text = re.sub(r"[ ]{2,}(?=\S)", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    # remove stray LawPhil footer
    text = re.sub(r"\n*The Lawphil Project - Arellano Law Foundation\s*$", "", text.strip())
    return text.strip() + "\n"


def pdf_to_text(path):
    try:
        r = subprocess.run(["pdftotext", "-layout", "-enc", "UTF-8", path, "-"], capture_output=True, timeout=300)
        t = r.stdout.decode("utf-8", "replace")
    except Exception:
        return ""
    t = t.replace("\f", "\n\n")
    paras = re.split(r"\n\s*\n", t)
    out = []
    for p in paras:
        lines = [x.strip() for x in p.split("\n") if x.strip()]
        if not lines:
            continue
        out.append(re.sub(r"[ ]{2,}", " ", " ".join(lines)))
    return "\n\n".join(out)


def front_matter(meta):
    keys = ["title", "identifier", "number", "type", "jurisdiction", "language", "date", "last_amended", "status",
            "source", "source_pdf", "source_format", "note", "retrieved"]
    lines = ["---"]
    for k in keys:
        if k in meta and meta[k] not in (None, ""):
            v = meta[k]
            if k in ("date", "last_amended", "retrieved", "jurisdiction", "language", "type", "status",
                     "source_format"):
                lines.append(f"{k}: {v}")
            else:
                lines.append(f"{k}: {yq(str(v))}")
    lines.append("---")
    return "\n".join(lines) + "\n\n"


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)


def number_of(label):
    m = re.search(r"(?:No\.?|Blg\.?|Number)\s*([0-9][0-9A-Za-z\-]*)", label or "")
    if m:
        return m.group(1).rstrip("-")
    m = re.search(r"([0-9][0-9A-Za-z\-]*)", label or "")
    return m.group(1) if m else ""


def convert_series(mod, raw, outdir, stats, code_targets):
    numkey, d, typ, pfx = SERIES[mod]
    rows = json.load(open(os.path.join(raw, "lists", f"{mod}.json")))
    used = set()
    for row in rows:
        label = (row.get(numkey) or "").strip()
        if mod == "republic" and not re.match(r"Republic Act", label, re.I):
            stats["skipped_non_" + mod] = stats.get("skipped_non_" + mod, 0) + 1
            continue
        num = number_of(label)
        date = (row.get("date") or "")[:10]
        year = date[:4] if re.match(r"\d{4}", date) else "unknown"
        desc = row.get("description") or row.get("citation") or row.get("subject") or ""
        desc = normalize_ws(re.sub(r"<[^>]+>", " ", desc))
        src, src_pdf, body = row.get("_html"), row.get("_pdf"), None
        fmt = "html"
        if src:
            p = cache_path(raw, src)
            if os.path.exists(p):
                soup, b, _ = extract_body(decode(open(p, "rb").read()))
                body = build_document(body_to_markdown(b))
        if body is None and src_pdf:
            p = cache_path(raw, src_pdf)
            if os.path.exists(p):
                body = pdf_to_text(p)
                fmt = "pdf"
                if body.strip():
                    body += "\n"
                src = src_pdf
        if not body or not body.strip():
            stats["missing_" + mod] = stats.get("missing_" + mod, 0) + 1
            missing.append((mod, label, date, row.get("_html") or row.get("_pdf") or ""))
            continue
        sdesc = re.sub(r"^(an?\s+)?(act|decree|order)\s+(to\s+|of\s+)?", "", desc, flags=re.I) or desc
        base = f"{pfx}-{slugify(num, 20)}-{slugify(sdesc, 60)}" if num else f"{pfx}-{slugify(sdesc, 70)}"
        fn = os.path.join(d, year, base + ".md")
        i = 2
        while fn in used:
            fn = os.path.join(d, year, f"{base}-{i}.md")
            i += 1
        used.add(fn)
        title = f"{label}" + (f" — {desc}" if desc else "")
        meta = {
            "title": title, "identifier": label, "number": num, "type": typ, "jurisdiction": "ph",
            "language": "en", "date": date or None, "status": "unknown", "source": src,
            "source_pdf": src_pdf if fmt == "html" else None,
            "source_format": fmt, "retrieved": RETRIEVED,
        }
        if mod == "execord" and "1986-02-25" <= date <= "1987-07-26":
            meta["note"] = ("Issued by President Corazon C. Aquino in the exercise of legislative power "
                            "(Freedom Constitution, Art. II s.1; 1987 Constitution, Art. XVIII s.6)")
        if "AS AMENDED" in body[:1500].upper():
            meta["note"] = ("LawPhil text is headed 'as amended': it may incorporate later amendments "
                            "rather than the as-enacted text")
        h1 = f"# {label}\n\n" + (f"**{desc}**\n\n" if desc else "")
        content = front_matter(meta) + h1 + body
        write(os.path.join(outdir, fn), content)
        stats[mod] = stats.get(mod, 0) + 1
        key = (mod, num)
        if key in code_targets:
            code_targets[key] = (meta, body, desc)


missing = []


def main():
    ap = argparse.ArgumentParser()
    here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument("--raw", default=os.path.join(here, "..", "..", "_raw", "ph"))
    ap.add_argument("--out", default=os.path.join(here, ".."))
    ap.add_argument("--modules", default=",".join(SERIES))
    a = ap.parse_args()
    raw, out = os.path.abspath(a.raw), os.path.abspath(a.out)
    stats = {}
    # constitutions
    for page, slug, title, date, status in CONSTITUTIONS:
        p = cache_path(raw, BASE + "/" + page)
        if not os.path.exists(p):
            print("missing constitution", page)
            continue
        soup, b, _ = extract_body(decode(open(p, "rb").read()))
        body = build_document(body_to_markdown(b))
        meta = {"title": title, "identifier": slug, "type": "constitution", "jurisdiction": "ph", "language": "en",
                "date": date, "status": status, "source": BASE + "/" + page, "source_format": "html",
                "retrieved": RETRIEVED}
        if slug == "1899-malolos-constitution":
            meta["note"] = "English translation as published by LawPhil; the original was in Spanish"
        write(os.path.join(out, "constitution", slug + ".md"), front_matter(meta) + f"# {title}\n\n" + body)
        stats["constitution"] = stats.get("constitution", 0) + 1
    code_targets = {(CODE_MODULE_ALIAS.get(m, m), n): None for m, n, _, _ in CODES}
    for mod in [m for m in a.modules.split(",") if m]:
        convert_series(mod, raw, out, stats, code_targets)
    for m, n, slug, title in CODES:
        v = code_targets.get((CODE_MODULE_ALIAS.get(m, m), n))
        if not v:
            print("code not found", m, n, slug)
            continue
        meta, body, desc = v
        meta = dict(meta)
        meta["title"] = title
        meta["type"] = "code"
        h1 = f"# {title}\n\n**{meta['identifier']}" + (f" — {desc}" if desc else "") + "**\n\n"
        write(os.path.join(out, "codes", slug + ".md"), front_matter(meta) + h1 + body)
        stats["codes"] = stats.get("codes", 0) + 1
    with open(os.path.join(raw, "missing.tsv"), "w") as f:
        for r in missing:
            f.write("\t".join(r) + "\n")
    json.dump(stats, open(os.path.join(raw, "stats.json"), "w"), indent=1)
    print(json.dumps(stats, indent=1))


if __name__ == "__main__":
    main()
