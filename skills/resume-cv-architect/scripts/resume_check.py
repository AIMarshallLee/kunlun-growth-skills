#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""resume_check.py — Read-only resume length, quantification, ATS, and compliance checker.

Checks:
  1. Length/page budget vs. years of experience (<3 yrs: 1p / 3-8 yrs: <=2p / >8 yrs: <=3p)
  2. Action-verb bullet openings & metric quantification rate
  3. ATS compatibility (flags Markdown tables / raw HTML layout tags)
  4. Generic "Self Evaluation / Objective" fluff detection
  5. Recruiting compliance red-line scan (age, marital status, gender, protected classes)

Usage:
  python3 scripts/resume_check.py --file my_resume.md --years 4 --pretty
  python3 scripts/resume_check.py --text "- Led API migration..." --years 3 --pretty
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

WEAK_VERBS_EN = ("responsible for", "assisted with", "helped with", "participated in", "worked on", "duties included")
WEAK_VERBS_ZH = ("负责", "参与", "协助", "配合", "进行", "开展")
NUMBER_PAT = re.compile(r"\d+(?:\.\d+)?\s*(?:%|x|k|m|b|ms|s|hrs?|hours?|days?|wks?|weeks?|mos?|months?|yrs?|years?|users?|clients?|万|千|亿|人|家|次|天|小时|倍|元|分钟|个月|年)?", re.I)
FORBIDDEN_BIAS_WORDS = (
    "marital status", "unmarried", "married", "date of birth", "age:", "gender:", "religion:",
    "未婚", "已婚", "已育", "未育", "限男性", "限女性", "只招男", "只招女", "本地户口", "星座", "属相",
)


def fail(code: str, message: str, hint: str, exit_code: int) -> None:
    print(json.dumps({
        "status": "ERROR",
        "error_code": code,
        "message": message,
        "fix_hint": hint,
    }, ensure_ascii=False, indent=2))
    sys.exit(exit_code)


def check_resume(text: str, years: float) -> dict[str, Any]:
    stripped = text.strip()
    if len(stripped) < 40:
        fail("E04", "Resume text too short (< 40 chars) to evaluate.", "Provide full resume text.", 5)

    is_cjk = len(re.findall(r"[\u4e00-\u9fff]", stripped)) > len(stripped) * 0.2
    if years < 3:
        max_chars = 1800 if is_cjk else 4500
        rec_pages = "1 page"
    elif years <= 8:
        max_chars = 3400 if is_cjk else 8500
        rec_pages = "<= 2 pages"
    else:
        max_chars = 5000 if is_cjk else 12000
        rec_pages = "<= 3 pages"

    char_count = len(re.sub(r"\s+", "", stripped))
    bullets = [re.sub(r"^[-*•]\s*", "", ln.strip()) for ln in stripped.splitlines() if re.match(r"^\s*[-*•]\s+\S", ln)]
    quantified = [b for b in bullets if re.search(r"\d", b) and NUMBER_PAT.search(b)]
    weak_starts = [
        b[:32] for b in bullets
        if any(b.lower().startswith(v) for v in WEAK_VERBS_EN) or any(b.startswith(v) for v in WEAK_VERBS_ZH)
    ]

    has_md_table = bool(re.search(r"^\s*\|.+\|\s*$", stripped, re.M))
    has_html = bool(re.search(r"<(table|div|img|span)\b", stripped, re.I))
    has_self_eval = bool(re.search(r"^(?:#+\s*)?(自我评价|个人评价|objective|personal statement)\b", stripped, re.M | re.I))
    lower_stripped = stripped.lower()
    bias_hits = [w for w in FORBIDDEN_BIAS_WORDS if w in lower_stripped]

    issues: list[dict[str, str]] = []
    if char_count > max_chars:
        issues.append({"severity": "WARN", "code": "W_TOO_LONG", "detail": f"Content length ({char_count} non-space chars) exceeds {max_chars} recommended for {years} yrs ({rec_pages})."})
    if bullets:
        q_rate = round(len(quantified) / len(bullets) * 100, 1)
        if q_rate < 50.0:
            issues.append({"severity": "WARN", "code": "W_LOW_QUANTIFICATION", "detail": f"Quantification rate is {q_rate}% ({len(quantified)}/{len(bullets)}). Add baseline-to-result metrics using STAR."})
    else:
        q_rate = 0.0
        issues.append({"severity": "WARN", "code": "W_NO_BULLETS", "detail": "No bullet points (- or *) detected; dense paragraphs hurt 15–40s recruiter scanning."})
    if weak_starts:
        issues.append({"severity": "WARN", "code": "W_WEAK_VERBS", "detail": f"{len(weak_starts)} bullet(s) start with passive/weak phrasing (e.g., 'Responsible for'); replace with action verbs like Built, Reduced, Led."})
    if has_md_table or has_html:
        issues.append({"severity": "WARN", "code": "W_ATS_RISK", "detail": "Markdown tables or HTML layout tags detected; many ATS parsers drop fields inside tables. Use clean linear sections."})
    if has_self_eval:
        issues.append({"severity": "INFO", "code": "I_SELF_EVAL", "detail": "Generic 'Objective / Personal Statement' section detected; consider replacing with a 2-line impact summary."})
    if bias_hits:
        issues.append({"severity": "FAIL", "code": "E05_COMPLIANCE_REDLINE", "detail": f"Compliance red-line terms detected: {bias_hits}. Remove protected-class attributes immediately."})

    has_fail = any(i["severity"] == "FAIL" for i in issues)
    status = "FAIL" if has_fail else ("WARN" if issues else "PASS")
    return {
        "status": status,
        "error_code": "E05" if has_fail else None,
        "metrics": {
            "non_space_chars": char_count,
            "recommended_pages": rec_pages,
            "recommended_max_chars": max_chars,
            "bullet_count": len(bullets),
            "quantified_bullets": len(quantified),
            "quantification_rate_pct": q_rate,
            "weak_verb_bullets": len(weak_starts),
            "ats_table_or_html_risk": has_md_table or has_html,
        },
        "issues": issues,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Read-only resume layout, quantification & compliance checker.")
    ap.add_argument("--file", help="Path to resume (.md / .txt)")
    ap.add_argument("--text", help="Inline resume plain text")
    ap.add_argument("--years", type=float, default=3.0, help="Relevant years of experience (default: 3.0)")
    ap.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    args = ap.parse_args()

    if args.years < 0 or args.years > 50:
        fail("E04", f"Years of experience out of range (0..50): {args.years}", "Pass a value between 0 and 50.", 5)
    if not args.file and not args.text:
        fail("E01", "Missing --file or --text argument.", "Example: python3 scripts/resume_check.py --file resume.md --years 3 --pretty", 2)

    if args.text is not None:
        raw = args.text
    else:
        p = Path(args.file).expanduser()
        if not p.exists() or not p.is_file():
            fail("E02", f"Resume file not found: {p}", "Verify the path and retry.", 3)
        if p.suffix.lower() not in {".md", ".txt"}:
            fail("E03", f"Only .md/.txt plain text is supported directly (got {p.suffix}).", "Extract text from PDF/DOCX into .md/.txt or pass via --text.", 4)
        raw = p.read_text(encoding="utf-8", errors="replace")

    res = check_resume(raw, args.years)
    print(json.dumps(res, ensure_ascii=False, indent=2 if args.pretty else None))
    if res["status"] == "FAIL":
        sys.exit(6)


if __name__ == "__main__":
    main()
