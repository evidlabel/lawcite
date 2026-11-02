---
name: lawcite
description: Use when citing Danish statutes by paragraph (§ / stk.) — fetch a law from retsinformation and emit one Hayagriva, BibTeX, or Markdown entry per provision.
---

# lawcite

Danish statute → one citable key per provision. The output format follows the `-f` extension.

## Rules
- Always pass `-f`. The default is `__temp.bib`.
- `.yaml` = Hayagriva, `.bib` = BibTeX, `.md` = plain reading.
- Keys are `<namespace>:<provision>`. A live fetch of `2024/1150` § 9 wrote `lbk2024-1150:main` for the act and `lbk2024-1150:p9stk1` for stk. 1. Override the namespace with `-n`. The default is derived from the short name (for example `lbk2024-1150`).
- A numbered item has its own key, for example `lbk2014-433:p3stk1nr1` for § 3, stk. 1, nr. 1. The stk entry keeps the items in its text.
- The API is rate-limited. Responses cache in `$LAWCITE_CACHE_DIR` (default `~/.cache/lawcite`). On a limit with a cache miss it falls back to the PDF endpoint.
- Legislation only. Guidance (vejledninger) goes through `other`.
- `-d` on `other` saves the fetched PDF content for debugging. It is not a directory flag.
- The text comes from a third-party API (`retsinformation-api.dk`), not from retsinformation.dk itself.
  Use lawcite for lookup and for the citation structure (§, stk., nr.).
  A quote comes from the official PDF keyed in evid: `evid --db evid doc add -s <set> https://www.retsinformation.dk/eli/lta/<year>/<no>/pdf`.

## Commands
    lawcite law <name|year/number> [-p 9-12] [-n <ns>] -f <out>.yaml
    lawcite other <pdf-url> [-d] -f <out>.md
Flags: `lawcite -h`, `lawcite law -h`, `lawcite other -h`.

## Examples
    lawcite law forældreansvarsloven -f fal.yaml
    lawcite law 2024/1150 -p 9,11,15a -f kl.yaml

## Install
    uv tool install git+https://github.com/evidlabel/lawcite.git

## Done
- Output is in the file named by `-f`, not `__temp.bib`.
- One provision spot-checked against the keyed retsinformation PDF.
