# Cityflo ops lateness MCP server

Answers Priya's Friday question: which routes were actually late this week, by how much, worst three.

## Run

```bash
python -m pip install -r requirements.txt
python server.py
```

The server speaks stdio MCP. Point any MCP client at it (`python server.py`).

## Tools

- `dataset_info` — raw/clean counts and cleaning rules
- `route_scorecard(metric, limit)` — per-route table (metric: median/mean/trimmed/p90/pct_late5)
- `worst_routes(n, metric)` — top n
- `route_detail(route_id)` — daily breakdown + top late trips for one route
- `trip_audit(route_id, late_only, limit)` — trip-level transparency
- `ops_incidents` — ops log
- `methodology` — the rule, runnable form

Data: `data/trips.csv` (~5,292 rows), `data/schedule_v2.csv` (REC-114), `data/ops_log.txt`.

No rider PII or verbatim complaint text is returned; trips are referenced by trip_id and category only.
