#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_mindmap.py — Convert nested Markdown outlines into a self-contained interactive HTML mind map (zero third-party dependencies)."""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path
from typing import Any


def parse_markdown_outline(text: str) -> dict[str, Any]:
    lines = [ln.rstrip("\n") for ln in text.splitlines() if ln.strip()]
    title = "Mind Map"
    root_children: list[dict[str, Any]] = []
    stack: list[tuple[int, dict[str, Any]]] = []

    for line in lines:
        h_match = re.match(r"^(#{1,6})\s+(.+)$", line)
        if h_match:
            level = len(h_match.group(1))
            label = h_match.group(2).strip()
            if level == 1 and title == "Mind Map" and not root_children:
                title = label
                continue
            node = {"label": label, "children": []}
            depth = level - 1
            while stack and stack[-1][0] >= depth:
                stack.pop()
            if stack:
                stack[-1][1]["children"].append(node)
            else:
                root_children.append(node)
            stack.append((depth, node))
            continue

        b_match = re.match(r"^(\s*)[-*+]\s+(.+)$", line)
        if b_match:
            indent = len(b_match.group(1).replace("\t", "  "))
            label = b_match.group(2).strip()
            node = {"label": label, "children": []}
            depth = 10 + indent
            while stack and stack[-1][0] >= depth:
                stack.pop()
            if stack:
                stack[-1][1]["children"].append(node)
            else:
                root_children.append(node)
            stack.append((depth, node))

    return {"label": title, "children": root_children}


def render_tree_html(node: dict[str, Any], is_root: bool = False) -> str:
    label = html.escape(node["label"])
    children = node.get("children", [])
    cls = "node root" if is_root else "node"
    if not children:
        return f'<li class="{cls}"><span class="pill leaf">{label}</span></li>'
    child_html = "".join(render_tree_html(c) for c in children)
    return (
        f'<li class="{cls}">'
        f'<details open><summary class="pill">{label}</summary>'
        f"<ul>{child_html}</ul></details></li>"
    )


def build_html(tree: dict[str, Any]) -> str:
    title = html.escape(tree["label"])
    body_tree = render_tree_html(tree, is_root=True)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{title}</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #e2e8f0; margin: 0; padding: 32px; }}
  h1 {{ font-size: 18px; color: #94a3b8; margin-bottom: 20px; }}
  ul {{ list-style: none; padding-left: 24px; border-left: 1px dashed #334155; margin: 8px 0; }}
  ul.tree-root {{ border-left: none; padding-left: 0; }}
  li.node {{ margin: 6px 0; }}
  summary {{ cursor: pointer; list-style: none; display: inline-block; }}
  .pill {{ display: inline-block; padding: 6px 12px; border-radius: 8px; background: #1e293b; border: 1px solid #334155; font-size: 14px; }}
  li.root > details > summary.pill {{ background: #2563eb; border-color: #3b82f6; color: #fff; font-weight: 600; font-size: 16px; }}
  .pill.leaf {{ background: #0f172a; border-color: #475569; color: #cbd5e1; }}
  @media print {{ body {{ background: #fff; color: #0f172a; }} .pill {{ background: #f8fafc; border-color: #cbd5e1; color: #0f172a; }} }}
</style>
</head>
<body>
  <h1>Mindmap Architect · Kunlun Growth</h1>
  <ul class="tree-root">{body_tree}</ul>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Build interactive HTML mind map from Markdown outline.")
    parser.add_argument("input", help="Path to Markdown outline file (or '-' for stdin).")
    parser.add_argument("-o", "--output", default="mindmap.html", help="Output HTML file path.")
    parser.add_argument("--json", action="store_true", help="Print parsed tree JSON to stdout.")
    args = parser.parse_args()

    if args.input == "-":
        raw = sys.stdin.read()
    else:
        p = Path(args.input)
        if not p.exists():
            print(f"Error: file not found: {p}", file=sys.stderr)
            return 2
        raw = p.read_text(encoding="utf-8")

    tree = parse_markdown_outline(raw)
    if args.json:
        print(json.dumps(tree, ensure_ascii=False, indent=2))
    out_path = Path(args.output)
    out_path.write_text(build_html(tree), encoding="utf-8")
    print(f"Generated: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
