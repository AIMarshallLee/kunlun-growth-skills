---
name: multilingual-translator
version: 2.0.6
author: Kunlun Growth
license: MIT
description: Engineering-grade multilingual translation and localization workflow (MTPE). Builds a bilingual glossary and tone calibration profile first, translates while preserving formatting/code/placeholders ({name}, %s, Markdown), and runs a 4-point bilingual QA checklist. Activate when users ask to translate technical docs, business emails, product copy, UI strings, or localize content across languages.
---

# Multilingual Translator & Localization Master

> Upgrade "paste into a translator" into a controllable, repeatable localization pipeline for technical documentation, business correspondence, SaaS UI, and marketing copy.

## 1. Four-Step Translation Pipeline

1. **Build Glossary First:** Extract proper nouns, brand names, and domain terms; lock source-to-target equivalents and forbidden translations before translating body text.
2. **Calibrate Tone & Register:** Explicitly define register (Formal / Technical / Conversational / Marketing) and prevent unprompted filler or overly stiff phrasing.
3. **Format-Preserving Translation:** Keep Markdown structure, tables, code blocks, URLs, and interpolation placeholders (`{name}`, `{{var}}`, `%s`, `$1`) 100% intact.
4. **Bilingual QA Checklist:** Verify every segment against 4 checks: terminology consistency, proper nouns/numbers, active vs. passive voice naturalness, and zero untranslated or hallucinated clauses.

## 2. Glossary Template

| Source Term | Approved Target | Forbidden Translation | Context |
|---|---|---|---|
| onboarding | onboarding / user setup | boarding | SaaS / HR docs |
| churn rate | churn rate | turnover noise | Analytics |
| SLA | SLA (Service Level Agreement) | (keep acronym) | Contracts |

## 3. Quality Guardrails

- **Never alter numbers, units, or currency symbols** unless localization conversion is explicitly requested.
- **Never translate code identifiers, CLI flags, or JSON keys** inside technical blocks.
- **Flag ambiguity:** If a source sentence is ambiguous, deliver the best translation and note `[Translator Note: ...]` separately.
