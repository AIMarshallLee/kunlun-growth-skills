# Kunlun Growth Skills Extension (v1.1.0)

This Gemini CLI extension provides **10 production-tested Agent Skills** created by **Kunlun Growth** ([https://kunlungrowth.com](https://kunlungrowth.com)).

## Bundled Agent Skills
1. **excel-spreadsheet-master** — End-to-end spreadsheet auditing, data cleaning, formula engineering, pivot table design, and chart selection.
2. **self-improving-agent** — Structured 4-category agent memory bank (`success`, `failure`, `preference`, `domain`) with conflict resolution, anti-dogma guardrails, and local read-only audit script (`scripts/memory_audit.py`).
3. **word-document-master** — Structural `.docx` diagnostics (`scripts/docx_probe.py`), style rebuilding, mail merge, review/comment extraction, and PDF export workflows.
4. **presentation-deck-master** — Audience-driven slide deck architecture, 60-30-10 design tokens, zero-dependency HTML/PPTX delivery, and automated quality auditing (`scripts/deck_audit.py`).
5. **resume-cv-architect** — Two-sided resume engineering for recruiters and candidates with 3 read-only Python scripts.
6. **mindmap-architect** — Turn notes, meetings, or topics into MECE-compliant mind maps delivered in Markdown, Mermaid, and interactive single-file HTML (`scripts/build_mindmap.py`).
7. **ai-workflow-diagnosis** — 5-dimension AI opportunity scoring matrix, conservative ROI estimation, human-in-the-loop boundaries, and 4-week pilot planning.
8. **multilingual-translator** — 4-step MTPE localization pipeline: glossary lock, tone calibration, format/placeholder preservation, and bilingual QA.
9. **academic-paper-reader** — 3-tier paper reading (Skim / Guided / Deep-dive) with `{page, section}` provenance anchors and n-gram verification scripts.
10. **human-prose-editor** — Material-sufficiency gate and AI-filler removal for authentic long-form writing (`scripts/check_prose.py`).

## Operating Guidelines
- Prefer running the bundled read-only Python audit scripts before modifying user files.
- Never fabricate metrics, credentials, citations, or personal data; mark missing values explicitly as `[TBD]`.
- Keep all file modifications non-destructive (output cleaned/edited copies rather than overwriting originals).

For support, enterprise customization, or API services: **dasean@yeah.net** | **https://kunlungrowth.com**
