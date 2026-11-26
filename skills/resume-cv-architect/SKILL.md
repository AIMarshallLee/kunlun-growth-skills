---
name: resume-cv-architect
version: 2.0.4
author: Kunlun Growth
license: MIT
description: Two-sided resume & recruiting engineering workflow. For recruiters/hiring managers: parse job descriptions (scripts/parse_jd.py), apply <=5 must-have filters, run 5-dimension weighted scoring, and generate verification questions. For candidates: rewrite bullets using STAR quantification, strip AI cliches (scripts/audit_ai_flavor.py), and check ATS & length compliance (scripts/resume_check.py). Activate when users ask to screen resumes, tailor a CV, run ATS checks, or remove AI-sounding phrasing.
---

# Resume & CV Architect

> Recruiting is hard on both sides: hiring managers have 15–40 seconds per resume, while candidates struggle to turn daily duties into verifiable impact. This skill provides **objective scoring rubrics and zero-dependency read-only Python audit scripts** for both sides.

## 1. Scope & Compliance Guardrails

| Dimension | Policy |
|---|---|
| **Recruiter Mode** | JD keyword & seniority parsing (`parse_jd.py`), `<=5` must-have knockouts, 5-dimension weighted scoring, and interview verification questions for gaps/anomalies. |
| **Candidate Mode** | ATS & page-budget check (`resume_check.py`), JD alignment, STAR quantification, and AI-cliche removal (`audit_ai_flavor.py`). |
| **Strict Red Lines** | 1. **Never fabricate experience, titles, degrees, or metrics**—if numbers are missing, ask or mark `[TBD]`. 2. **Zero discriminatory filtering**—never score or filter by age, gender, marital status, ethnicity, or protected characteristics. 3. **Plain-text input for scripts:** Extract text from PDF/DOCX into `.md`/`.txt` before running scripts. |

## 2. Local Read-Only Script Pipeline (`scripts/`)

Zero third-party dependencies (Python standard library only):

```bash
# 1. Parse a Job Description for role family, seniority, and weighted skills
python3 scripts/parse_jd.py --jd-text "Senior Python Backend Engineer, 3+ years, Docker & PostgreSQL" --pretty

# 2. Check resume length, action-verb strength, quantification rate, and ATS/compliance risks
python3 scripts/resume_check.py --file my_resume.md --years 5 --pretty

# 3. Audit for AI cliches (e.g., "spearheaded", "synergy", "empowered", "delved")
python3 scripts/audit_ai_flavor.py --file my_resume.md --pretty --summary
```

## 3. Core Methodologies

- **Recruiter Scoring (5 Dimensions):** Role Match (35%) + Verified Impact (25%) + Technical/Domain Depth (20%) + Career Trajectory (10%) + Stability (10%). Advance candidates scoring `>= 3.0 / 5.0` with **no 0-score** on any >=20% weight dimension.
- **Candidate STAR Rules:** Lead every bullet with a strong action verb (never *"Responsible for"*), 3–5 bullets per role, quantify outcomes with baselines (e.g., *"Reduced API p95 latency from 420ms to 140ms (-67%)"*), and align top 1/3 of page 1 with JD keywords.
- **Page Budget:** `<3 yrs` = 1 page; `3–8 yrs` = <= 2 pages; `>8 yrs` = <= 3 pages.

## 4. Error Codes & Fallback

| Code | Trigger | Exit | Resolution |
|---|---|---|---|
| **E01** | Missing `--file` / `--text` / `--jd-text` | `2` | Supply required input flag. |
| **E02** | File or reference JSON not found | `3` | Check path and `references/*.json`. |
| **E03** | Binary `.pdf`/`.docx` passed directly | `4` | Extract plain text to `.md`/`.txt` first. |
| **E04** | Input < 40 chars or `--years` outside `0..50` | `5` | Provide complete text and valid years. |
| **E05** | Compliance red-line or severe AI-cliche hit | `6` | Remove protected attributes or rewrite cliches. |
| **E06** | Restricted Python environment | — | **Fallback:** Apply the 5-dimension rubric and STAR rules manually in markdown. |
