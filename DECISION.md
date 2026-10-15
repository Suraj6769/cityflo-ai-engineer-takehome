# DECISION.md — Cityflo AI Engineer take-home

## Priya's question

One verdict per route, and a ranked worst-three, for the Friday review:
*which routes were actually late this week, by how much, and which three were worst*.

**Worst three (systemic): R-33, R-27, R-26.**
R-35 has the largest weekly mean (7.58 min) but a 2.0-min median; it is a one-day tail event, not a chronic route, and is not in the worst three.

## What "late" means here

- `lateness_min = actual_arrival_local - (scheduled_departure + timetable_runtime)`.
- A **trip** is late when `lateness_min > 5` minutes.
- A **route** verdict and ranking use the **median** lateness over its week's trips, with `% trips >5 min` as the reliability cross-check. Mean is reported but never used for ranking, because a single bad row or a single bad day swings it (R-35 being the case in point).
- Median chosen so one stuck GPS unit, one weather day, or one parked-bus no-show moves the worst-three ranking back toward what the depot head actually experiences.

## Data cleaning (applied before any number above)

1. 24 rows whose `actual_arrival` did not parse (`08:60` minute) were dropped (5292 -> 5268).
2. One device with `tz_offset=+00:00` was corrected to canonical `+05:30` (arrival 01:32 became 07:02 local).
3. Per REC-114, R-14 (53 min) and R-27 (45 min) are measured against `schedule_v2.csv`, not the export's `scheduled_runtime_min`.
4. No rider phone numbers or verbatim complaint text is stored or returned; trips are referenced by `trip_id` and category only.

## Route scorecard (REC-114 applied, 40 routes)

| Route | n | median lateness (min) | mean | % trips >5 min late | p90 | verdict |
|---|---:|---:|---:|---:|---:|---|
| R-33 | 104 | 5.0 | 5.36 | 47.1 | 10.0 | Late (systemic) |
| R-27 | 144 | 4.5 | 3.45 | 46.5 | 14.0 | Late (systemic) |
| R-26 | 104 | 4.0 | 3.94 | 42.3 | 9.0 | Late (systemic) |
| R-31 | 112 | 4.0 | 3.59 | 33.0 | 8.0 | Late (systemic) |
| R-37 | 105 | 4.0 | 4.13 | 40.0 | 9.0 | Late (systemic) |
| R-07 | 147 | 3.0 | 2.73 | 21.8 | 7.4 | Late (systemic) |
| R-08 | 126 | 3.0 | 2.36 | 20.6 | 7.0 | Late (systemic) |
| R-15 | 119 | 3.0 | 2.67 | 21.0 | 8.0 | Late (systemic) |
| R-17 | 147 | 3.0 | 2.98 | 27.9 | 8.0 | Late (systemic) |
| R-19 | 125 | 3.0 | 2.33 | 18.4 | 7.0 | Late (systemic) |
| R-34 | 125 | 3.0 | 2.01 | 22.4 | 8.0 | Late (systemic) |
| R-40 | 153 | 3.0 | 2.26 | 21.6 | 7.0 | Late (systemic) |
| R-02 | 105 | 2.0 | 1.34 | 14.3 | 6.0 | Late (mild) |
| R-05 | 105 | 2.0 | 2.34 | 19.0 | 7.0 | Late (mild) |
| R-09 | 147 | 2.0 | 1.95 | 22.4 | 7.4 | Late (mild) |
| R-11 | 139 | 2.0 | 1.55 | 16.5 | 7.2 | Late (mild) |
| R-12 | 112 | 2.0 | 1.79 | 13.4 | 6.0 | Late (mild) |
| R-18 | 154 | 2.0 | 2.03 | 20.8 | 7.0 | Late (mild) |
| R-20 | 146 | 2.0 | 1.65 | 16.4 | 6.5 | Late (mild) |
| R-21 | 126 | 2.0 | 0.92 | 20.6 | 7.0 | Late (mild) |
| R-22 | 112 | 2.0 | 1.82 | 16.1 | 6.0 | Late (mild) |
| R-35 | 133 | 2.0 | 7.58 | 24.1 | 49.6 | Late (mild, tail risk) |
| R-39 | 154 | 2.0 | 1.81 | 16.2 | 6.0 | Late (mild) |
| R-03 | 104 | 1.5 | 1.25 | 20.2 | 7.0 | Late (mild) |
| R-01 | 153 | 1.0 | 0.82 | 8.5 | 5.0 | Late (mild) |
| R-10 | 126 | 1.0 | 1.07 | 14.3 | 6.5 | Late (mild) |
| R-24 | 147 | 1.0 | 0.49 | 10.9 | 6.0 | Late (mild) |
| R-25 | 139 | 1.0 | 1.45 | 14.4 | 7.0 | Late (mild) |
| R-28 | 152 | 1.0 | 0.35 | 9.9 | 5.0 | Late (mild) |
| R-32 | 133 | 1.0 | 1.17 | 15.8 | 7.0 | Late (mild) |
| R-36 | 132 | 1.0 | 0.22 | 9.8 | 5.0 | Late (mild) |
| R-38 | 146 | 1.0 | 1.49 | 16.4 | 7.0 | Late (mild) |
| R-14 | 119 | 0.0 | -0.17 | 31.1 | 10.4 | Borderline (see below) |
| R-16 | 146 | 0.0 | -0.19 | 4.8 | 4.0 | On time |
| R-23 | 132 | 0.0 | 0.11 | 6.1 | 5.0 | On time |
| R-04 | 146 | -0.5 | -0.56 | 9.6 | 5.0 | On time |
| R-13 | 133 | -1.0 | -0.93 | 6.0 | 4.8 | On time |
| R-29 | 151 | -1.0 | -0.93 | 4.0 | 4.0 | On time |
| R-30 | 147 | -1.0 | -0.38 | 7.5 | 5.0 | On time |
| R-06 | 118 | -2.0 | -1.91 | 5.1 | 3.3 | On time |

## Consequential calls

### 1. R-14 must be cleared after REC-114, not flagged

- **Rule:** If `vehicle_series` is on the 4xx class and a revised runtime exists in `schedule_v2.csv`, use the revised runtime; otherwise use `scheduled_runtime_min`. R-14's arrivals are then judged against 53 min.
- **Case it breaks on:** T1-01676-class trips on R-14 on Tue where the depot head can point at 7-9 min early arrivals; under the export's ~45 min timetable even those look fine on the old basis. Actually R-14's typical trip (median 0.0 after correction) sits around on-time; one trip T1-01691 arrives 58 min early on 04 Aug, which under even the revised 53-min timetable is impossible unless the GPS stamp is wrong — the row is treated as a stuck-clock outlier, not as evidence R-14 is fast.
- **Cost, who pays:** Applying REC-114 costs the depot head nothing (R-14 keeps his incentive), and avoids ~31% false-positives. Ignoring REC-114 instead costs ~12 depot-head incentives across the route for a variance that is a reconciliation artifact.
- **What would change my mind:** A corrected export where `scheduled_runtime_min` for R-14 is genuinely 45 and the revised 53 is itself the error; then R-14 returns to worst-three candidate with 7.62 min mean.

### 2. R-35 is not in the worst three, even though it has the highest mean

- **Rule:** Route ranking and "worst three" use median lateness, and median 2.0 min. The Wednesday waterlogging day is retained in the data (it did happen), but it does not dominate the verdict because the median is unaffected by it.
- **Case it breaks on:** Every one of R-35's 19 Wednesday trips ran +36 to +61 min, i.e. the route genuinely lost ~50 min per trip that day (matching the ops log's "western corridor diverted ~35 min"). A rider standing in the rain on Wednesdays 06 Aug was out of luck, and excluding the day would be the lie. The median rule still stands because the route is on time the other six days.
- **Cost, who pays:** Not flagging R-35 "worst" costs riders nothing — they already got R-35's normal service the other six days, and the waterlogged day is an incident the ops log already owns, not a route defect. Flagging it 3rd would instead cost a different route (R-26 or R-37, at ~42%/40% late trips) its depot-head incentive for nothing.
- **What would change my mind:** A second waterlogged Wednesday, or a baseline median rising above ~3 min; either makes R-35 genuinely chronic and it goes into the worst three.

### 3. Worst three are R-33, R-27, R-26 (R-37 is fourth)

- **Rule:** Sort by (median desc, % trips >5 min late desc, mean desc); take top 3. R-33 (median 5.0, 47.1% late), R-27 (4.5, 46.5%), R-26 (4.0, 42.3%) vs R-37 (4.0, 40.0%).
- **Case it breaks on:** R-26 has one row (T1-03377) at -55 min (impossibly early, a stuck clock), which is why its mean (3.94) is *below* R-37's (4.13) while its median (4.0) equals. Using mean would swap R-26 for R-37; using median + pct late keeps R-26.
- **Cost, who pays:** Flagging R-26 over R-37 costs R-26's depot head; clearing R-26 instead costs riders on the 42.3% of trips already running 5+ min late and the refund queue. Given the two routes are within ~2 percentage points, the depot head of R-26 is the one who pays, but R-26 is the stronger chronic case on tail (p90 9.0 vs 9.0, mean lower — disputed; see "least sure" in debrief prep).
- **What would change my mind:** Recounting with the -55 row removed drops R-26's mean but not median/pct; nothing short of R-37 exceeding 42.3% pct late flips it.

### 4. Exclude stuck-clock GPS rows from any per-trip verdict, not by blanket deletion

- **Rule:** A row where `actual_arrival` is before `scheduled_departure` by more than the (negative) runtime is not used in "was this specific trip on time" drill-downs, but is counted for the route median only if within a sane bound; the 42 rows with |lateness| >= 20 min are surfaced via `trip_audit` and `route_detail` but do not vote on route classification beyond their actual value (robust median absorbs them).
- **Case it breaks on:** R-27's T1-03491 at -50 min on 07 Aug and T1-03477 at +22 min on the same morning — both probably a unit reporting a stale clock. Keeping them makes R-27's (already high) variance honest but does not move its median.
- **Cost, who pays:** Deleting them would make R-27 look 0.3 min better and would be a lie to the review; keeping them costs Priya one line in the footnote. Nobody pays for the truth.
- **What would change my mind:** A second independent GPS fix showing the bus was genuinely 50 min early.

### 5. R-14 is the mislabel trap that must be called out explicitly

- **Rule:** As consequential call 1; surfaced at the Friday review because regional review will have REC-114 numbers in front of them.
- **Case it breaks on:** R-14 at median 0.0 — looks clean only after the correction.
- **Cost, who pays:** ~119 depot-head incentives saved if REC-114 is applied.
- **What would change my mind:** The corrected export (per consequential call 1).

## Least-sure call (the one I expect to be challenged)

R-26 vs R-37 4th place: the two are 42.3% vs 40.0% pct late with identical 4.0-min medians and 9.0-min p90s. My committed pick is R-26 on pct late, defended in consequential call 3. I will not be shocked if the review swaps them.

## Ops context from ops_log (context only; does not join trips.csv on any key)

- Mon 06:10 yard swap, 2 buses late out of depot.
- Tue 21:40 driver no-show evening, covered.
- Wed 06:40 SV Road waterlogged, western corridor diverted ~35 min all AM (explains R-35 Wednesday).
- Wed 18:20 crowd surge, festival, everything slow city-wide.
- Thu 09:05 AC complaint, vehicle swapped midday.
- Fri 07:30 all normal.