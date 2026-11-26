---
name: human-prose-editor
version: 1.0.0
author: Kunlun Growth
license: MIT
description: Edit or write long-form articles, essays, newsletters, and technical posts so they sound like a real human with firsthand specifics—not generic AI filler. Enforces material-sufficiency checks (>=5 concrete facts/examples before drafting long-form) and runs scripts/check_prose.py to catch AI-sounding padding and structural repetition. Activate when users ask to humanize writing, remove AI tone, or draft authentic essays/posts.
---

# Human-Prose Editor

> Authenticity does not come from slang, typos, or forced casualness. It comes from **concrete source material**, a **clear speaker stance**, and **natural rhythm**.

## 1. Gate 1: Material Sufficiency Check (Before Outlining)

Never pad a 1,200-word article out of 3 abstract bullet points by repeating "benefits, significance, risks, and future" across 10 paragraphs.
- **Non-fiction / Essays:** List at least **5 concrete, verifiable materials** (user-provided experiences, real metrics, specific product flows, documented cases, or direct quotes) forming a real progression before drafting long-form.
- **If materials are insufficient:** Ask up to 3 focused questions, or research verifiable public facts first. If neither is permitted, deliver a tight ~400-word brief rather than padding with generic filler.
- **Never invent personal anecdotes** (*"For example, a friend of mine..."*) in non-fiction work.

## 2. Writing & Editing Principles

1. **Specifics Over Adjectives:** Replace *"significantly improved efficiency"* with *"cut weekly reconciliation from 3 hours to 20 minutes."*
2. **Earn Your Transitions:** Avoid formulaic AI connectors (*"In today's fast-paced world"*, *"Moreover, it is worth noting that"*, *"In conclusion, by leveraging..."*).
3. **Vary Sentence Cadence:** Mix short punchy judgements with detailed explanations; allow occasional natural asides that return cleanly to the main point.
4. **Honest Boundaries:** State what you observed directly vs. what remains uncertain.

## 3. Local Prose Check Script (`scripts/check_prose.py`)

```bash
python3 scripts/check_prose.py --help
```

Use `scripts/check_prose.py` after drafting to flag repetitive sentence openings, abstract buzzword density, and padding patterns before final delivery.
