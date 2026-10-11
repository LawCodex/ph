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
| Constitutions (1987 in force; 1986, 1973, 1943, 1935, 1899 historical) | `constitution/` | 6 |
<!-- /COUNTS -->

## Structure

```
constitution/<year>-<name>.md
codes/<code-slug>.md                         # copies of the main codes, type: code
republic-acts/<year>/ra-<n>-<slug>.md        # Republic Acts, 1946–present (Congress)
commonwealth-acts/<year>/ca-<n>-<slug>.md    # Commonwealth Acts, 1935–1946 (National Assembly / Congress)
batas-pambansa/<year>/bp-<n>-<slug>.md       # Batas Pambansa, 1978–1985 (Interim / Regular Batasang Pambansa)
presidential-decrees/<year>/pd-<n>-<slug>.md # Presidential Decrees, 1972–1986 (Marcos, martial law legislation)
executive-orders/<year>/eo-<n>-<slug>.md     # Executive Orders, 1901–present
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
tables when simple and as plain HTML otherwise.

### Codes

`codes/` contains a copy (with `type: code`) of the following instruments, which are also present
in their own series directory: Civil Code (RA 386), Revised Penal Code (Act 3815), Labor Code
(PD 442, LawPhil "as amended" text), Family Code (EO 209), Administrative Code of 1987 (EO 292),
National Internal Revenue Code of 1997 (RA 8424, as enacted), Local Government Code (RA 7160),
Revised Corporation Code (RA 11232), Intellectual Property Code (RA 8293), Customs Modernization
and Tariff Act (RA 10863), Omnibus Election Code (BP 881), Child and Youth Welfare Code (PD 603),
Insurance Code (PD 612; and RA 10607 amending it), Property Registration Decree (PD 1529),
Water Code (PD 1067), Code on Sanitation (PD 856), Revised Forestry Code (PD 705), National
Building Code (PD 1096), Code of Muslim Personal Laws (PD 1083), Fisheries Code (RA 8550),
Securities Regulation Code (RA 8799), Cooperative Codes (RA 6938, RA 9520), Comprehensive Agrarian
Reform Law (RA 6657), Agricultural Land Reform Code (RA 3844), Mining Act (RA 7942), and the Act
on Crimes against International Humanitarian Law (RA 9851). The Code of Commerce of 1885
(Spanish-era, extended to the Philippines in 1888) is not available as a statute page on LawPhil
and is not included.

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

## Not covered

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
