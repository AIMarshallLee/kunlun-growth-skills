#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""resume_check.py — 简历版式、量化表达与招聘合规红线只读体检脚本。

检查项:
  1. 篇幅/字数阈值对照工作年限（应届/<3年/3-8年/8年以上）
  2. 经历条目动词开头 + 量化数字覆盖率
  3. ATS 机器友好检查（禁止用 Markdown 表格/HTML 标签承载正文）
  4. 「个人评价」等无效空话章节提醒
  5. 招聘合规红线扫描（年龄/婚育/性别/户籍等法定禁止筛选维度）

用法:
  python3 scripts/resume_check.py --file my_resume.md --years 4 --pretty
  python3 scripts/resume_check.py --text "## 工作经历..." --years 1 --pretty
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

WEAK_VERBS = ("负责", "参与", "协助", "配合", "进行", "开展")
NUMBER_PAT = re.compile(r"\d+(?:\.\d+)?\s*(?:%|万|千|亿|人|家|次|天|小时|倍|元|w|k|ms|s|分钟|个月|年)", re.I)
FORBIDDEN_BIAS_WORDS = ("未婚", "已婚", "已育", "未育", "限男性", "限女性", "只招男", "只招女", "本地户口", "星座", "属相")


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
        fail("E04", "简历文本过短（不足 40 字），无法有效评估", "请传入完整简历正文。", 5)

    # Length expectation by seniority
    if years < 3:
        max_chars = 1800
        rec_pages = "1 页"
    elif years <= 8:
        max_chars = 3400
        rec_pages = "≤ 2 页"
    else:
        max_chars = 5000
        rec_pages = "≤ 3 页"

    char_count = len(re.sub(r"\s+", "", stripped))
    bullets = [re.sub(r"^[-*•]\s*", "", ln.strip()) for ln in stripped.splitlines() if re.match(r"^\s*[-*•]\s+\S", ln)]
    quantified = [b for b in bullets if NUMBER_PAT.search(b)]
    weak_starts = [b[:18] for b in bullets if any(b.startswith(v) for v in WEAK_VERBS)]

    has_md_table = bool(re.search(r"^\s*\|.+\|\s*$", stripped, re.M))
    has_html = bool(re.search(r"<(table|div|img|span)\b", stripped, re.I))
    has_self_eval = bool(re.search(r"^(?:#+\s*)?(自我评价|个人评价)", stripped, re.M))
    bias_hits = [w for w in FORBIDDEN_BIAS_WORDS if w in stripped]

    issues: list[dict[str, str]] = []
    if char_count > max_chars:
        issues.append({"severity": "WARN", "code": "W_TOO_LONG", "detail": f"正文 {char_count} 字，建议控制在 {max_chars} 字以内（{years} 年经验推荐 {rec_pages}）。"})
    if bullets:
        q_rate = round(len(quantified) / len(bullets) * 100, 1)
        if q_rate < 50.0:
            issues.append({"severity": "WARN", "code": "W_LOW_QUANTIFICATION", "detail": f"经历条目的数字量化率仅 {q_rate}% ({len(quantified)}/{len(bullets)})，建议用 STAR 补充规模/增幅/时长基线。"})
    else:
        q_rate = 0.0
        issues.append({"severity": "WARN", "code": "W_NO_BULLETS", "detail": "未识别到项目符号(- / *)分条描述，大段纯文字不利于 HR 15~40 秒初筛。"})
    if weak_starts:
        issues.append({"severity": "WARN", "code": "W_WEAK_VERBS", "detail": f"{len(weak_starts)} 条以「负责/参与/协助」开头，建议改为「主导/搭建/重构/推动」等强结果动词。"})
    if has_md_table or has_html:
        issues.append({"severity": "WARN", "code": "W_ATS_RISK", "detail": "检测到表格或 HTML 布局标签，部分 ATS 机筛系统解析易丢字段，建议改为纯线性分栏排版。"})
    if has_self_eval:
        issues.append({"severity": "INFO", "code": "I_SELF_EVAL", "detail": "存在「自我/个人评价」段落，建议替换为可验证的项目亮点摘要。"})
    if bias_hits:
        issues.append({"severity": "FAIL", "code": "E05_COMPLIANCE_REDLINE", "detail": f"命中招聘合规敏感词 {bias_hits}，请立即移除，严禁将其纳入筛选或个人基本信息栏。"})

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
    ap = argparse.ArgumentParser(description="简历版式、量化度与合规红线只读检查")
    ap.add_argument("--file", help="简历 Markdown / TXT 文件路径")
    ap.add_argument("--text", help="直接传入简历纯文本")
    ap.add_argument("--years", type=float, default=3.0, help="候选人相关工作年限（默认 3）")
    ap.add_argument("--pretty", action="store_true", help="格式化输出 JSON")
    args = ap.parse_args()

    if args.years < 0 or args.years > 50:
        fail("E04", f"工作年限超出合理区间 (0~50): {args.years}", "请传入 0~50 之间的数值。", 5)
    if not args.file and not args.text:
        fail("E01", "缺少 --file 或 --text 参数", "示例: python3 scripts/resume_check.py --file resume.md --years 3 --pretty", 2)

    if args.text is not None:
        raw = args.text
    else:
        p = Path(args.file).expanduser()
        if not p.exists() or not p.is_file():
            fail("E02", f"找不到简历文件: {p}", "请核对路径后再试。", 3)
        if p.suffix.lower() not in {".md", ".txt"}:
            fail("E03", f"暂仅直接体检 .md/.txt 纯文本，不支持 {p.suffix}", "请先将 PDF/Word 简历文本复制后通过 --text 或导出为 .md 传入。", 4)
        raw = p.read_text(encoding="utf-8", errors="replace")

    res = check_resume(raw, args.years)
    print(json.dumps(res, ensure_ascii=False, indent=2 if args.pretty else None))
    if res["status"] == "FAIL":
        sys.exit(6)


if __name__ == "__main__":
    main()
