#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""deck_audit.py — PPT 演示稿（deck.json / .pptx / .html / .md 大纲）只读质检脚本。

用法:
  python3 scripts/deck_audit.py --file deck.json --minutes 10 --pretty
  python3 scripts/deck_audit.py --file slides.pptx --minutes 15 --pretty
  python3 scripts/deck_audit.py --file deck.html --pretty
  python3 scripts/deck_audit.py --text "## 第1页 结论..." --minutes 5 --pretty

退出码:
  0  PASS / WARN
  2  E01 缺少必填参数或参数错误
  3  E02 文件不存在
  4  E03 文件格式不支持或解析失败
  5  E04 篇幅/时长超出合理阈值
  6  E05 存在高危排版缺陷（如占位符未清理或整份无页数）
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

PLACEHOLDER_PATTERNS = ("单击此处添加", "click to add", "[待补]", "todo", "lorem ipsum")


def fail(code: str, message: str, hint: str, exit_code: int) -> None:
    print(json.dumps({
        "status": "ERROR",
        "error_code": code,
        "message": message,
        "fix_hint": hint,
    }, ensure_ascii=False, indent=2))
    sys.exit(exit_code)


class SlideHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.slides: list[dict[str, Any]] = []
        self._cur: dict[str, Any] | None = None
        self._in_title = False
        self._buf: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_d = dict(attrs)
        cls = attr_d.get("class") or ""
        if tag == "section" and "slide" in cls.split():
            self._cur = {"title": "", "lines": [], "notes": (attr_d.get("data-notes") or "").strip()}
        elif self._cur is not None and tag in {"h1", "h2"}:
            self._in_title = True
            self._buf = []
        elif self._cur is not None and tag in {"li", "p"}:
            self._buf = []

    def handle_data(self, data: str) -> None:
        if self._cur is not None:
            self._buf.append(data)

    def handle_endtag(self, tag: str) -> None:
        if self._cur is None:
            return
        if tag in {"h1", "h2"} and self._in_title:
            self._cur["title"] = "".join(self._buf).strip()
            self._in_title = False
            self._buf = []
        elif tag in {"li", "p"}:
            txt = "".join(self._buf).strip()
            if txt:
                self._cur["lines"].append(txt)
            self._buf = []
        elif tag == "section":
            self.slides.append(self._cur)
            self._cur = None


def parse_json_deck(raw: str) -> list[dict[str, Any]]:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        fail("E03", f"deck.json 解析失败: {exc}", "请检查 JSON 语法是否闭合。", 4)
    slides_raw = data.get("slides") if isinstance(data, dict) else data
    if not isinstance(slides_raw, list):
        fail("E03", "JSON 必须包含 slides 数组或本身为数组", "示例: {\"slides\": [{\"title\": \"...\", \"bullets\": [...], \"notes\": \"...\"}]}", 4)
    slides: list[dict[str, Any]] = []
    for s in slides_raw:
        if not isinstance(s, dict):
            continue
        lines = []
        for k in ("bullets", "body", "lines"):
            v = s.get(k)
            if isinstance(v, list):
                lines.extend(str(x).strip() for x in v if str(x).strip())
            elif isinstance(v, str) and v.strip():
                lines.extend(ln.strip() for ln in v.splitlines() if ln.strip())
        slides.append({
            "title": str(s.get("title") or "").strip(),
            "lines": lines,
            "notes": str(s.get("notes") or "").strip(),
        })
    return slides


def parse_markdown_deck(raw: str) -> list[dict[str, Any]]:
    blocks = [b.strip() for b in re.split(r"\n-{3,}\n|^##\s+", raw, flags=re.M) if b.strip()]
    slides: list[dict[str, Any]] = []
    for blk in blocks:
        lines = [ln.strip() for ln in blk.splitlines() if ln.strip()]
        if not lines:
            continue
        title = re.sub(r"^#+\s*", "", lines[0])
        body: list[str] = []
        notes = ""
        for ln in lines[1:]:
            if ln.startswith("备注") or ln.lower().startswith("notes:"):
                notes = re.sub(r"^(备注[:：]?|notes[:：]?)\s*", "", ln, flags=re.I)
            else:
                body.append(re.sub(r"^[-*•]\s*", "", ln))
        slides.append({"title": title, "lines": body, "notes": notes})
    return slides


def parse_pptx(path: Path) -> list[dict[str, Any]]:
    try:
        zf = zipfile.ZipFile(path, "r")
    except zipfile.BadZipFile:
        fail("E03", f"不是合法的 .pptx 文件: {path.name}", "请确认文件未损坏，或使用 deck.json / .md 传入。", 4)
    with zf as z:
        slide_names = sorted(
            [n for n in z.namelist() if re.match(r"^ppt/slides/slide\d+\.xml$", n)],
            key=lambda x: int(re.findall(r"\d+", x)[0]),
        )
        if not slide_names:
            fail("E03", "压缩包内未找到 ppt/slides/slide*.xml", "请确认这是标准 PowerPoint (.pptx) 文件。", 4)
        slides: list[dict[str, Any]] = []
        for idx, sname in enumerate(slide_names, 1):
            root = ET.fromstring(z.read(sname))
            texts = [el.text.strip() for el in root.iter() if el.tag.endswith("}t") and el.text and el.text.strip()]
            title = texts[0] if texts else ""
            body = texts[1:] if len(texts) > 1 else []
            notes_name = f"ppt/notesSlides/notesSlide{idx}.xml"
            notes = ""
            if notes_name in z.namelist():
                nroot = ET.fromstring(z.read(notes_name))
                ntexts = [el.text.strip() for el in nroot.iter() if el.tag.endswith("}t") and el.text and el.text.strip()]
                notes = " ".join(ntexts)
            slides.append({"title": title, "lines": body, "notes": notes})
        return slides


def audit_slides(slides: list[dict[str, Any]], minutes: int) -> dict[str, Any]:
    if not slides:
        fail("E05", "未识别到任何幻灯片页面", "请确认文件非空且格式正确。", 6)

    rec_pages = max(3, round(minutes * 1.3))
    slide_issues: list[dict[str, Any]] = []
    placeholder_hits = 0
    overdense_count = 0
    long_title_count = 0
    missing_notes_count = 0

    for idx, s in enumerate(slides, 1):
        title = s["title"]
        lines = s["lines"]
        notes = s["notes"]
        joined = (title + " " + " ".join(lines)).lower()
        errs: list[str] = []
        if not title:
            errs.append("缺少页面标题")
        elif len(title) > 20:
            long_title_count += 1
            errs.append(f"标题过长({len(title)}字 > 20字上限)")
        if len(lines) > 6:
            overdense_count += 1
            errs.append(f"正文行数过多({len(lines)}行 > 6行上限)")
        long_lines = [len(ln) for ln in lines if len(ln) > 24]
        if long_lines:
            errs.append(f"存在 {len(long_lines)} 行单行超长(>24字)，建议精简或拆分")
        if not notes and idx > 1:
            missing_notes_count += 1
            errs.append("缺少演讲者备注")
        elif len(notes) > 60:
            errs.append(f"备注偏长({len(notes)}字，建议≤40字口语金句)")
        if any(p in joined for p in PLACEHOLDER_PATTERNS):
            placeholder_hits += 1
            errs.append("发现未清理占位符文字（如「单击此处添加」/[待补]）")
        if errs:
            slide_issues.append({"slide": idx, "title": title[:24], "problems": errs})

    global_issues: list[str] = []
    if len(slides) > rec_pages * 1.6:
        global_issues.append(f"页数 {len(slides)} 偏多（{minutes} 分钟建议约 {rec_pages} 页），存在超时风险")
    elif len(slides) < max(3, int(rec_pages * 0.5)):
        global_issues.append(f"页数 {len(slides)} 偏少（{minutes} 分钟建议约 {rec_pages} 页），可能信息展开不足")

    # 10-point scorecard summary
    score = 10.0
    if long_title_count:
        score -= min(2.0, 0.5 * long_title_count)
    if overdense_count:
        score -= min(2.5, 0.7 * overdense_count)
    if missing_notes_count > len(slides) * 0.4:
        score -= 1.5
    if placeholder_hits:
        score -= 3.0
    if global_issues:
        score -= 1.0
    score = round(max(1.0, score), 1)

    status = "FAIL" if placeholder_hits > 0 else ("WARN" if (slide_issues or global_issues) else "PASS")
    return {
        "status": status,
        "error_code": "E05" if placeholder_hits > 0 else None,
        "score_out_of_10": score,
        "target_minutes": minutes,
        "recommended_pages": rec_pages,
        "actual_pages": len(slides),
        "summary_counts": {
            "long_titles": long_title_count,
            "overdense_slides": overdense_count,
            "missing_notes_slides": missing_notes_count,
            "placeholder_hits": placeholder_hits,
        },
        "global_issues": global_issues,
        "slide_issues": slide_issues,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="PPT 演示稿只读质检脚本")
    ap.add_argument("--file", help="待检测文件路径（.json / .pptx / .html / .md）")
    ap.add_argument("--text", help="直接传入 Markdown 大纲文本")
    ap.add_argument("--minutes", type=int, default=10, help="预计汇报时长（分钟），默认 10")
    ap.add_argument("--pretty", action="store_true", help="格式化输出 JSON")
    args = ap.parse_args()

    if args.minutes <= 0 or args.minutes > 240:
        fail("E04", f"汇报时长超出合理区间 (1~240 分钟): {args.minutes}", "请传入 --minutes 5/10/15/30 等正整数。", 5)
    if not args.file and not args.text:
        fail("E01", "缺少 --file 或 --text 参数", "示例: python3 scripts/deck_audit.py --file deck.json --minutes 10 --pretty", 2)

    if args.text is not None:
        slides = parse_markdown_deck(args.text)
    else:
        p = Path(args.file).expanduser()
        if not p.exists() or not p.is_file():
            fail("E02", f"文件不存在: {p}", "请核对路径后再试。", 3)
        suf = p.suffix.lower()
        if suf == ".pptx":
            slides = parse_pptx(p)
        elif suf == ".json":
            slides = parse_json_deck(p.read_text(encoding="utf-8"))
        elif suf in {".html", ".htm"}:
            parser = SlideHTMLParser()
            parser.feed(p.read_text(encoding="utf-8"))
            slides = parser.slides
        elif suf in {".md", ".txt"}:
            slides = parse_markdown_deck(p.read_text(encoding="utf-8"))
        else:
            fail("E03", f"不支持的文件扩展名: {suf}", "仅支持 .json / .pptx / .html / .md / .txt。", 4)

    res = audit_slides(slides, args.minutes)
    print(json.dumps(res, ensure_ascii=False, indent=2 if args.pretty else None))
    if res["status"] == "FAIL":
        sys.exit(6)


if __name__ == "__main__":
    main()
