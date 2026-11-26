---
name: ai-workflow-diagnosis
version: 1.0.2
author: Kunlun Growth
license: MIT
description: Evaluate business processes for AI automation using a 5-dimension weighted scoring matrix (Frequency, Standardization, Data Availability, Business Value, Risk), conservative ROI estimation formulas, human-in-the-loop responsibility boundaries, and a 4-week pilot execution plan. Activate when users ask where to apply AI in their business, how to prioritize AI use cases, estimate AI ROI, or design an AI pilot.
---

# AI Workflow Diagnosis

> Designed for founders, operations leaders, and AI architects deciding **where AI actually pays off first**—without vendor hype or fabricated ROI promises.

## 1. Scope & Guardrails

| Dimension | Policy |
|---|---|
| **Deliverables** | 8–12 candidate use cases mapped to business flow, 5-dimension weighted scoring matrix, Top 1–2 pilot picks, conservative ROI formula, 4-week pilot plan, and Human-in-the-Loop boundaries. |
| **Strict Boundaries** | 1. **Never guarantee financial savings**—present formulas and mark estimates as `[Estimate - verify with actual labor rates]`. 2. **Vendor-neutral**—focus on workflow mechanics before tool selection. 3. **Single-pilot discipline**—converge on 1 department + 1 input type + 1 verifiable output. |

## 2. Five-Dimension Scoring Matrix

| Dimension | 1 (Low) | 3 (Medium) | 5 (High) | Weight |
|---|---|---|---|---|
| **Frequency** | < 10x / month | 50–200x / month | > 500x / month | **25%** |
| **Standardization** | Ad-hoc every time | Loose guidelines exist | Clear templates & rules | **25%** |
| **Data Availability** | No historical records | Scattered/partial records | Structured historical data | **20%** |
| **Business Value** | Helps < 1 person | Helps 1 team | Impacts dept KPI or revenue | **20%** |
| **Risk Controllability** | High error cost, hard to spot | Correctable errors | Easy to spot, low error cost | **10%** |

**Decision Thresholds:** Weighted Score `>= 3.8` = **Priority Pilot**; `3.0–3.7` = **Secondary Candidate**; `< 3.0` = **Defer**.

## 3. Conservative ROI Formula

```text
Monthly Hours Saved = Monthly Volume * Baseline Hours/Task * (1 - Post-AI Time Ratio)
Monthly Labor Value = (Monthly Hours Saved / 8) * Daily Labor Cost
Payback Period (Mo) = One-Time Setup Cost / Monthly Labor Value
```

- Keep `Post-AI Time Ratio` conservative at `0.30–0.50` (never assume 0% human review time).
- If Payback Period `> 6 months`, recommend deferring until data/process standardization improves.

## 4. Four-Week Pilot Blueprint

| Week | Focus | Deliverable | Acceptance Gate |
|---|---|---|---|
| **Week 1** | Process mapping & data collection | As-is flowchart + sample dataset | Covers >= 80% of real cases |
| **Week 2** | Prompt/template & guardrail build | Workflow v1 | 20-sample human eval >= 4.0/5.0 |
| **Week 3** | Shadow run & edge-case tuning | Error log + Workflow v2 | Handles >= 90% of edge cases |
| **Week 4** | Before/After benchmark | Pilot readout (time, quality, coverage) | Verified before/after metrics |

## 5. Human-in-the-Loop Boundaries

- **AI Drafts, Humans Approve:** Never auto-send external client/legal communications without human review.
- **Sampling QA:** Audit at least 10% of automated classifications/extractions.
- **No Autonomous High-Stakes Decisions:** Keep hiring, pricing, refunds, and compliance sign-off strictly human-owned.

---
*Need an enterprise AI workflow audit or custom Gemini CLI / MCP integration? Visit [kunlungrowth.com](https://kunlungrowth.com) or email [dasean@yeah.net](mailto:dasean@yeah.net).*
