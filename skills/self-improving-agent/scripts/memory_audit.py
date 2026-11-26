#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""memory_audit.py — Read-only audit script for AI Agent memory banks (zero third-party dependencies).

Checks:
  1. Required 4 fields (Scenario / Action or Lesson / Result / Triggers)
  2. Anti-dogma guardrail (unbounded absolutes like 'never', 'always', '100%' without scope)
  3. Privacy & credential leak blocking (API keys, tokens, phones, national IDs, emails)
  4. Recurrence denoising (failure lessons should note >= 2 occurrences before promotion)
  5. Duplicate / conflict detection across directory scans (title similarity >= 0.72)

Usage:
  python3 scripts/memory_audit.py --text "## Entry Title..." --pretty
  python3 scripts/memory_audit.py --file ./memory_bank/pref.md --pretty
  python3 scripts/memory_audit.py --dir ./memory_bank --pretty
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from pathlib import Path
from typing import Any

FIELD_GROUPS = [
    ("Scenario", ("scenario", "场景")),
    ("Action / Lesson", ("action", "lesson", "做法", "教训")),
    ("Result", ("result", "结果")),
    ("Triggers", ("triggers", "trigger", "触发词")),
]

DOGMA_WORDS_EN = ("never", "always", "100%", "without exception", "must always")
DOGMA_WORDS_ZH = ("永远", "绝不", "绝对", "一律", "必须始终")

SECRET_PATTERNS = [
    ("API_KEY_OR_TOKEN", re.compile(r"\b(sk-[A-Za-z0-9]{12,}|skh_[A-Za-z0-9]{10,}|ghp_[A-Za-z0-9]{16,}|gho_[A-Za-z0-9]{16,}|Bearer\s+[A-Za-z0-9._\-]{12,})")),
    ("PHONE_CN", re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)")),
    ("ID_CARD_CN", re.compile(r"(?<!\d)\d{17}[\dXx](?!\d)")),
    ("EMAIL", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),
]


def fail(code: str, message: str, hint: str, exit_code: int) -> None:
    print(json.dumps({
        "status": "FAIL",
        "error_code": code,
        "message": message,
        "fix_hint": hint,
    }, ensure_ascii=False, indent=2))
    sys.exit(exit_code)


def audit_entry(text: str, source_name: str = "inline") -> dict[str, Any]:
    if not text.strip():
        return {"source": source_name, "status": "FAIL", "issues": [{"severity": "FAIL", "code": "E04", "detail": "Memory entry is empty."}]}

    issues: list[dict[str, str]] = []
    lower_text = text.lower()

    # 1. Required fields
    missing = []
    for label, aliases in FIELD_GROUPS:
        if not any(alias in lower_text for alias in aliases):
            missing.append(label)
    if missing:
        issues.append({"severity": "WARN", "code": "W_MISSING_FIELDS", "detail": f"Missing required fields: {', '.join(missing)}"})

    # 2. Dogmatism check
    dogma_hits = [w for w in DOGMA_WORDS_EN if re.search(rf"\b{re.escape(w)}\b", lower_text)] + [w for w in DOGMA_WORDS_ZH if w in text]
    has_scope = any(k in lower_text for k in ("scenario", "when ", "only if", "except", "适用", "仅当", "场景"))
    if dogma_hits and not has_scope:
        issues.append({"severity": "WARN", "code": "W_DOGMA_ABSOLUTE", "detail": f"Unbounded absolute wording {dogma_hits} detected without applicability scope."})
    elif dogma_hits:
        issues.append({"severity": "INFO", "code": "I_ABSOLUTE_WORD", "detail": f"Strong constraint words {dogma_hits} found; verify scope conditions are explicit."})

    # 3. Privacy & Secret check (HARD FAIL)
    for label, pat in SECRET_PATTERNS:
        if pat.search(text):
            issues.append({"severity": "FAIL", "code": "E05_SECRET_OR_PII", "detail": f"Potential sensitive PII/credential detected ({label}). Strip and replace with a placeholder before saving."})

    # 4. De-noising check for failure memories
    is_failure = any(k in lower_text for k in ("failure", "error", "pitfall", "bug", "失败", "报错", "踩坑"))
    has_recurrence = re.search(r"(occurrences|reproduced|seen)\s*[:：=]?\s*[2-9]\d*|(复现|出现|发生)\s*[2-9]\d*\s*次", lower_text)
    if is_failure and not has_recurrence:
        issues.append({"severity": "INFO", "code": "I_SINGLE_FAILURE_PENDING", "detail": "Failure lessons should document >= 2 occurrences before promotion to avoid one-off noise."})

    title_m = re.search(r"^#+\s*(.+)$", text, re.M)
    title = title_m.group(1).strip() if title_m else source_name
    trig_m = re.search(r"(?:Triggers?|触发词)\s*[:：]\s*(.+)$", text, re.M | re.I)
    triggers = trig_m.group(1).strip() if trig_m else ""

    has_fail = any(i["severity"] == "FAIL" for i in issues)
    status = "FAIL" if has_fail else ("WARN" if any(i["severity"] == "WARN" for i in issues) else "PASS")
    return {
        "source": source_name,
        "title": title,
        "triggers": triggers,
        "status": status,
        "issues": issues,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Read-only audit script for AI Agent memory banks.")
    ap.add_argument("--file", help="Path to a single Markdown memory file")
    ap.add_argument("--dir", help="Path to memory bank directory (scans all .md files)")
    ap.add_argument("--text", help="Inline Markdown memory entry text")
    ap.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    args = ap.parse_args()

    provided = sum(1 for x in (args.file, args.dir, args.text) if x is not None)
    if provided == 0:
        fail("E01", "Missing input: provide one of --text, --file, or --dir.", "Example: python3 scripts/memory_audit.py --text \"## Entry...\" --pretty", 2)
    if provided > 1:
        fail("E01", "Pass only one of --text, --file, or --dir.", "Keep a single input flag.", 2)

    results: list[dict[str, Any]] = []
    if args.text is not None:
        results.append(audit_entry(args.text, "inline_text"))
    elif args.file is not None:
        p = Path(args.file).expanduser()
        if not p.exists() or not p.is_file():
            fail("E02", f"File not found: {p}", "Verify the file path and retry.", 3)
        results.append(audit_entry(p.read_text(encoding="utf-8"), p.name))
    else:
        d = Path(args.dir).expanduser()
        if not d.exists() or not d.is_dir():
            fail("E02", f"Directory not found: {d}", "Verify the memory bank directory path.", 3)
        md_files = sorted(d.rglob("*.md"))
        if not md_files:
            fail("E04", f"No .md files found in {d}", "Add at least one structured Markdown memory entry.", 5)
        for mf in md_files[:200]:
            results.append(audit_entry(mf.read_text(encoding="utf-8", errors="replace"), mf.relative_to(d).as_posix()))

    conflicts: list[dict[str, Any]] = []
    if len(results) > 1:
        for i in range(len(results)):
            for j in range(i + 1, len(results)):
                sim = difflib.SequenceMatcher(None, results[i]["title"], results[j]["title"]).ratio()
                if sim >= 0.72:
                    conflicts.append({
                        "entry_a": results[i]["source"],
                        "entry_b": results[j]["source"],
                        "title_similarity": round(sim, 2),
                        "hint": "High title similarity; review and merge older entry with newer evidence.",
                    })

    any_fail = any(r["status"] == "FAIL" for r in results)
    any_warn = any(r["status"] == "WARN" for r in results) or bool(conflicts)
    out = {
        "status": "FAIL" if any_fail else ("WARN" if any_warn else "PASS"),
        "error_code": "E05" if any_fail else None,
        "checked_count": len(results),
        "entries": results,
        "potential_conflicts": conflicts,
    }
    print(json.dumps(out, ensure_ascii=False, indent=2 if args.pretty else None))
    if any_fail:
        sys.exit(6)


if __name__ == "__main__":
    main()
