---
name: word-document-master
version: 2.0.5
author: Kunlun Growth
license: MIT
description: Structural .docx document diagnostics, style rebuilding, mail merge, tracked-changes/comment extraction, and PDF conversion engineering. Includes the zero-dependency OOXML probe script scripts/docx_probe.py to inspect heading coverage, direct formatting ratios, media bloat, and page margins before editing. Activate when users mention Word, .docx formatting, broken TOCs, mail merge, extracting tracked changes/comments, or bloated document sizes.
---

# Word & Document Master

> Formatting breaks for one reason: manual "direct formatting" applied with the mouse instead of structural styles. This skill brings `.docx` workflows back to the OOXML and style-definition layer: **Probe -> Rebuild Styles -> Fix Tables/Media -> Verify 12-Point QA**.

## 1. Scope & Limits

| Dimension | Policy |
|---|---|
| **Use Cases** | Long-report style rebuilding & automatic TOCs, bulk mail-merge contracts/letters (`docxtpl`), extracting all tracked changes & comments into a table, shrinking bloated `.docx` files (`word/media/`), and lossless PDF export. |
| **Strict Boundaries** | 1. **Never fabricate business facts or legal clauses.** 2. **Never overwrite the original `.docx`**—always generate a new output file. 3. **File size guard:** `docx_probe.py` inspects `.docx` archives up to 120 MB uncompressed (convert legacy binary `.doc` to `.docx` first). |

## 2. Execution Priority

When multiple issues exist, follow this strict order:
**Structural Probe (`docx_probe.py`) -> Apply Heading/Normal Styles -> Strip Direct Formatting -> Fix Tables/Media/Sections -> Refresh TOC & Export PDF**.
Never build a TOC or tweak local fonts before clearing direct formatting.

## 3. Local Read-Only OOXML Probe (`scripts/docx_probe.py`)

Zero third-party dependencies (Python standard library only). Inspects any `.docx` without modifying it:

```bash
# 1. Inspect a .docx file
python3 scripts/docx_probe.py --file path/to/report.docx --pretty

# 2. Pre-check a Markdown/text outline before generating .docx
python3 scripts/docx_probe.py --text "# Chapter 1 Overview
Body text here." --pretty
```

Outputs: heading style coverage, direct formatting ratio, empty paragraph count, table `tblHeader` repeat-row status, pending tracked changes/comments, embedded media size (MB), and page margins (mm).

## 4. Core Engineering Rules

1. **`.docx` is a ZIP Archive:** Paragraph-level overrides live in `word/document.xml`; global style definitions live in `word/styles.xml`; image bloat lives in `word/media/`.
2. **Correct Order to Clear Direct Formatting:**
   - Step 1: Assign `Heading 1/2/3` and `Normal` styles to all paragraphs.
   - Step 2: Select All (`Ctrl+A` / `Cmd+A`) -> Clear Character Formatting (`Ctrl+Space`) & Clear Paragraph Formatting (`Ctrl+Q`).
   - Step 3: Modify the Style definitions in the Styles pane. Reversing this order wipes out heading hierarchy.
3. **Multi-Page Tables:** Always enable `Repeat Header Rows` (`w:tblHeader`) on the first row and disable `Allow row to break across pages` (`w:cantSplit`) where appropriate.
4. **Font Fallbacks:** When automating with `python-docx`, set both ASCII and East Asian/complex script font attributes if targeting multilingual documents.

## 5. Error Codes & Fallback

| Code | Trigger | Exit | Resolution |
|---|---|---|---|
| **E01** | Missing `--file` / `--text` | `2` | Provide one valid input source. |
| **E02** | File not found | `3` | Verify file path. |
| **E03** | Invalid `.docx` or corrupt XML | `4` | Re-save legacy `.doc` as `.docx` in Word/LibreOffice. |
| **E04** | Exceeds 120 MB uncompressed guard | `5` | Downscale oversized images in `word/media/` to <= 1600px. |
| **E05** | Empty body text or blocking structural defect | `6` | Ensure content is not trapped inside text boxes/images. |
| **E06** | Missing `python-docx` / `LibreOffice` | — | **Fallback:** `docx_probe.py` still runs on stdlib; deliver step-by-step Word/LibreOffice style instructions. |

## 6. 12-Point Delivery QA Checklist

- [ ] All headings use `Heading 1/2/3` (visible in Navigation Pane).
- [ ] Automatic TOC updates cleanly via `F9` / Update Field.
- [ ] Page numbers verified across all section breaks (`Link to Previous`).
- [ ] Direct formatting stripped; body paragraphs show clean `Normal` style.
- [ ] Multi-page tables have `tblHeader` enabled.
- [ ] All images embedded (not linked) and compressed appropriately.
- [ ] Tracked changes accepted/rejected; no stray review balloons if final.
- [ ] Comments resolved or exported separately as requested.
- [ ] Headers/footers verified on first and last page of every section.
- [ ] Final PDF export visually spot-checked for orphan headings or clipped tables.
