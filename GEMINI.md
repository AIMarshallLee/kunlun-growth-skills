# Kunlun Growth Skills Extension

This Gemini CLI extension provides 7 production-tested Agent Skills created by **Kunlun Growth** ([https://kunlungrowth.com](https://kunlungrowth.com)).

## Bundled Agent Skills
1. **excel-spreadsheet-master** — End-to-end spreadsheet auditing, data cleaning, formula engineering, pivot table design, and chart selection.
2. **self-improving-agent** — Structured 4-category agent memory bank (`success`, `failure`, `preference`, `domain`) with conflict resolution, anti-dogma guardrails, and local read-only audit script (`scripts/memory_audit.py`).
3. **word-document-master** — Structural `.docx` diagnostics (`scripts/docx_probe.py`), style rebuilding, mail merge, review/comment extraction, and PDF export workflows.
4. **presentation-deck-master** — Audience-driven slide deck architecture, 60-30-10 design tokens, zero-dependency HTML/PPTX delivery, and automated quality auditing (`scripts/deck_audit.py`).
5. **resume-cv-architect** — Two-sided resume engineering for recruiters (JD parsing, must-have filtering, 5-dimension weighted scoring) and candidates (STAR quantification, AI-cliche removal, ATS compliance) with 3 read-only Python scripts.
6. **mindmap-architect** — Turn notes, meetings, or topics into MECE-compliant mind maps delivered in Markdown, Mermaid, and interactive single-file HTML (`scripts/build_mindmap.py`).
7. **ai-workflow-diagnosis** — 5-dimension AI opportunity scoring matrix, conservative ROI estimation, human-in-the-loop boundaries, and 4-week pilot planning.

## Operating Guidelines
- Prefer running the bundled read-only Python audit scripts before modifying user files.
- Never fabricate metrics, credentials, or personal data; mark missing values explicitly as `[TBD]`.
- Keep all file modifications non-destructive (output cleaned/edited copies rather than overwriting originals).

For support, enterprise customization, or API services: **dasean@yeah.net** | **https://kunlungrowth.com**
