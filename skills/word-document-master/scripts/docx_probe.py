#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""docx_probe.py — Word (.docx) / 文本结构只读体检脚本（零第三方依赖）。

用法:
  python3 scripts/docx_probe.py --file report.docx --pretty
  python3 scripts/docx_probe.py --file notice.docx --standard gb9704 --pretty
  python3 scripts/docx_probe.py --text "# 标题\n正文内容" --pretty

退出码:
  0  PASS / WARN（结构合法，可参考建议优化）
  2  E01 缺少必填参数或参数组合无效
  3  E02 文件不存在或路径越界
  4  E03 文件非合法 .docx / XML 解析失败
  5  E04 文件体积或内容超过安全阈值
  6  E05 命中硬性阻断缺陷（如无有效正文/大面积缺样式且含未清理标记）
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
        fail("E05", "输入文本为空，无法生成文档结构检查", "请提供至少一段正文或标题文本，或传入 --file <path.docx>。", 6)
    headings = [ln for ln in non_empty if re.match(r"^(#{1,4}\s+|第[一二三四五六七八九十百]+[章节条]\s+|[一二三四五六七八九十]+、)", ln.strip())]
    space_aligned = [i + 1 for i, ln in enumerate(lines) if re.search(r"\S\s{4,}\S", ln)]
    manual_num = [i + 1 for i, ln in enumerate(lines) if re.match(r"^\s*\d+\.\s+\S", ln)]
    issues: list[dict[str, str]] = []
    if not headings:
        issues.append({"severity": "WARN", "code": "W_NO_HEADING", "detail": "未检测到明确标题层级（建议用 #/## 或「一、」「（一）」标识层级）。"})
    if space_aligned:
        issues.append({"severity": "WARN", "code": "W_SPACE_ALIGN", "detail": f"第 {space_aligned[:5]} 行存在连续 4 个以上空格对齐，转入 Word 后易错位。"})
    if standard == "gb9704":
        issues.append({"severity": "INFO", "code": "I_GB9704", "detail": "已选 GB/T 9704 公文标准：正式出稿需确保页边距上37/下35/左28/右26mm、仿宋三号行距固定28磅。"})
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
        fail("E02", f"找不到目标文件: {path}", "请核对文件路径是否正确，或改用 --text 传入纯文本。", 3)
    if path.suffix.lower() != ".docx":
        fail("E03", f"文件后缀不是 .docx: {path.name}", "当前脚本仅体检 .docx（OOXML）。旧版 .doc 请先用 Word/LibreOffice 另存为 .docx。", 4)

    try:
        zf_ctx = zipfile.ZipFile(path, "r")
    except zipfile.BadZipFile:
        fail("E03", f"文件不是有效的 ZIP/OOXML 容器: {path.name}", "可能文件已损坏或实为重命名的 .doc/.rtf，请先在办公软件另存为标准 .docx。", 4)

    with zf_ctx as z:
        infos = z.infolist()
        total_uncompressed = sum(i.file_size for i in infos)
        if total_uncompressed > MAX_UNCOMPRESSED_BYTES:
            fail("E04", f"解压后体积超限 ({total_uncompressed} bytes > 120MB)", "请先压缩 word/media 内的超大图片后再进行体检。", 5)
        names = set(z.namelist())
        for req in ("[Content_Types].xml", "word/document.xml"):
            if req not in names:
                fail("E03", f".docx 缺少核心部件 {req}", "请用 Word/WPS 重新另存为标准 .docx。", 4)

        try:
            doc_root = ET.fromstring(z.read("word/document.xml"))
        except ET.ParseError as exc:
            fail("E03", f"word/document.xml 解析失败: {exc}", "XML 节点存在语法损坏，请定位对应标签或重新导出文档。", 4)

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

    for p in paras:
        texts = "".join(t.text or "" for t in p.findall(".//w:t", NS))
        if not texts.strip():
            empty_spacer_paras += 1
            continue
        non_empty_paras += 1
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

    # Page margins
    margins_mm: dict[str, float | None] = {}
    pg_mar = doc_root.find(".//w:sectPr/w:pgMar", NS)
    if pg_mar is not None:
        for side in ("top", "bottom", "left", "right"):
            margins_mm[side] = twips_to_mm(pg_mar.get(f"{{{W_NS}}}{side}"))

    # Check EastAsia font in styles.xml
    has_eastasia_font = False
    if styles_root is not None:
        for rf in styles_root.findall(".//w:rFonts", NS):
            if rf.get(f"{{{W_NS}}}eastAsia"):
                has_eastasia_font = True
                break

    issues: list[dict[str, str]] = []
    if non_empty_paras == 0 and len(tables) == 0:
        issues.append({"severity": "FAIL", "code": "F_EMPTY_DOC", "detail": "正文与表格均为空（无有效文本内容）。"})
    if non_empty_paras >= 5 and heading_paras == 0:
        issues.append({"severity": "WARN", "code": "W_NO_HEADING_STYLE", "detail": "未检测到标题样式（Heading 1/2/3），将无法生成自动目录和导航窗格。"})
    if non_empty_paras > 0 and (direct_run_fmt / non_empty_paras) > 0.5:
        issues.append({"severity": "WARN", "code": "W_HIGH_DIRECT_FMT", "detail": f"超过一半段落({direct_run_fmt}/{non_empty_paras})含字符直接格式，建议清理后改用样式控制。"})
    if space_align_paras > 0:
        issues.append({"severity": "WARN", "code": "W_SPACE_ALIGN", "detail": f"发现 {space_align_paras} 处用多个空格对齐，跨端易错位，建议改用制表位或无框线表格。"})
    if empty_spacer_paras > max(5, non_empty_paras * 0.4):
        issues.append({"severity": "WARN", "code": "W_EMPTY_PARAS", "detail": f"空段落过多({empty_spacer_paras}个)，疑用回车推分页/调间距，建议改用段前距或 Ctrl+Enter 分页符。"})
    if len(tables) > 0 and tables_with_repeat_header < len(tables):
        issues.append({"severity": "WARN", "code": "W_TBL_NO_REPEAT_HDR", "detail": f"{len(tables)-tables_with_repeat_header}/{len(tables)} 个表格未开启「跨页重复标题行」。"})
    if (ins_count + del_count) > 0:
        issues.append({"severity": "WARN", "code": "W_UNRESOLVED_REVISIONS", "detail": f"存在 {ins_count + del_count} 处未接受/未清理修订痕迹，对外交付前需处理。"})
    if comments_count > 0:
        issues.append({"severity": "WARN", "code": "W_UNRESOLVED_COMMENTS", "detail": f"存在 {comments_count} 条批注，对外正式发稿前请确认是否删除。"})
    if not has_eastasia_font:
        issues.append({"severity": "WARN", "code": "W_NO_EASTASIA_FONT", "detail": "styles.xml 未显式指定 w:eastAsia 中文字体，部分系统可能回退为默认宋体。"})
    if media_bytes > 20 * 1024 * 1024:
        issues.append({"severity": "WARN", "code": "W_HEAVY_MEDIA", "detail": f"嵌入图片总计 {round(media_bytes/1048576, 1)}MB，建议长边压缩至 ≤1600px。"})

    if standard == "gb9704":
        if not margins_mm:
            issues.append({"severity": "WARN", "code": "W_GB9704_NO_MARGIN", "detail": "未读取到页面边距节点 w:pgMar，请人工核对 GB/T 9704（上37/下35/左28/右26mm）。"})
        else:
            diffs = [f"{k}={margins_mm.get(k)}mm(标准{v})" for k, v in GB9704_MM.items() if margins_mm.get(k) is None or abs(margins_mm[k] - v) > 1.5]
            if diffs:
                issues.append({"severity": "WARN", "code": "W_GB9704_MARGINS", "detail": "页边距不符合 GB/T 9704 公文标准：" + "，".join(diffs)})

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
    ap = argparse.ArgumentParser(description="Word (.docx) 或文档大纲只读体检工具")
    ap.add_argument("--file", help="待检测的 .docx 文件路径")
    ap.add_argument("--text", help="无 .docx 文件时，直接传入 Markdown/纯文本大纲预检")
    ap.add_argument("--standard", choices=["general", "gb9704"], default="general", help="检查标准：general 通用文档 / gb9704 党政公文")
    ap.add_argument("--pretty", action="store_true", help="格式化输出 JSON")
    args = ap.parse_args()

    if not args.file and not args.text:
        fail("E01", "缺少输入参数：必须提供 --file 或 --text 之一", "示例: python3 scripts/docx_probe.py --file report.docx --pretty", 2)
    if args.file and args.text:
        fail("E01", "--file 与 --text 不能同时传入", "请二选一传入。", 2)

    if args.text is not None:
        res = probe_text_outline(args.text, args.standard)
    else:
        res = probe_docx(Path(args.file).expanduser(), args.standard)

    print(json.dumps(res, ensure_ascii=False, indent=2 if args.pretty else None))
    if res["status"] == "FAIL":
        sys.exit(6)


if __name__ == "__main__":
    main()
