#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""deck_audit.py — Read-only quality auditor for presentations (.json / .pptx / .html / .md).

Usage:
  python3 scripts/deck_audit.py --file deck.json --minutes 10 --pretty
  python3 scripts/deck_audit.py --file slides.pptx --minutes 15 --pretty
  python3 scripts/deck_audit.py --file deck.html --pretty
  python3 scripts/deck_audit.py --text "## Slide 1 Takeaway..." --minutes 5 --pretty

Exit codes:
  0  PASS / WARN
  2  E01 Missing or invalid arguments
  3  E02 File not found
  4  E03 Unsupported format or parse failure
  5  E04 Duration out of range (1..240 minutes)
  6  E05 Blocking defects (e.g., unresolved placeholders or 0 slides)
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

PLACEHOLDER_PATTERNS = ("click to add", "[tbd]", "todo", "lorem ipsum", "单击此处添加", "[待补]")


def fail(code: str, message: str, hint: str, exit_code: int) -> None:
    print(json.dumps({
        "status": "ERROR",
        "error_code": code,
        "message": message,
        "fix_hint": hint,
    }, ensure_ascii=False, indent=2))
    sys.exit(exit_code)


def _is_cjk_heavy(text: str) -> bool:
    cjk = len(re.findall(r"[\u4e00-\u9fff]", text))
    return cjk > len(text) * 0.25


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
        fail("E03", f"Failed to parse deck.json: {exc}", "Verify valid JSON syntax.", 4)
    slides_raw = data.get("slides") if isinstance(data, dict) else data
    if not isinstance(slides_raw, list):
        fail("E03", "JSON must be an array or contain a 'slides' array.", 'Example: {"slides": [{"title": "...", "bullets": [...], "notes": "..."}]}', 4)
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
        fail("E03", f"Invalid .pptx archive: {path.name}", "Verify the file is not corrupted, or pass deck.json / .md.", 4)
    with zf as z:
        slide_names = sorted(
            [n for n in z.namelist() if re.match(r"^ppt/slides/slide\d+\.xml$", n)],
            key=lambda x: int(re.findall(r"\d+", x)[0]),
        )
        if not slide_names:
            fail("E03", "No ppt/slides/slide*.xml found inside archive.", "Ensure this is a standard PowerPoint (.pptx) file.", 4)
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
        fail("E05", "No slides detected in input.", "Verify the file is non-empty and properly formatted.", 6)

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
            errs.append("Missing slide title.")
        else:
            title_limit = 24 if _is_cjk_heavy(title) else 72
            if len(title) > title_limit:
                long_title_count += 1
                errs.append(f"Title too long ({len(title)} chars > {title_limit} limit).")

        if len(lines) > 6:
            overdense_count += 1
            errs.append(f"Too many body lines ({len(lines)} lines > 6 limit).")

        long_lines = [ln for ln in lines if len(ln) > (28 if _is_cjk_heavy(ln) else 90)]
        if long_lines:
            errs.append(f"{len(long_lines)} line(s) exceed recommended length; split or tighten.")

        if not notes and idx > 1:
            missing_notes_count += 1
            errs.append("Missing speaker notes.")
        elif notes:
            notes_limit = 60 if _is_cjk_heavy(notes) else 240
            if len(notes) > notes_limit:
                errs.append(f"Speaker notes too long ({len(notes)} chars > {notes_limit} limit).")

        if any(p in joined for p in PLACEHOLDER_PATTERNS):
            placeholder_hits += 1
            errs.append("Unresolved placeholder text found (e.g., 'Click to add', '[TBD]', 'Lorem ipsum').")

        if errs:
            slide_issues.append({"slide": idx, "title": title[:40], "problems": errs})

    global_issues: list[str] = []
    if len(slides) > rec_pages * 1.6:
        global_issues.append(f"Slide count ({len(slides)}) is high for {minutes} min (recommended ~{rec_pages}); risk of running overtime.")
    elif len(slides) < max(3, int(rec_pages * 0.5)):
        global_issues.append(f"Slide count ({len(slides)}) is low for {minutes} min (recommended ~{rec_pages}); key points may be under-explained.")

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
    ap = argparse.ArgumentParser(description="Read-only presentation quality auditor.")
    ap.add_argument("--file", help="Path to presentation (.json / .pptx / .html / .md)")
    ap.add_argument("--text", help="Inline Markdown slide outline")
    ap.add_argument("--minutes", type=int, default=10, help="Target talk duration in minutes (default: 10)")
    ap.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    args = ap.parse_args()

    if args.minutes <= 0 or args.minutes > 240:
        fail("E04", f"Duration out of bounds (1..240 minutes): {args.minutes}", "Pass a positive integer like --minutes 5/10/15/30.", 5)
    if not args.file and not args.text:
        fail("E01", "Missing --file or --text argument.", "Example: python3 scripts/deck_audit.py --file deck.json --minutes 10 --pretty", 2)

    if args.text is not None:
        slides = parse_markdown_deck(args.text)
    else:
        p = Path(args.file).expanduser()
        if not p.exists() or not p.is_file():
            fail("E02", f"File not found: {p}", "Verify the file path and retry.", 3)
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
            fail("E03", f"Unsupported file extension: {suf}", "Supported formats: .json, .pptx, .html, .md, .txt.", 4)

    res = audit_slides(slides, args.minutes)
    print(json.dumps(res, ensure_ascii=False, indent=2 if args.pretty else None))
    if res["status"] == "FAIL":
        sys.exit(6)


if __name__ == "__main__":
    main()
