#!/usr/bin/env python3
"""Cityflo ops lateness MCP server.

Stdio MCP server. Run:  python server.py
"""
import csv
import statistics
from datetime import datetime, timedelta, timezone
from pathlib import Path

from mcp.server.fastmcp import FastMCP

DATA = Path(__file__).resolve().parent / "data"
REVISED = {"R-14": 53, "R-27": 45}  # REC-114
IST = timedelta(minutes=330)

mcp = FastMCP("cityflo-ops")


def _parse_dt(s):
    return datetime.strptime(s.strip(), "%Y-%m-%d %H:%M")


def _load_clean():
    rows = []
    dropped = 0
    tz_fixed = 0
    orig = 0
    with open(DATA / "trips.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            orig += 1
            try:
                sd = _parse_dt(r["scheduled_departure"])
                aa = _parse_dt(r["actual_arrival"])
            except ValueError:
                dropped += 1
                continue
            # tz correction: device-reported arrival -> canonical local (+05:30)
            off = r["tz_offset"].strip()
            if off == "+05:30":
                aa_local = aa
            elif off == "+00:00":
                aa_local = aa + IST
                tz_fixed += 1
            else:
                dropped += 1
                continue
            route = r["route"].strip()
            sched_rt = int(r["scheduled_runtime_min"])
            if route in REVISED:
                sched_rt = REVISED[route]
            sched_arrival = sd + timedelta(minutes=sched_rt)
            lateness = (aa_local - sched_arrival).total_seconds() / 60.0
            rows.append({
                "trip_id": r["trip_id"],
                "route": route,
                "vehicle_series": r["vehicle_series"],
                "scheduled_departure": sd,
                "weekday": sd.strftime("%A"),
                "scheduled_runtime_min": sched_rt,
                "revised_schedule": route in REVISED,
                "actual_arrival_local": aa_local,
                "tz_fixed": off != "+05:30",
                "lateness_min": lateness,
            })
    return rows, {"raw": orig, "clean": len(rows), "dropped_bad_ts": dropped, "tz_fixed": tz_fixed}


_CLEAN, _META = _load_clean()
_ROUTES = sorted({r["route"] for r in _CLEAN})


def _trim_mean(xs, lo=0.05, hi=0.95):
    s = sorted(xs)
    n = len(s)
    a = s[int(n * lo)]
    b = s[min(n - 1, int(n * hi))]
    clipped = [min(max(x, a), b) for x in s]
    return sum(clipped) / len(clipped)


def _route_stats(route):
    xs = [r["lateness_min"] for r in _CLEAN if r["route"] == route]
    xs_sorted = sorted(xs)
    n = len(xs)
    late5 = sum(1 for x in xs if x > 5)
    return {
        "route": route,
        "n_trips": n,
        "mean_lateness": round(statistics.mean(xs), 2),
        "median_lateness": round(statistics.median(xs), 2),
        "trimmed_mean_lateness": round(_trim_mean(xs), 2),
        "p90_lateness": round(xs_sorted[int(0.9 * (n - 1))], 2) if n else 0,
        "pct_trips_late_gt5": round(100.0 * late5 / n, 1),
        "max_lateness": round(max(xs), 1) if xs else 0,
        "min_lateness": round(min(xs), 1) if xs else 0,
        "revised_schedule_applied": route in REVISED,
    }


def _all_stats(metric):
    rows = [_route_stats(rt) for rt in _ROUTES]
    key = {
        "median": lambda r: r["median_lateness"],
        "mean": lambda r: r["mean_lateness"],
        "trimmed": lambda r: r["trimmed_mean_lateness"],
        "p90": lambda r: r["p90_lateness"],
        "pct_late5": lambda r: r["pct_trips_late_gt5"],
    }[metric]
    rows.sort(key=key, reverse=True)
    return rows


@mcp.tool()
def dataset_info() -> dict:
    """Counts and cleaning rules applied to the ops export."""
    return {
        "meta": _META,
        "routes": len(_ROUTES),
        "cleaning_rules": [
            "Drop rows whose scheduled_departure or actual_arrival does not parse (invalid minute e.g. 08:60).",
            "Convert misconfigured tz_offset (+00:00) arrivals to canonical +05:30 local wall clock.",
            "REC-114: R-14 and R-27 measured against revised runtime in data/schedule_v2.csv (53 and 45 min) not export scheduled_runtime_min.",
            "No rider PII or verbatim complaint text is stored or returned; reference trips by trip_id and category only.",
        ],
    }


@mcp.tool()
def route_scorecard(metric: str = "median", limit: int = 40) -> dict:
    """Per-route lateness scorecard. metric in {median, mean, trimmed, p90, pct_late5}."""
    if metric not in {"median", "mean", "trimmed", "p90", "pct_late5"}:
        metric = "median"
    rows = _all_stats(metric)[:limit]
    return {"metric": metric, "ranking": "descending", "routes": rows}


@mcp.tool()
def worst_routes(n: int = 3, metric: str = "median") -> dict:
    """Return the n worst routes under the chosen metric."""
    if metric not in {"median", "mean", "trimmed", "p90", "pct_late5"}:
        metric = "median"
    rows = _all_stats(metric)[:n]
    return {"metric": metric, "worst": rows}


@mcp.tool()
def route_detail(route_id: str) -> dict:
    """Deep dive for one route: daily breakdown, top late trips, cleaning notes."""
    r = route_id.strip().upper()
    if not r.startswith("R-"):
        r = "R-" + r.lstrip("R-").zfill(2)
    trips = [t for t in _CLEAN if t["route"] == r]
    if not trips:
        return {"error": f"unknown route {route_id}"}
    stats = _route_stats(r)
    # daily
    by_day = {}
    for t in trips:
        d = t["weekday"]
        by_day.setdefault(d, []).append(t["lateness_min"])
    daily = {
        day: {
            "n": len(xs),
            "mean": round(statistics.mean(xs), 2),
            "median": round(statistics.median(xs), 2),
            "pct_late5": round(100.0 * sum(1 for x in xs if x > 5) / len(xs), 1),
        }
        for day, xs in sorted(by_day.items())
    }
    # top late trips
    top_late = sorted(trips, key=lambda t: t["lateness_min"], reverse=True)[:8]
    top_early = sorted(trips, key=lambda t: t["lateness_min"])[:5]
    def tript(t):
        return {
            "trip_id": t["trip_id"],
            "weekday": t["weekday"],
            "scheduled_departure": t["scheduled_departure"].strftime("%Y-%m-%d %H:%M"),
            "scheduled_runtime_min": t["scheduled_runtime_min"],
            "lateness_min": round(t["lateness_min"], 1),
            "revised_schedule": t["revised_schedule"],
            "tz_fixed": t["tz_fixed"],
        }
    return {
        "route": r,
        "stats": stats,
        "daily": daily,
        "top_late_trips": [tript(t) for t in top_late],
        "most_early_trips": [tript(t) for t in top_early],
    }


@mcp.tool()
def trip_audit(route_id: str, late_only: bool = False, limit: int = 30) -> dict:
    """List trips for a route (transparency). late_only filters lateness > 5 min."""
    r = route_id.strip().upper()
    if not r.startswith("R-"):
        r = "R-" + r.lstrip("R-").zfill(2)
    trips = [t for t in _CLEAN if t["route"] == r]
    if late_only:
        trips = [t for t in trips if t["lateness_min"] > 5]
    trips = sorted(trips, key=lambda t: t["lateness_min"], reverse=True)[:limit]
    return {
        "route": r,
        "returned": len(trips),
        "trips": [
            {
                "trip_id": t["trip_id"],
                "weekday": t["weekday"],
                "scheduled_departure": t["scheduled_departure"].strftime("%Y-%m-%d %H:%M"),
                "scheduled_runtime_min": t["scheduled_runtime_min"],
                "lateness_min": round(t["lateness_min"], 1),
                "revised_schedule": t["revised_schedule"],
                "tz_fixed": t["tz_fixed"],
            }
            for t in trips
        ],
    }


@mcp.tool()
def ops_incidents() -> dict:
    """Parsed ops log lines (incident, no PII)."""
    out = []
    with open(DATA / "ops_log.txt", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(line)
    return {"incidents": out}


@mcp.tool()
def methodology() -> dict:
    """The decision rule, in runnable form."""
    return {
        "question": "Which routes were actually late this week, by how much, worst three.",
        "definition_of_late": "lateness_min = actual_arrival_local - (scheduled_departure + timetable_runtime). A trip is 'late' when lateness_min > 5 minutes.",
        "route_verdict": "Median lateness over the week's trips, with pct_trips_late_gt5 as the reliability cross-check. Mean is reported but never used for ranking because single bad rows/days swing it.",
        "rec114": "R-14 and R-27 runtimes replaced with schedule_v2.csv revised values (53, 45); all other routes use export scheduled_runtime_min.",
        "data_cleaning": "Drop unparseable timestamps (24 rows, 08:60 minute). Fix one +00:00 misconfigured device. No PII retained.",
        "worst_three_rule": "Sort routes by (median_lateness desc, pct_trips_late_gt5 desc, mean_lateness desc); take top 3. Systemic lateness beats tail risk: a one-day weather event (R-35 Wed) with median 2 min is not ranked above routes late on >=30% of trips.",
        "cost_terms": "Flagged-but-not-late costs a depot head his on-time incentive; cleared-but-late costs rider refunds and app ratings. The 5-min trip threshold and median route rule are chosen to make the depot-head false-positive rarer than the rider false-negative is not; see DECISION.md.",
    }


if __name__ == "__main__":
    mcp.run()