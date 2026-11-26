---
name: mindmap-architect
version: 1.1.0
author: Kunlun Growth
license: MIT
description: Transform messy notes, meeting transcripts, or complex topics into MECE-structured mind maps delivered simultaneously as nested Markdown, Mermaid mindmap syntax, and a self-contained interactive HTML mind map via scripts/build_mindmap.py. Activate when users ask for a mind map, brain map, structured outline, or visual knowledge breakdown.
---

# Mindmap Architect

> Turn a wall of unstructured thoughts into a clear visual hierarchy. Every mind map is built **100% locally** and delivered in three ready-to-use formats: **Markdown outline**, **Mermaid diagram**, and **interactive single-file HTML**.

## 1. Five Structural Principles

1. **One Dimension per Level:** Level-1 branches under the central topic must share a single logical axis (all phases, all modules, or all stakeholders—never mix axes).
2. **3–7 Branches Rule:** Fewer than 3 branches means under-segmented; more than 7 means cognitive overload (group into parent categories).
3. **Actionable Leaf Nodes:** End nodes should be concrete ("Pause 3 ad sets with CTR < 1%") rather than vague ("Misc items").
4. **Max Depth <= 4 Levels:** Beyond 4 levels, split into separate sub-maps.
5. **Skeleton First:** Confirm Level-1 and Level-2 branches before expanding deep leaves on large topics.

## 2. Recommended Axes by Purpose

| Purpose | Recommended Level-1 Axis | Example Branches |
|---|---|---|
| **Executive Report** | Timeline / Narrative | Context -> Actions -> Metrics -> Risks -> Next Steps |
| **Project Plan** | Workstreams | Goals -> Scope -> Resources -> Risks -> Milestones |
| **Book / Course** | Knowledge Tree | Concepts -> Principles -> Methods -> Cases -> Practice |
| **Meeting Notes** | Decision-Oriented | Decisions -> Evidence -> Open Questions -> Action Items |
| **Root Cause** | Logic Tree | Symptoms -> Root Causes (People/Process/Tools) -> Fixes |

## 3. Generate Interactive HTML Mind Map (`scripts/build_mindmap.py`)

Zero third-party dependencies (Python standard library only). Converts any nested Markdown list into a collapsible, printable single-file HTML mind map:

```bash
python3 scripts/build_mindmap.py outline.md -o mindmap.html
```

## 4. Pre-Delivery Checklist

- [ ] Central topic is concise (<= 12 words) and states audience/purpose.
- [ ] Level-1 has 3–7 branches along a single MECE axis.
- [ ] Leaf nodes are concrete and verifiable.
- [ ] Both Mermaid `mindmap` block and Markdown outline are valid and clean.
