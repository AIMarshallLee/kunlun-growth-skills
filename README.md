# Kunlun Growth Skills for Google Gemini CLI

[![Gemini CLI Extension](https://img.shields.io/badge/Gemini%20CLI-Extension-4285F4?logo=google-gemini&logoColor=white)](https://geminicli.com/docs/extensions/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)
[![Website](https://img.shields.io/badge/Website-kunlungrowth.com-0F172A)](https://kunlungrowth.com)

A curated suite of **7 production-tested Agent Skills** adapted from Kunlun Growth's highest-adoption workflows (280,000+ cumulative community downloads) for **Google Gemini CLI**.

Built to run **100% locally** with zero telemetry and zero external API dependencies.

---

## Installation

### Install directly from GitHub
```bash
gemini extensions install https://github.com/AIMarshallLee/kunlun-growth-skills
```

### Verify installation
```bash
gemini extensions list
```

### Update to the latest version
```bash
gemini extensions update kunlun-growth-skills
```

---

## Included Agent Skills (7)

| Skill | What It Does | Bundled Local Script (Zero-Dep Python) |
|---|---|---|
| **excel-spreadsheet-master** | Audits dirty spreadsheets, eliminates 12 silent formula/format traps (`VLOOKUP`, text-numbers, precision loss), designs Pivot Tables & charts. | — |
| **self-improving-agent** | 4-category structured memory bank (`success`, `failure`, `preference`, `domain`) with recurrence denoising and secret/PII leak blocking. | `skills/self-improving-agent/scripts/memory_audit.py` |
| **word-document-master** | OOXML `.docx` structural diagnostics, style rebuilding, mail merge, tracked-changes extraction, and media bloat checks. | `skills/word-document-master/scripts/docx_probe.py` |
| **presentation-deck-master** | Audience-scoped slide outlining, 60-30-10 design tokens, zero-dependency HTML/PPTX delivery, and automated slide density auditing. | `skills/presentation-deck-master/scripts/deck_audit.py` |
| **resume-cv-architect** | Two-sided recruiting & CV workflow: JD parsing, 5-dimension scoring, STAR quantification, ATS checks, and AI-cliche removal. | `parse_jd.py`, `resume_check.py`, `audit_ai_flavor.py` |
| **mindmap-architect** | Converts messy notes or meetings into MECE mind maps in Markdown, Mermaid, and interactive single-file HTML. | `skills/mindmap-architect/scripts/build_mindmap.py` |
| **ai-workflow-diagnosis** | 5-dimension AI opportunity scoring matrix, conservative ROI formulas, human-in-the-loop guardrails, and 4-week pilot plan. | — |

### Custom Slash Commands
- `/kunlun:skills` — Show all 7 bundled skills and example prompts.
- `/kunlun:diagnose` — Launch an interactive 5-dimension AI Workflow Diagnosis session.

---

## Quick Usage Examples

Once installed, Gemini CLI automatically activates the right skill based on your prompt:

- *"Audit this messy sales CSV and tell me why my VLOOKUP and SUM formulas are returning wrong numbers."* -> **excel-spreadsheet-master**
- *"Remember that I prefer executive summaries under 3 bullet points, and audit our memory_bank folder."* -> **self-improving-agent**
- *"Inspect report.docx for direct formatting overrides and broken heading styles."* -> **word-document-master**
- *"Create a 10-minute investor pitch deck outline and audit the slide density."* -> **presentation-deck-master**
- *"Rewrite these resume bullets using STAR metrics and check for AI cliches."* -> **resume-cv-architect**
- *"Turn these meeting notes into a Mermaid and interactive HTML mind map."* -> **mindmap-architect**
- *"Score our customer support and finance workflows to find the best 4-week AI pilot."* -> **ai-workflow-diagnosis**

---

## Privacy & Security

- **Local-First:** All scripts use Python's standard library only and make zero outbound network requests.
- **No Telemetry:** We do not collect prompts, files, or usage analytics.
- **Full Policy:** See [PRIVACY.md](./PRIVACY.md).

---

## Commercial Services & Support

These 7 core skills are open-source and free under the [MIT License](./LICENSE).

For **enterprise AI workflow consulting, custom Gemini CLI / MCP extensions, private knowledge-base deployments, or API services**, contact Kunlun Growth:

- **Website:** [https://kunlungrowth.com](https://kunlungrowth.com)
- **Support & Inquiries:** [dasean@yeah.net](mailto:dasean@yeah.net)
- **Issues & Feedback:** [GitHub Issues](https://github.com/AIMarshallLee/kunlun-growth-skills/issues)
