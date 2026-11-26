---
name: excel-spreadsheet-master
version: 2.0.8
author: Kunlun Growth
license: MIT
description: End-to-end Excel and CSV spreadsheet engineering pipeline: audit dirty source data, clean formatting traps, write reliable formulas (XLOOKUP/INDEX-MATCH/SUMIFS/LET), design pivot tables, select charts, and deliver production-ready .xlsx files or repeatable Python/openpyxl scripts. Activate when users mention Excel, spreadsheets, .xlsx, .csv, VLOOKUP/#N/A/#REF! errors, data cleaning, pivot tables, or reporting automation.
---

# Excel & Spreadsheet Master

> Stop manually fixing cells on dirty spreadsheets. Every spreadsheet goes through three states: **Raw/Dirty Sheet (human-entered)** -> **Clean Data Table (machine-readable)** -> **Executive Report (human-readable)**. Skipping the middle step means building on sand.

This skill executes a structured 6-stage pipeline: **Audit -> Clean -> Compute -> Summarize -> Visualize -> Verify**.

## 1. Scope & Guardrails

| Dimension | Policy |
|---|---|
| **Deliverables** | Data Audit Report (Red/Yellow/Green issues), Formula or Python (`openpyxl`/`pandas`) solution, Pivot Table config, Chart specification, and 10-point QA checklist. |
| **Strict Boundaries** | 1. **Never invent business definitions** (e.g., how "active user" or "gross margin" is defined must come from the user). 2. **Never fabricate missing values**—leave gaps blank and mark `[TBD]`. 3. **Never overwrite source files**—always output cleaned/processed copies. |

## 2. Choose the Right Execution Route

| Task Type | Typical Request | Preferred Route | Avoid |
|---|---|---|---|
| **Cleaning** | Messy formats, duplicates, merged cells | Power Query / `pandas` | Manual copy-paste |
| **Calculation** | Commissions, aging, YoY growth (<= 50k rows) | Native Excel Formulas | Macros / heavy scripts |
| **Aggregation** | Regional / monthly / category rollups | Pivot Table | Dozens of manual `SUMIFS` |
| **Presentation** | Leadership dashboards, monthly reports | Charts + Conditional Formatting | Wide walls of raw numbers |
| **Automation** | Recurring weekly/monthly reports | `openpyxl` / `pandas` script | Repeating manual steps |

**Rule of thumb:** Use formulas for one-offs, scripts for recurring workflows, Pivot Tables for multi-dimensional exploration, and charts to persuade.

## 3. Source Data Audit: Six Iron Rules

Before writing a single formula, audit the source sheet against these 6 rules:
1. **Flat 1D Table:** One record per row, one attribute per column; Row 1 is the sole header row.
2. **No Merged Cells:** Merged cells break sorting, filtering, and Pivot Tables.
3. **No Blank Rows/Columns:** Blank gaps prematurely terminate `Ctrl+Down` and range auto-detection.
4. **Single Data Type per Column:** Mixing text and numbers silently breaks `SUM` and `AVERAGE`.
5. **Unique, Single-Row Headers:** Duplicate column names (e.g., two "Amount" columns) break lookups and Pivots.
6. **True Numeric Values:** Verify numbers are not stored as text (check status bar `Sum` or left-aligned cells).

Tag findings as **Red** (breaks calculation—fix first), **Yellow** (affects presentation), or **Green** (safe).

## 4. Twelve High-Risk Spreadsheet Traps (Silent Wrong Answers)

1. **Numbers Stored as Text:** `SUM` ignores them; `SUMPRODUCT` throws `#VALUE!`. Fix: Text-to-Columns -> Finish, or `=VALUE(TRIM(A2))`.
2. **Lost Leading Zeros:** IDs like `00123` truncated to `123`. Format as Text *before* import (cannot be recovered once stripped).
3. **15-Digit Precision Loss:** 16–20 digit IDs/cards truncated to `4.2E+17` or trailing zeros. Always import long IDs as Text.
4. **Date Serial Numbers:** `45000` is a 1900-epoch date serial (~2023-03-15). Apply Date formatting.
5. **Mixed Text Dates:** `2026/3/5`, `Mar 5, 2026`, `20260305` sort alphabetically instead of chronologically. Normalize with `DATE()` or ISO `YYYY-MM-DD`.
6. **VLOOKUP Missing 4th Argument:** `=VLOOKUP(A2, Sheet2!A:C, 3)` defaults to approximate match and returns wrong rows silently. **Always pass `,FALSE)` or `,0)`.**
7. **Unanchored References:** Tax rates or lookup tables dragged without `$` (`$C$1`) shift to blank cells.
8. **Merged Cells in Data:** Only the top-left cell holds the value. Unmerge -> `Ctrl+G` (Go To Special -> Blanks) -> `=UpArrow` + `Ctrl+Enter`.
9. **Floating-Point Drift:** `=0.1+0.2=0.3` evaluates to `FALSE`. Wrap financial comparisons in `ROUND(..., 2)`.
10. **Volatile Functions:** Excessive `INDIRECT()`, `OFFSET()`, `TODAY()`, `NOW()` force full recalculation on every edit. Prefer `INDEX()`.
11. **Full-Column References:** `SUM(A:A)` or `COUNTIF(B:B, ...)` scans 1,048,576 rows. Use bounded ranges (`A2:A5000`) or Excel Tables (`Table1[Amount]`).
12. **Manual Calculation Mode:** Formulas appear frozen after edits. Switch Formulas -> Calculation Options -> Automatic (or press `F9`).

## 5. Formula Selection Matrix

| Goal | Primary Formula | Notes / Legacy Fallback |
|---|---|---|
| **Exact Lookup** | `XLOOKUP(val, lookup_col, return_col, "Not Found")` | Fallback: `INDEX(return_col, MATCH(val, lookup_col, 0))` |
| **Multi-Condition Sum** | `SUMIFS(sum_range, crit_range1, crit1, ...)` | Supports wildcards `*` and `?` |
| **Multi-Condition Count** | `COUNTIFS(range1, crit1, ...)` | Always pair with bounded ranges |
| **Multi-Branch Logic** | `IFS(cond1, val1, cond2, val2, TRUE, fallback)` | Replace nested `IF` > 3 levels |
| **Error Handling** | `IFERROR(formula, "")` | Wrap only at the outermost layer |
| **Text Joining** | `TEXTJOIN("-", TRUE, range)` | Automatically skips empty cells |
| **Date Diff / Workdays** | `DATEDIF(start, end, "M")` / `NETWORKDAYS(start, end, holidays)` | Essential for SLA and aging |
| **Month End Anchor** | `EOMONTH(date, 0)` | Standardize monthly cohort grouping |
| **Dynamic Arrays** | `FILTER`, `UNIQUE`, `SORT`, `LET` | Keep spill ranges clear |

## 6. 10-Point Delivery QA Checklist

Before delivering any `.xlsx` file or script:
- [ ] Source data passes all 6 Iron Rules (no merged cells, no mixed types).
- [ ] All `VLOOKUP` calls explicitly use `FALSE`/`0` (or replaced by `XLOOKUP`/`INDEX+MATCH`).
- [ ] Currency and financial totals wrapped in `ROUND(..., 2)`.
- [ ] No `#N/A`, `#REF!`, `#VALUE!`, `#DIV/0!`, or `#NAME?` errors anywhere in the workbook.
- [ ] Fixed constants/rates use absolute `$` references.
- [ ] Date columns normalized to consistent ISO or true Excel Date serials.
- [ ] No full-column (`A:A`) volatile bottlenecks on large sheets.
- [ ] Calculation mode verified as Automatic.
- [ ] Original source file untouched; output saved as a separate artifact.
- [ ] Python `openpyxl`/`pandas` script (if generated) runs cleanly and preserves formatting.
