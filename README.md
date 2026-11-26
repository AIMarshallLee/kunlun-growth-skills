# Kunlun Growth Skills for Google Gemini CLI

[![Gemini CLI Extension](https://img.shields.io/badge/Gemini%20CLI-Extension-4285F4?logo=google-gemini&logoColor=white)](https://geminicli.com/docs/extensions/)
[![Version](https://img.shields.io/badge/Version-1.1.0-blue.svg)](https://github.com/AIMarshallLee/kunlun-growth-skills/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)
[![Website](https://img.shields.io/badge/Website-kunlungrowth.com-0F172A)](https://kunlungrowth.com)

A curated suite of **10 production-tested Agent Skills** adapted from Kunlun Growth's highest-adoption workflows (345,000+ cumulative community downloads) for **Google Gemini CLI**.

Built to run **100% locally** with zero telemetry.

> Looking for developer & AI engineering skills (MCP, Skill Builder, Security Guard, Code Review, API Design)? Check out our companion extension: **[kunlun-dev-skills](https://github.com/AIMarshallLee/kunlun-dev-skills)**.

---

## Installation

```bash
# Install directly from GitHub
gemini extensions install https://github.com/AIMarshallLee/kunlun-growth-skills

# Verify installation
gemini extensions list
gemini skills list

# Update to latest version
gemini extensions update kunlun-growth-skills
```

---

## Included Agent Skills (10)

| Skill | What It Does | Bundled Local Scripts |
|---|---|---|
| **excel-spreadsheet-master** | Audits dirty spreadsheets, eliminates 12 silent formula/format traps, designs Pivot Tables & charts. | — |
| **self-improving-agent** | 4-category structured memory bank with recurrence denoising and secret/PII leak blocking. | `scripts/memory_audit.py` |
| **word-document-master** | OOXML `.docx` structural diagnostics, style rebuilding, mail merge, and tracked-changes extraction. | `scripts/docx_probe.py` |
| **presentation-deck-master** | Audience-scoped slide outlining, 60-30-10 design tokens, HTML/PPTX delivery, and density auditing. | `scripts/deck_audit.py` |
| **resume-cv-architect** | Two-sided recruiting & CV workflow: JD parsing, 5-dimension scoring, STAR quantification, ATS checks. | `parse_jd.py`, `resume_check.py`, `audit_ai_flavor.py` |
| **mindmap-architect** | Converts messy notes or meetings into MECE mind maps in Markdown, Mermaid, and interactive HTML. | `scripts/build_mindmap.py` |
| **ai-workflow-diagnosis** | 5-dimension AI opportunity scoring matrix, conservative ROI formulas, and 4-week pilot plan. | — |
| **multilingual-translator** | 4-step MTPE localization pipeline: glossary lock, tone calibration, format preservation, bilingual QA. | — |
| **academic-paper-reader** | 3-tier paper reading (Skim/Guided/Deep-dive) with `{page, section}` anchors & n-gram verification. | `parse_pdf.py`, `fetch_arxiv_tex.py`, `verify_provenance.py`, `render_report.py` |
| **human-prose-editor** | Material-sufficiency gate and AI-filler removal for authentic long-form writing. | `scripts/check_prose.py` |

### Custom Slash Commands
- `/kunlun:skills` — Show all 10 bundled skills and example prompts.
- `/kunlun:diagnose` — Launch an interactive 5-dimension AI Workflow Diagnosis session.

---

## Privacy & Security

- **Local-First & Zero Telemetry:** Bundled audit scripts run locally without collecting prompts, files, or analytics. See [PRIVACY.md](./PRIVACY.md).

## Commercial Services & Support

- **Website:** [https://kunlungrowth.com](https://kunlungrowth.com)
- **Support & Enterprise Inquiries:** [dasean@yeah.net](mailto:dasean@yeah.net)
- **Issues:** [GitHub Issues](https://github.com/AIMarshallLee/kunlun-growth-skills/issues)
