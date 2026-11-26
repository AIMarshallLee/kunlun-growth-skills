---
name: self-improving-agent
version: 2.0.7
author: Kunlun Growth
license: MIT
description: Engineering-grade AI Agent self-improvement and structured memory system. Captures reusable lessons across four categories (success, failure, preference, domain), enforces anti-dogma and recurrence thresholds (>=2 occurrences), resolves conflicts with evidence-based precedence, and blocks credential/PII leaks using the bundled read-only script scripts/memory_audit.py. Activate when users ask to remember preferences, conduct post-mortems, avoid repeating mistakes, or maintain an agent memory bank.
---

# Self-Improving Agent Engine

> Making an AI agent smarter over time is not about dumping raw chat logs into prompts. It requires a **4-category structured memory bank + recurrence denoising + evidence-based conflict resolution + hard privacy/secret blocking**.

## 1. Scope & Hard Red Lines

| Dimension | Policy |
|---|---|
| **Use Cases** | Persisting user formatting/tone preferences across sessions, capturing root causes of recurring errors, recording domain definitions, and pre-task pitfall retrieval. |
| **Never Persist (Red Lines)** | 1. **Credentials & PII:** API keys, `sk-`/`ghp_`/`Bearer` tokens, passwords, phone numbers, national IDs, or unmasked personal emails. 2. **One-Off Glitches:** Single transient network hiccups (failures require `occurrences >= 2` to promote). 3. **Unbounded Dogma:** Absolute slogans like "never use X" or "always do Y" without scope conditions. |
| **Storage Scope** | Local Markdown memory bank (`./memory_bank/`), audited via `scripts/memory_audit.py` before writing. |

## 2. Triggers & Precedence Order

1. **Explicit User Correction (Highest Priority):** *"Keep weekly reports under 300 words"* -> Record immediately under `preferences/`.
2. **Explicit Post-Mortem:** *"Remember this pitfall"* / *"Save this workflow"* -> Record under `failures/` or `successes/`.
3. **Pre-Task Retrieval:** Before starting complex tasks, match trigger keywords against the memory bank and inform the user which prior lessons apply.
4. **Post-Task Reflection:** Only persist genuinely reusable patterns or corrections; never log trivial small talk.
5. **Periodic Audit:** Run `python3 scripts/memory_audit.py --dir ./memory_bank --pretty` to detect duplicates, missing fields, or secret leaks.

**Conflict Resolution Precedence:**
`Explicit User Rule (3*)` > `Live User Correction (2*)` > `Verified Success Pattern (2*)` > `Recurring Failure (>=2x, 1*)` > `Default Assumption (1*)`.
When new evidence contradicts an older entry, overwrite with evidence or mark the old entry `deprecated`.

## 3. Memory Entry Contract

Every memory entry must include **4 required fields**:
- **Scenario:** When/where this applies.
- **Action / Lesson:** Concrete rule, fix, or workflow (with applicability conditions).
- **Result:** Verified outcome.
- **Triggers:** Comma-separated keywords for retrieval.

## 4. Local Read-Only Audit Script (`scripts/memory_audit.py`)

Zero third-party dependencies (Python standard library only). Always validate before persisting:

```bash
# 1. Validate a candidate memory entry before writing
python3 scripts/memory_audit.py --text "## Concise Weekly Report
- Scenario: Generating Friday team status updates
- Action / Lesson: Limit to 3 bullet points under 40 words each when reporting to leadership
- Result: Approved on first review
- Triggers: weekly report, status update, summary" --pretty

# 2. Audit a single memory file
python3 scripts/memory_audit.py --file ./memory_bank/preferences/reporting.md --pretty

# 3. Scan an entire memory bank for duplicates (similarity >= 0.72) and PII/secret leaks
python3 scripts/memory_audit.py --dir ./memory_bank --pretty
```

## 5. Standard Error Codes & Fallback

| Code | Trigger | Exit | Resolution |
|---|---|---|---|
| **E01** | Missing or conflicting `--text` / `--file` / `--dir` | `2` | Pass exactly one input mode. |
| **E02** | Target file or directory not found | `3` | Verify path or initialize the 4 memory subdirectories. |
| **E03** | Non-UTF-8 encoding or malformed file | `4` | Convert to UTF-8 Markdown and retry. |
| **E04** | Empty input or no `.md` files found | `5` | Provide at least one structured entry. |
| **E05** | **Privacy/Secret Red Line:** Detected API key, token, phone, ID, or email | `6` | Strip sensitive strings and replace with placeholders like `<API_KEY_ENV>` before saving. |
| **E06** | Restricted environment (cannot execute Python) | — | **Fallback:** Output the 4-field Markdown card directly in chat for user review; never drop lessons silently. |
