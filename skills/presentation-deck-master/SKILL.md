---
name: presentation-deck-master
version: 2.0.4
author: Kunlun Growth
license: MIT
description: End-to-end presentation & slide deck engineering: 5-question scoping, 8 narrative frameworks (executive review, pitch deck, training, product launch, post-mortem), 60-30-10 design tokens, zero-dependency single-file HTML deck or deck.json + python-pptx generation, and automated quality auditing via scripts/deck_audit.py. Activate when users need to create, structure, or audit a PPT, slide deck, pitch deck, or executive presentation.
---

# Presentation & Slide Deck Master

> Great presentations don't start by picking a template—they start by deciding **the one takeaway each slide leaves with the audience**. This skill enforces a 5-step pipeline: **Scope -> Outline -> Content -> Build -> Audit**.

## 1. Scope & Output Routes

| Dimension | Policy |
|---|---|
| **Scenarios** | Executive status updates, fundraising pitch decks, training workshops, annual reviews, product launches, project post-mortems, and auditing existing `.pptx` / `deck.json` / `.html` decks. |
| **Guardrails** | 1. **Never fabricate metrics**—mark missing numbers `[TBD]`. 2. **Outline before slides**—confirm slide-by-slide thesis titles before generating full slides. |
| **Two Delivery Routes** | **Route A (Default):** Zero-dependency single-file `.html` presentation (keyboard navigation, speaker notes via `S` key, print-to-PDF ready). **Route B (Editable `.pptx`):** Structured `deck.json` + `python-pptx` build script. |

## 2. Five-Question Scoping

Before outlining, establish (or state defaults for):
1. **Scenario** (e.g., Executive Review, Pitch Deck, Product Launch)
2. **Audience** (Executives, Investors, Customers, Engineers)
3. **Duration** (minutes -> target slide count = `round(minutes * 1.3)`)
4. **Visual Tone** (Executive Navy, Minimal Tech, Warm Editorial, Academic)
5. **Output Format** (`html` default or `pptx`)

## 3. Core Slide Rules

- **Thesis Titles Only:** Every slide title must be a complete insight/claim (e.g., *"APAC Retention Dropped 13% Due to Onboarding Friction"*), never a generic noun phrase (*"Sales Data"*).
- **Density Ceiling:** Max 6 lines per slide, max 3–5 bullets, concise phrasing, speaker notes <= 40 words.
- **60-30-10 Color System:** 60% neutral background, 30% structural surface/text, 10% single accent color; WCAG AA contrast >= 4.5:1.
- **Typography:** Max 2 sans-serif font families; body >= 18pt for projection readability.

## 4. Local Read-Only Deck Audit (`scripts/deck_audit.py`)

Zero third-party dependencies (Python standard library only). Supports `.json`, `.pptx`, `.html`, and `.md`:

```bash
# 1. Audit deck.json against a 10-minute talk
python3 scripts/deck_audit.py --file deck.json --minutes 10 --pretty

# 2. Audit an existing .pptx file (checks placeholders, slide count, density, notes)
python3 scripts/deck_audit.py --file presentation.pptx --minutes 15 --pretty

# 3. Pre-audit a Markdown slide outline
python3 scripts/deck_audit.py --text "## APAC Retention Dropped 13% in Q3
- Onboarding drop-off rose from 18% to 31%
Notes: Lead with the root cause before showing regional breakdown" --minutes 5 --pretty
```

## 5. Error Codes & Fallback

| Code | Trigger | Exit | Resolution |
|---|---|---|---|
| **E01** | Missing `--file` / `--text` | `2` | Provide a file path or Markdown outline. |
| **E02** | File not found | `3` | Verify path or pre-audit with `--text`. |
| **E03** | Unsupported format or parse failure | `4` | Convert legacy `.ppt` to `.pptx`; ensure `deck.json` has `slides` array. |
| **E04** | Duration outside `1..240` minutes | `5` | Pass a valid `--minutes` value. |
| **E05** | Unresolved placeholders (`Click to add`, `[TBD]`, `Lorem ipsum`) or 0 slides | `6` | Replace placeholders with real content and re-run `deck_audit.py`. |
| **E06** | `python-pptx` not installed | — | **Fallback:** Deliver Route A (zero-dependency single-file `.html`) + `deck.json`. |
