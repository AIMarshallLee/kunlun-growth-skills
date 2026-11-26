---
name: academic-paper-reader
version: 1.0.0
author: Kunlun Growth
license: MIT
description: Three-tier academic paper reading workflow (Skim / Guided / Deep-dive) with page-and-section provenance anchors, multi-paper dimension-major comparison, and automated n-gram anti-hallucination verification via bundled scripts (parse_pdf.py, fetch_arxiv_tex.py, verify_provenance.py, render_report.py). Activate when users want to read, summarize, compare, or verify claims in research papers or arXiv preprints.
---

# Academic Paper Reader

> Built for researchers, graduate students, and AI engineers: **3 reading depths + page-level provenance anchors + multi-paper comparison + n-gram hallucination auditing**.

## 1. Scope & Safety Boundaries

- **What It Does:** Single-paper Skim (6 core fields with `{page, section}` anchors), Guided reading aligned to your research direction, Deep-dive Q&A with verbatim excerpts + critical analysis, and 2–10 paper dimension-major comparison.
- **What It Does NOT Do:** No generic web scraping (only `arxiv.org` TeX/PDF via `fetch_arxiv_tex.py` or user-provided local `.pdf` / pasted text), no OCR on scanned image-only PDFs, and no fabricated citations.
- **Security:** Only reads explicit user-provided paper paths; outputs reports only when requested.

## 2. Three Reading Depths (Auto-Selected)

| Depth | Trigger Condition | Output |
|---|---|---|
| **Skim** | Paper only | 6 anchored fields (`research_question`, `method`, `dataset`, `key_results`, `contributions`, `limitations`) + 1-sentence plain summary + 3 follow-up questions |
| **Guided** | User provides `my_direction` | Adds 3–7 evidence-backed `connection_points` showing how this paper applies to your work |
| **Deep-dive** | User provides `specific_question` | Adds verbatim excerpts (`page + section + text`) + 3-part critical analysis (`agree / question / complement`) |

## 3. Bundled Local Scripts (`scripts/`)

```bash
# 1. Fetch arXiv TeX source (falls back to PDF if needed)
python3 scripts/fetch_arxiv_tex.py --help

# 2. Parse a local PDF into (text, page, section) triples
python3 scripts/parse_pdf.py --help

# 3. Audit generated claims against source text with 3-gram/5-gram provenance matching
python3 scripts/verify_provenance.py --help

# 4. Render structured reading report (HTML / Markdown / PDF)
python3 scripts/render_report.py --help
```

*(Note: `parse_pdf.py` / `fetch_arxiv_tex.py` use optional packages like `pdfplumber`/`pymupdf`/`arxiv` if installed; pasted text works with zero external dependencies.)*

## 4. Anti-Hallucination Rules

- **Every core claim must cite `{page, section}`.**
- **If the paper does not address a question, state `"Not mentioned in the source text"`**—never extrapolate.
- **Multi-paper comparisons must be dimension-major** (`Dimension -> Paper A / Paper B`), never paper-by-paper summaries.
