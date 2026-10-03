#!/usr/bin/env python3
"""Static checks for the dashboard JSON files synced by Grafana Git Sync.

Queries are not executed here: CI cannot reach Grafana. See README.md for
checking them against the live data sources.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GRID_WIDTH = 24
# Data source UIDs on graph.stzky.com, plus Grafana's built-in ones.
KNOWN_DATASOURCES = {
    "eee1hnw7bw9oge",  # Prometheus
    "dfmeex0rrg7b4c",  # Loki
    "-- Grafana --",
    "-- Mixed --",
    "-- Dashboard --",
    "__expr__",
}


def panels_of(dashboard):
    """Yield (panel, visible) for every panel, including those inside collapsed rows.

    A collapsed row keeps its panels in `panels` with the positions they take when
    the row is expanded, so they can share cells with the panels below the row and
    are left out of the overlap check.
    """
    for panel in dashboard.get("panels", []):
        yield panel, True
        for child in panel.get("panels", []):
            yield child, False


def datasource_uids(panel):
    for ref in [panel.get("datasource")] + [t.get("datasource") for t in panel.get("targets", [])]:
        if isinstance(ref, dict) and ref.get("uid"):
            yield ref["uid"]


def check(path, dashboard, seen_uids, seen_titles):
    errors = []
    uid, title = dashboard.get("uid"), dashboard.get("title")
    if not uid or not title:
        return [f"{path}: missing uid or title"]
    if uid in seen_uids:
        errors.append(f"{path}: uid {uid!r} is also used by {seen_uids[uid]}")
    if title in seen_titles:
        errors.append(f"{path}: title {title!r} is also used by {seen_titles[title]}")
    seen_uids[uid], seen_titles[title] = path, path
    if "Stzky" in title:
        errors.append(f"{path}: write stzky in lowercase in the title")

    ids, cells = set(), {}
    for panel, visible in panels_of(dashboard):
        name = f"{path}: panel {panel.get('title')!r}"
        if "Stzky" in (panel.get("title") or ""):
            errors.append(f"{name}: write stzky in lowercase")
        if panel.get("id") in ids:
            errors.append(f"{name}: duplicate id {panel.get('id')}")
        ids.add(panel.get("id"))
        for ds in datasource_uids(panel):
            if ds not in KNOWN_DATASOURCES and not ds.startswith("$"):
                errors.append(f"{name}: unknown data source uid {ds!r}")
        grid = panel.get("gridPos", {})
        x, y, w, h = (grid.get(k, 0) for k in ("x", "y", "w", "h"))
        if x < 0 or y < 0 or w <= 0 or h <= 0:
            errors.append(f"{name}: invalid gridPos {grid}")
            continue
        if x + w > GRID_WIDTH:
            errors.append(f"{name}: extends past column {GRID_WIDTH}")
        if not visible:
            continue
        for row in range(y, y + h):
            for col in range(x, x + w):
                if (col, row) in cells:
                    errors.append(f"{name}: overlaps {cells[(col, row)]!r}")
                    break
                cells[(col, row)] = panel.get("title")
            else:
                continue
            break
    return errors


def main():
    files = sorted(p for p in ROOT.rglob("*.json") if not any(part.startswith(".") for part in p.relative_to(ROOT).parts))
    errors, seen_uids, seen_titles = [], {}, {}
    for file in files:
        path = file.relative_to(ROOT)
        try:
            dashboard = json.loads(file.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            errors.append(f"{path}: invalid JSON: {e}")
            continue
        errors += check(path, dashboard, seen_uids, seen_titles)
    for error in errors:
        print(error, file=sys.stderr)
    print(f"checked {len(files)} dashboard(s), {len(errors)} problem(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
