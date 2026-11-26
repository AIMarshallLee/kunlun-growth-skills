#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""docx_probe.py — Read-only OOXML (.docx) & outline structural probe (zero third-party dependencies).

Usage:
  python3 scripts/docx_probe.py --file report.docx --pretty
  python3 scripts/docx_probe.py --file notice.docx --standard gb9704 --pretty
  python3 scripts/docx_probe.py --text "# Title\nBody content" --pretty

Exit codes:
  0  PASS / WARN
  2  E01 Missing or conflicting arguments
  3  E02 File not found
  4  E03 Invalid .docx or XML parse error
  5  E04 Uncompressed size > 120 MB safety guard
  6  E05 Empty document or blocking structural defect
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import Any

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W_NS}
MAX_UNCOMPRESSED_BYTES = 120 * 1024 * 1024  # 120 MB zip-bomb guard
HEADING_STYLE_HINTS = {"heading1", "heading2", "heading3", "heading4", "1", "2", "3", "4", "标题1", "标题2", "标题3", "标题 1", "标题 2", "标题 3"}
GB9704_MM = {"top": 37.0, "bottom": 35.0, "left": 28.0, "right": 26.0}


def fail(code: str, message: str, hint: str, exit_code: int) -> None:
    print(json.dumps({
        "status": "ERROR",
        "error_code": code,
        "message": message,
        "fix_hint": hint,
    }, ensure_ascii=False, indent=2))
    sys.exit(exit_code)


def twips_to_mm(val: str | None) -> float | None:
    if not val:
        return None
    try:
        return round(int(val) * 25.4 / 1440.0, 1)
    except ValueError:
        return None


def probe_text_outline(text: str, standard: str) -> dict[str, Any]:
    lines = text.splitlines()
    non_empty = [ln for ln in lines if ln.strip()]
    if not non_empty:
        fail("E05", "Input text is empty; cannot probe structure.", "Provide at least one heading or paragraph, or pass --file <path.docx>.", 6)
    headings = [ln for ln in non_empty if re.match(r"^(#{1,4}\s+|第[一二三四五六七八九十百]+[章节条]\s+|[一二三四五六七八九十]+、)", ln.strip())]
    space_aligned = [i + 1 for i, ln in enumerate(lines) if re.search(r"\S\s{4,}\S", ln)]
    manual_num = [i + 1 for i, ln in enumerate(lines) if re.match(r"^\s*\d+\.\s+\S", ln)]
    issues: list[dict[str, str]] = []
    if not headings:
        issues.append({"severity": "WARN", "code": "W_NO_HEADING", "detail": "No Markdown headings (# / ##) detected; add structured headings before generating .docx."})
    if space_aligned:
        issues.append({"severity": "WARN", "code": "W_SPACE_ALIGN", "detail": f"Line(s) {space_aligned[:5]} use 4+ consecutive spaces for alignment, which misaligns in Word."})
    if standard == "gb9704":
        issues.append({"severity": "INFO", "code": "I_GB9704", "detail": "GB/T 9704 standard selected: verify margins (37/35/28/26mm) and 28pt fixed line spacing."})
    status = "WARN" if any(x["severity"] == "WARN" for x in issues) else "PASS"
    return {
        "status": status,
        "error_code": None,
        "mode": "text_outline",
        "standard": standard,
        "metrics": {
            "total_lines": len(lines),
            "non_empty_lines": len(non_empty),
            "detected_headings": len(headings),
            "space_aligned_lines": len(space_aligned),
            "manual_numbered_lines": len(manual_num),
        },
        "issues": issues,
        "fix_hints": [x["detail"] for x in issues if x["severity"] in {"WARN", "FAIL"}],
    }


def probe_docx(path: Path, standard: str) -> dict[str, Any]:
    if not path.exists() or not path.is_file():
        fail("E02", f"File not found: {path}", "Verify the path or pass plain text via --text.", 3)
    if path.suffix.lower() != ".docx":
        fail("E03", f"Expected .docx file, got: {path.name}", "Re-save legacy .doc files as .docx in Word or LibreOffice first.", 4)

    try:
        zf_ctx = zipfile.ZipFile(path, "r")
    except zipfile.BadZipFile:
        fail("E03", f"Not a valid ZIP/OOXML container: {path.name}", "File may be corrupted or a renamed .doc/.rtf.", 4)

    with zf_ctx as z:
        infos = z.infolist()
        total_uncompressed = sum(i.file_size for i in infos)
        if total_uncompressed > MAX_UNCOMPRESSED_BYTES:
            fail("E04", f"Uncompressed size exceeds 120 MB guard ({total_uncompressed} bytes).", "Downscale oversized images inside word/media/ first.", 5)
        names = set(z.namelist())
        for req in ("[Content_Types].xml", "word/document.xml"):
            if req not in names:
                fail("E03", f"Missing required OOXML part: {req}", "Re-save as a standard .docx file.", 4)

        try:
            doc_root = ET.fromstring(z.read("word/document.xml"))
        except ET.ParseError as exc:
            fail("E03", f"Failed to parse word/document.xml: {exc}", "Fix malformed XML nodes or re-export the document.", 4)

        styles_root = None
        if "word/styles.xml" in names:
            try:
                styles_root = ET.fromstring(z.read("word/styles.xml"))
            except ET.ParseError:
                styles_root = None

        comments_count = 0
        if "word/comments.xml" in names:
            try:
                c_root = ET.fromstring(z.read("word/comments.xml"))
                comments_count = len(c_root.findall(".//w:comment", NS))
            except ET.ParseError:
                comments_count = -1

        media_files = [n for n in names if n.startswith("word/media/")]
        media_bytes = sum(i.file_size for i in infos if i.filename.startswith("word/media/"))

    paras = doc_root.findall(".//w:body/w:p", NS)
    non_empty_paras = 0
    heading_paras = 0
    direct_run_fmt = 0
    space_align_paras = 0
    empty_spacer_paras = 0
    has_cjk_content = False

    for p in paras:
        texts = "".join(t.text or "" for t in p.findall(".//w:t", NS))
        if not texts.strip():
            empty_spacer_paras += 1
            continue
        non_empty_paras += 1
        if not has_cjk_content and re.search(r"[\u4e00-\u9fff]", texts):
            has_cjk_content = True
        p_style_el = p.find("./w:pPr/w:pStyle", NS)
        style_val = (p_style_el.get(f"{{{W_NS}}}val") or "").strip().lower() if p_style_el is not None else ""
        if style_val in HEADING_STYLE_HINTS or style_val.startswith("heading"):
            heading_paras += 1
        if p.findall("./w:r/w:rPr", NS):
            direct_run_fmt += 1
        if re.search(r"\S\s{4,}\S", texts):
            space_align_paras += 1

    tables = doc_root.findall(".//w:body/w:tbl", NS)
    tables_with_repeat_header = 0
    for tbl in tables:
        first_tr = tbl.find("./w:tr", NS)
        if first_tr is not None and first_tr.find("./w:trPr/w:tblHeader", NS) is not None:
            tables_with_repeat_header += 1

    ins_count = len(doc_root.findall(".//w:ins", NS))
    del_count = len(doc_root.findall(".//w:del", NS))

    margins_mm: dict[str, float | None] = {}
    pg_mar = doc_root.find(".//w:sectPr/w:pgMar", NS)
    if pg_mar is not None:
        for side in ("top", "bottom", "left", "right"):
            margins_mm[side] = twips_to_mm(pg_mar.get(f"{{{W_NS}}}{side}"))

    has_eastasia_font = False
    if styles_root is not None:
        for rf in styles_root.findall(".//w:rFonts", NS):
            if rf.get(f"{{{W_NS}}}eastAsia"):
                has_eastasia_font = True
                break

    issues: list[dict[str, str]] = []
    if non_empty_paras == 0 and len(tables) == 0:
        issues.append({"severity": "FAIL", "code": "F_EMPTY_DOC", "detail": "Both body paragraphs and tables are empty."})
    if non_empty_paras >= 5 and heading_paras == 0:
        issues.append({"severity": "WARN", "code": "W_NO_HEADING_STYLE", "detail": "No Heading 1/2/3 styles detected; automatic TOC and Navigation Pane will be empty."})
    if non_empty_paras > 0 and (direct_run_fmt / non_empty_paras) > 0.5:
        issues.append({"severity": "WARN", "code": "W_HIGH_DIRECT_FMT", "detail": f"Over half of paragraphs ({direct_run_fmt}/{non_empty_paras}) have direct character formatting; strip overrides and use styles."})
    if space_align_paras > 0:
        issues.append({"severity": "WARN", "code": "W_SPACE_ALIGN", "detail": f"{space_align_paras} paragraph(s) use repeated spaces for alignment; replace with tabs or borderless tables."})
    if empty_spacer_paras > max(5, non_empty_paras * 0.4):
        issues.append({"severity": "WARN", "code": "W_EMPTY_PARAS", "detail": f"Too many empty spacer paragraphs ({empty_spacer_paras}); use paragraph spacing or page breaks instead."})
    if len(tables) > 0 and tables_with_repeat_header < len(tables):
        issues.append({"severity": "WARN", "code": "W_TBL_NO_REPEAT_HDR", "detail": f"{len(tables)-tables_with_repeat_header}/{len(tables)} table(s) lack 'Repeat Header Rows' (w:tblHeader)."})
    if (ins_count + del_count) > 0:
        issues.append({"severity": "WARN", "code": "W_UNRESOLVED_REVISIONS", "detail": f"{ins_count + del_count} unresolved tracked change(s) found; accept or reject before final delivery."})
    if comments_count > 0:
        issues.append({"severity": "WARN", "code": "W_UNRESOLVED_COMMENTS", "detail": f"{comments_count} comment(s) present; resolve or strip before external distribution."})
    if (has_cjk_content or standard == "gb9704") and not has_eastasia_font:
        issues.append({"severity": "WARN", "code": "W_NO_EASTASIA_FONT", "detail": "styles.xml does not specify w:eastAsia font for CJK text; fallback rendering may occur."})
    if media_bytes > 20 * 1024 * 1024:
        issues.append({"severity": "WARN", "code": "W_HEAVY_MEDIA", "detail": f"Embedded media totals {round(media_bytes/1048576, 1)} MB; compress images to <= 1600px."})

    if standard == "gb9704":
        if not margins_mm:
            issues.append({"severity": "WARN", "code": "W_GB9704_NO_MARGIN", "detail": "No w:pgMar found; verify GB/T 9704 margins (37/35/28/26mm)."})
        else:
            diffs = [f"{k}={margins_mm.get(k)}mm (expected {v})" for k, v in GB9704_MM.items() if margins_mm.get(k) is None or abs(margins_mm[k] - v) > 1.5]
            if diffs:
                issues.append({"severity": "WARN", "code": "W_GB9704_MARGINS", "detail": "Margins deviate from GB/T 9704: " + ", ".join(diffs)})

    has_fail = any(i["severity"] == "FAIL" for i in issues)
    status = "FAIL" if has_fail else ("WARN" if issues else "PASS")
    return {
        "status": status,
        "error_code": "E05" if has_fail else None,
        "mode": "docx_archive",
        "file": str(path),
        "standard": standard,
        "metrics": {
            "total_paragraphs": len(paras),
            "non_empty_paragraphs": non_empty_paras,
            "heading_paragraphs": heading_paras,
            "direct_formatted_paragraphs": direct_run_fmt,
            "empty_paragraphs": empty_spacer_paras,
            "tables": len(tables),
            "tables_with_repeat_header": tables_with_repeat_header,
            "embedded_media_count": len(media_files),
            "embedded_media_mb": round(media_bytes / 1048576, 2),
            "revisions_ins_del": ins_count + del_count,
            "comments_count": comments_count,
            "has_eastasia_font": has_eastasia_font,
            "margins_mm": margins_mm,
        },
        "issues": issues,
        "fix_hints": [i["detail"] for i in issues],
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Read-only OOXML (.docx) & document outline probe.")
    ap.add_argument("--file", help="Path to .docx file")
    ap.add_argument("--text", help="Inline Markdown/plain-text outline")
    ap.add_argument("--standard", choices=["general", "gb9704"], default="general", help="Check standard: general or gb9704")
    ap.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    args = ap.parse_args()

    if not args.file and not args.text:
        fail("E01", "Provide one of --file or --text.", "Example: python3 scripts/docx_probe.py --file report.docx --pretty", 2)
    if args.file and args.text:
        fail("E01", "Cannot pass both --file and --text.", "Choose one input source.", 2)

    if args.text is not None:
        res = probe_text_outline(args.text, args.standard)
    else:
        res = probe_docx(Path(args.file).expanduser(), args.standard)

    print(json.dumps(res, ensure_ascii=False, indent=2 if args.pretty else None))
    if res["status"] == "FAIL":
        sys.exit(6)


if __name__ == "__main__":
    main()
