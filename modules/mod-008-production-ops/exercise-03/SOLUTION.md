# SOLUTION — Exercise 3: SLO / SLI Definition & Monitoring (90 min)

Reference for [learning ex-03](https://github.com/ai-infra-curriculum/ai-infra-mlops-learning/blob/main/lessons/mod-008-production-ops/exercises/exercise-03-slosli-definition-monitoring.md).

## 1. Solution overview

Define availability and latency SLOs for the reference `iris-api`
service, express the SLIs as Prometheus recording rules, and add a
multi-window burn-rate alert. The worked answer is:

- [SLO.md](SLO.md) — the SLO table, error-budget math, alert
  policy in prose.
- [sli-slo.yml](sli-slo.yml) — Prometheus recording + alerting
  rules that implement it.

Per the module-level SOLUTION.md (Decision 1), each production
model gets its own SLO because "models have different cost /
quality / latency profiles; one global SLO is wrong for any of
them". This exercise instantiates that pattern for one service.

## 2. Worked answer

### SLO table

| SLO | Target | Window | Source metric |
|---|---|---|---|
| Availability (non-5xx) | 99.5% | 30 days | `http_requests_total` |
| Latency (fraction of requests < 200 ms) | 95% | 30 days | `http_request_duration_seconds` |

### Error budget

For availability: `1 − 0.995 = 0.005` (0.5%) of monthly requests
may fail. At ~10M requests/month, the budget is ~50,000 failed
responses before it is exhausted.

### Multi-window burn-rate alerts

Two severities on the same signal, each requiring a short *and* a
long window to fire (short = catches acute burns, long = suppresses
false positives):

- **Page** (`severity: critical`): 1h burn > 14.4× AND 5m burn >
  14.4× → 30-day budget exhausted in ~2 days at that rate.
- **Ticket** (`severity: warning`): 6h burn > 6× AND 30m burn > 6×
  → budget exhausted in ~5 days at that rate.

### Prometheus rules (from `sli-slo.yml`)

The recording rules compute the SLI ratios at 5m and 1h windows:

```yaml
- record: sli:availability:ratio_rate5m
  expr: |
    sum(rate(http_requests_total{job="iris-api",status!~"5.."}[5m]))
    /
    sum(rate(http_requests_total{job="iris-api"}[5m]))
- record: sli:availability:ratio_rate1h
  expr: |
    sum(rate(http_requests_total{job="iris-api",status!~"5.."}[1h]))
    /
    sum(rate(http_requests_total{job="iris-api"}[1h]))
- record: sli:latency:under_200ms_rate5m
  expr: |
    sum(rate(http_request_duration_seconds_bucket{job="iris-api",le="0.2"}[5m]))
    /
    sum(rate(http_request_duration_seconds_count{job="iris-api"}[5m]))
```

The alert:

```yaml
- alert: BudgetBurnFast
  expr: |
    ( (1 - sli:availability:ratio_rate1h) / 0.005 > 14.4 )
    and
    ( (1 - sli:availability:ratio_rate5m) / 0.005 > 14.4 )
  labels:   { severity: critical }
  annotations: { summary: "30d availability budget burning > 14.4x" }
```

### Decision rationale

- **Two signals, not five** — availability and latency are the
  smallest set that captures "service is up and fast". Adding
  freshness / drift SLOs is worthwhile once the base two are
  green, and belongs to Exercise 5.
- **Multi-window burn-rate** instead of static "error rate > X%":
  static thresholds either page on every blip (window too short) or
  miss slow burns (window too long). Two windows in AND kills the
  false-positive rate without dropping the true-positive rate.
- **99.5% availability, not 99.99%** — the SLO is deliberately loose
  enough that a real burn is a real problem; a stricter number
  produces alert fatigue.
- **Latency SLI is a fraction under threshold**, not a histogram
  quantile aggregated across servers — quantile aggregation is
  mathematically invalid; per-request classification is correct.

## Implementation

The rules and alerts live in [sli-slo.yml](sli-slo.yml) and the
SLO prose lives in [SLO.md](SLO.md); this is how they wire up:

- **Prometheus** — mount `sli-slo.yml` into the Prometheus config
  as a rule file; validate locally with `promtool check rules
  modules/mod-008-production-ops/exercise-03/sli-slo.yml` before
  applying. The recording rules compute 5m and 1h SLI ratios that
  the burn-rate expressions consume.
- **Alertmanager routes** — `severity: critical` routes to the
  on-call pager (fast burn = wake someone up), `severity: warning`
  routes to a ticket queue (slow burn = fix within the sprint).
  Both share the same `service: iris-api` label so the runbook
  link resolves.
- **Runbook** — the alert `annotations.runbook_url` points at the
  service runbook entry for "availability budget burning"; the
  runbook lists the top three known causes (bad deploy, dependency
  outage, retry storm) and the corresponding first-response step
  for each.
- **Review cadence** — the SLO table is re-derived quarterly
  against real traffic; if the 30-day compliance is consistently
  99.9%+ the target is tightened, if it is under 99.5% the source
  of loss is investigated before loosening.

## 3. Validation steps

- Load `sli-slo.yml` with `promtool check rules
  modules/mod-008-production-ops/exercise-03/sli-slo.yml` and
  confirm it parses.
- Confirm the availability numerator excludes 5xx (`status!~"5.."`)
  and the denominator is total requests.
- Confirm the latency SLI uses the histogram bucket `le="0.2"`
  matching the 200 ms target.
- Confirm both burn windows are present in the alert `expr` joined
  by `and` (single-window versions are considered incomplete).

## 4. Rubric / review checklist

| Weight | Criterion | Evidence |
|---|---|---|
| 25% | SLO table has target, window, and source metric per SLO | Table in `SLO.md` |
| 15% | Error budget is calculated from the target, not asserted | Arithmetic shown |
| 20% | Recording rules compute the SLI as a ratio over the correct denominator | `promtool check rules` passes |
| 20% | Alert uses a **multi-window** burn-rate expression (short AND long) | `and` between two windows in the `expr` |
| 10% | Two severities exist (page and ticket) with distinct burn thresholds | Both alerts present |
| 10% | Latency SLI uses per-request classification (bucket ratio), not aggregated quantile | `_bucket{le=...}` in the numerator |

Pass = 80% weighted score with `promtool check rules` passing.

## 5. Common mistakes

- Aggregating `histogram_quantile` across replicas and using it as
  an SLI — mathematically invalid. Use the bucket ratio instead.
- Single-window burn alerts — either flappy (short only) or blind
  (long only). Combine both.
- Availability numerator counts everything except 5xx *and 4xx*.
  4xx is usually a client error, not a service failure — count it
  in the denominator, not against the budget.
- Error budget stated as "X% availability" instead of "N failed
  requests per window" — teams cannot reason about a percentage
  when triaging an incident.
- One SLO for every model in the fleet — the module-level rationale
  explicitly rejects this (Decision 1). Instantiate per model.

## 6. References

- Module-level rationale: [../SOLUTION.md](../SOLUTION.md), esp.
  Decision 1 (SLOs per registered model).
- NIST AI Risk Management Framework —
  <https://www.nist.gov/itl/ai-risk-management-framework> (Measure
  function: performance monitoring against defined targets).
- Companion engineer-track solution linked from [SLO.md](SLO.md):
  full Sloth-format SLO spec + quarterly review template.
- Artifacts: [SLO.md](SLO.md), [sli-slo.yml](sli-slo.yml).
