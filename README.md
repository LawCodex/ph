# Philippines — LawCodex

Legislation of the Republic of the Philippines as plain Markdown (English), one file per
instrument. Part of [LawCodex](https://github.com/LawCodex).

> **Texts are as enacted / as published, not consolidated.** The Philippines has no official
> consolidated (in-force, "as amended") edition of its statutes. Each file reproduces the text
> of the instrument as originally enacted, as transcribed by The LawPhil Project. Later
> amendments, repeals and declarations of unconstitutionality are **not** applied, and
> `status` is therefore `unknown` for every statute. A handful of LawPhil pages (e.g. the Labor
> Code, PD 442) are headed "as amended" and incorporate later amendments; those files carry a
> `note` in their front matter. Nothing here is an official text: check the Official Gazette or
> the enrolled copies before relying on any provision.

## Contents

<!-- COUNTS -->
| Category | Directory | Files |
|---|---|---|
| Constitutions (1987 in force; 1986 Freedom, 1973, 1943, 1935, 1899 Malolos — historical) | `constitution/` | 6 |
| Main codes (copies, see below) | `codes/` | 27 |
| Republic Acts (RA 1 – RA 12325, 1946–2026) | `republic-acts/` | 12,001 |
| Commonwealth Acts (CA 1 – 733, 1935–1946) | `commonwealth-acts/` | 733 |
| Batas Pambansa (BP 88 – 889, 1979–1986) | `batas-pambansa/` | 806 |
| Presidential Decrees (PD 1 – 1913, 1972–1986) | `presidential-decrees/` | 1,696 |
| Executive Orders (1901–2026) | `executive-orders/` | 5,782 |
| Acts of the Philippine Commission / Legislature (Act 1 – 4275, 1900–1935) | `acts/` | 4,199 |
| **Total** | | **25,250** |

Numbers with letter suffixes (e.g. PD 1258-A, EO 124-B) are separate files. 16 instruments
that exist on LawPhil only as PDF scans were converted from the PDF text layer (OCR quality is
poor; flagged with a `note`).
<!-- /COUNTS -->

## Structure

```
constitution/<year>-<name>.md
codes/<code-slug>.md                         # copies of the main codes, type: code
republic-acts/<year>/ra-<n>-<slug>.md        # Republic Acts, 1946–present (Congress)
commonwealth-acts/<year>/ca-<n>-<slug>.md    # Commonwealth Acts, 1935–1946 (National Assembly / Congress)
batas-pambansa/<year>/bp-<n>-<slug>.md       # Batas Pambansa, 1978–1985 (Interim / Regular Batasang Pambansa)
presidential-decrees/<year>/pd-<n>-<slug>.md # Presidential Decrees, 1972–1986 (Marcos, martial law legislation)
executive-orders/<year>/eo-<n>-<slug>.md     # Executive Orders, 1901–present (all that LawPhil lists)
acts/<year>/act-<n>-<slug>.md                # Acts of the Philippine Commission / Philippine Legislature, 1900–1935
```

`<year>` is the year of approval (`unknown` when LawPhil gives no date). Each file has YAML
front matter (`title`, `identifier` = official number as styled by LawPhil, `number`, `type`,
`jurisdiction: ph`, `language: en`, `date` = date of approval, `status`, `source` = LawPhil page,
`source_pdf` where LawPhil also holds a scan, `source_format` (`html` or `pdf`), `retrieved`).
The H1 is the official number, followed by the long title in bold. Divisions of the text (Book,
Part, Title, Chapter, Article, Section headings set as centred headings in the source) are mapped
to Markdown headings in their order of rank; individual provisions ("Section 1.", "Article 1.",
"Sec. 1.") become the deepest heading level, followed by their text. Tables are kept as Markdown
tables when simple and as plain HTML otherwise. LawPhil inserts anti-copying watermarks (e.g.
`1awphi1`, `lawphil`) inside `<cite>` tags in the middle of sentences; these are removed during
conversion. Page-level annotations by LawPhil (e.g. "Amended by RA 8533") are kept as they
appear in the page.

### Codes

`codes/` contains a copy (with `type: code`) of the following instruments, which are also present
in their own series directory: Civil Code (RA 386), Revised Penal Code (Act 3815), Labor Code
(PD 442, LawPhil "as amended" text), Family Code (EO 209), Administrative Code of 1987 (EO 292),
National Internal Revenue Code of 1997 (RA 8424, as enacted), Local Government Code (RA 7160),
Revised Corporation Code (RA 11232), Intellectual Property Code (RA 8293), Customs Modernization
and Tariff Act (RA 10863), Omnibus Election Code (BP 881), Child and Youth Welfare Code (PD 603),
Insurance Code (PD 612; and RA 10607 amending it), Property Registration Decree (PD 1529),
Water Code (PD 1067), Code on Sanitation (PD 856), Revised Forestry Code (PD 705), Code of Muslim Personal Laws (PD 1083), Fisheries Code (RA 8550),
Securities Regulation Code (RA 8799), Cooperative Codes (RA 6938, RA 9520), Comprehensive Agrarian
Reform Law (RA 6657), Agricultural Land Reform Code (RA 3844), Mining Act (RA 7942), and the Act
on Crimes against International Humanitarian Law (RA 9851). The Code of Commerce of 1885
(Spanish-era, extended to the Philippines in 1888) is not available as a statute page on LawPhil
and is not included; neither is the National Building Code (PD 1096), which LawPhil does not list.

### Executive Orders and "force of law"

All Executive Orders listed by LawPhil are included, from the American Governors-General (1901)
to the present. Only some have the force of statute: those issued by President Corazon Aquino
between 25 February 1986 and 26 July 1987 while she exercised legislative power (Freedom
Constitution Art. II s.1; 1987 Constitution Art. XVIII s.6 — e.g. the Family Code, EO 209, and the
Administrative Code, EO 292) carry a `note` saying so; certain Marcos-era EOs issued under
Amendment No. 6 to the 1973 Constitution also have legislative force but are not flagged. The
remaining EOs are executive issuances (administrative acts of the President). Users should not
assume that every EO is legislation.

## Sources

- **The LawPhil Project — Arellano Law Foundation, Inc.**, https://lawphil.net — free,
  **unofficial** online library of Philippine statutes. Listings were read from the JSON API that
  LawPhil's own browse pages use (`https://lawphil.net/api/public/<series>`), and each
  instrument's HTML page was converted. Where LawPhil has no HTML page but has a PDF scan, the
  PDF's text layer was extracted with `pdftotext` (`source_format: pdf`; layout may be rough).
- **Not used:**
  - *Official Gazette* (https://www.officialgazette.gov.ph) — every request, including
    `/robots.txt`, returns an HTTP 403 Cloudflare "managed challenge" (JavaScript bot check) from
    our network (checked 2026-10-12). LawCodex does not circumvent bot challenges, so the Gazette
    could not be crawled.
  - *Supreme Court E-Library* (https://elibrary.judiciary.gov.ph) and *Congress* websites
    (congress.gov.ph, legacy.senate.gov.ph) — LawPhil already covers the same series with
    cleaner HTML and a structured listing; these were not needed.

### Copyright and licence

- Statutes, decrees and executive issuances are works of the Government of the Philippines. Under
  **Section 176.1 of the Intellectual Property Code (RA 8293)**, "no copyright shall subsist in any
  work of the Government of the Philippines" (prior approval is required only for exploitation of
  such works for profit). The legal texts in this repository are therefore free of copyright.
- LawPhil states: "The collection is licensed under a Creative Commons Attribution-NonCommercial
  4.0 Philippine license. Statutes, Issuances and Court Decisions are works of the Philippine
  Government." (https://lawphil.net/copyright.html). LawPhil has no robots.txt and its terms
  (https://lawphil.net/usepolicy.html, https://lawphil.net/disclaim.html) do not prohibit
  automated access. To respect LawPhil's licence on its *collection*, this repository is
  published **non-commercially, with attribution**: *Source: The LawPhil Project, Arellano Law
  Foundation, Inc. (https://lawphil.net)*. Anyone wishing to reuse the compilation commercially
  should either rely on the public-domain status of the underlying government texts or contact
  the Arellano Law Foundation.
- LawPhil disclaims any warranty as to accuracy or completeness; so does LawCodex.

## Not covered / gaps

- Instruments listed by LawPhil but with no text (HTML page missing — HTTP 404 — and no usable
  PDF): 32 Republic Acts (e.g. RA 80, 135, 143, 156, 320, 12326 [image-only PDF]),
  85 Batas Pambansa (BP 1–87 of 1978–79 and a few others have no text on LawPhil),
  2 Presidential Decrees, 118 Executive Orders (mostly 1901–1913 and 1941), 80 Acts. The
  full list is produced by `ph_convert.py` as `missing.tsv` in the raw directory.
- Numbers not listed at all by LawPhil (approximate count of gaps in the numbering): ~300
  Republic Acts (e.g. RA 427–436 and other short runs; many are private franchise or
  citizenship acts), ~260 Presidential Decrees (and PD 1914–2036 of 1984–86, which LawPhil does
  not list), ~140 Acts. The Official Gazette, which might fill some gaps, is behind a Cloudflare
  bot challenge (see above).
- Some LawPhil pages contain only a cross-reference or "The text of this statute is not
  included in this publication" (e.g. some General Appropriations Acts); they are reproduced as is.
- Where the source page has no "Section N." labels (e.g. some PDs numbered "1.", "2."), no
  provision headings could be generated; the text is still complete.

- Implementing Rules and Regulations (IRRs), vetoes and other non-statute entries that appear in
  LawPhil's Republic Acts listing (skipped).
- Proclamations, Administrative Orders, Memorandum Orders/Circulars, General Orders, Letters of
  Instruction, and agency issuances (secondary/executive issuances; not collected).
- Treaties, court rules (Rules of Court) and jurisprudence.
- Consolidated "as amended" versions (none exist officially).
- Filipino-language versions.

## Regenerating

```sh
python3 -m venv .venv && .venv/bin/pip install -r scripts/requirements.txt   # + poppler (pdftotext)
.venv/bin/python scripts/ph_fetch.py      # lists + downloads into ../_raw/ph/ (cached, polite: 3 workers)
.venv/bin/python scripts/ph_convert.py    # writes the Markdown tree into the repository
```

`ph_fetch.py --relist` refreshes the listings to pick up new instruments. Retrieved: 2026-10-12.
