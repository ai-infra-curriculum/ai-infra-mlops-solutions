# SOLUTION — Exercise 2: Capacity Planning & Resource Management (90 min)

Reference for [learning ex-02](https://github.com/ai-infra-curriculum/ai-infra-mlops-learning/blob/main/lessons/mod-008-production-ops/exercises/exercise-02-capacity-planning-resource-management.md).

## 1. Solution overview

Given a target load profile (sustained + peak RPS, latency budget)
and a single-pod capacity measurement, produce:

1. A sizing plan (min replicas, HPA max, headroom for AZ failure).
2. A cluster shape that fits the pods across AZs with reserve.
3. A cost estimate and a mix of on-demand + spot.
4. Triggers and alerts that keep the plan honest as load drifts.

The worked example in [CAPACITY.md](CAPACITY.md) walks through a
product-recommendation inference service: 5K sustained, 15K peak,
p95 < 150 ms.

## 2. Worked answer

See [CAPACITY.md](CAPACITY.md). Summary of the numbers and where
they come from:

| Input | Value | Source |
|---|---|---|
| Sustained RPS | 5,000 | Requirement |
| Peak RPS | 15,000 | Requirement |
| Latency SLO | p95 < 150 ms | Requirement |
| Single-pod RPS at 80% CPU | 200 | Measured (load test) |
| Single-pod memory | 1 GB | Measured |

Derived:

| Output | Calculation | Value |
|---|---|---|
| Min replicas (sustained) | 5000 / 200 | 25 |
| Replicas at peak | 15000 / 200 | 75 |
| HPA max (peak + 20% AZ headroom) | 75 × 1.2 | 90 |
| Cluster CPU at HPA max | 0.8 vCPU × 90 | 72 vCPU |
| Cluster memory at HPA max | 1 GB × 90 | 90 GB |
| Cluster shape | 6 × m5.4xlarge (16 vCPU / 64 GB) | 96 vCPU / 384 GB across AZs |
| On-demand cost | 6 × $0.768/hr × 24 × 30 | ~$3,317/month |
| Effective cost with ~50% spot | mixed | ~$2,200/month |

### Decision rationale

- **20% headroom over peak** for a single-AZ failure — HPA cannot
  scale into capacity that does not exist.
- **25% cluster reserve** on top of the pod requests for HPA burst,
  system daemons, and DaemonSets.
- **Spot for ~50% of capacity** because inference is stateless and
  tolerates node loss with pod disruption budgets. The remaining
  on-demand half floors the availability guarantee.
- **HPA on CPU utilization 70%** — CPU is the observed bottleneck at
  200 RPS/pod; scaling on RPS would require a custom metric server
  for no meaningful benefit here.
- **Alert on scaling latency p95 > 60 s** — if HPA lags, users see
  latency SLO violations before capacity arrives; the alert catches
  that lag independent of the CPU metric.

### Why this pattern generalizes

The same table works for GPU-backed inference; only the units
change (per-pod tokens/s instead of RPS, per-node GPUs instead of
vCPU, spot GPU availability instead of spot CPU). The module-level
SOLUTION.md notes that GPU capacity should be planned on a
quarterly cadence against a demand forecast, because reservation
windows and spot availability are the dominant cost lever (see
module-level SOLUTION.md, Decision 2, for the reasoning). Cost
attribution must go down to the model + team + environment
(Decision 4), which is what makes the per-replica $ figure
meaningful.

## Implementation

The worked example lives at [CAPACITY.md](CAPACITY.md); this section
describes how the plan is instantiated in the cluster:

- **HPA manifest** — CPU target 70% (matches the observed
  bottleneck at 200 RPS/pod), `minReplicas: 25`, `maxReplicas: 90`
  (peak + 20% AZ headroom).
- **Pod disruption budget** — `maxUnavailable: 10%` so spot node
  reclaims cannot drain more than a fraction at once.
- **Node groups** — one on-demand group across three AZs sized for
  50% of HPA-max, one spot group sized for the remaining 50%; the
  scheduler prefers spot via node affinity, on-demand carries the
  floor if spot is starved.
- **Cluster reserve** — request-based sizing multiplied by 1.25 to
  leave room for system daemons and HPA burst.
- **Alerts** — high-utilization (`pod_cpu > 80% for 10m`),
  low-utilization (`pod_cpu < 30% for 30m` — flags overprovision),
  and scaling-lag (`hpa_target_replicas − hpa_current_replicas > 0
  for 60s`) — the module-level SOLUTION.md, Decision 5, requires
  both over- and under-utilization signals.

## 3. Validation steps

- `modules/mod-008-production-ops/exercise-02/CAPACITY.md` exists
  and contains the sizing, cluster, cost, and triggers sections.
- The learner reproduces the arithmetic (min replicas, HPA max,
  cluster CPU) from their own inputs.
- Their submission includes both a high-utilization and a
  low-utilization alert (module-level SOLUTION.md, Decision 5).
- Their submission includes at least one HPA and one scaling-lag
  alert.

## 4. Rubric / review checklist

| Weight | Criterion | Evidence |
|---|---|---|
| 25% | Sizing math is correct (min, peak, headroom) and reproduces from inputs | Table matches inputs |
| 15% | Cluster shape fits the HPA-max pods with reserve headroom | Cluster totals ≥ pod totals × 1.25 |
| 15% | Cost estimate breaks out on-demand vs spot with a justification | Cost section labels each portion |
| 15% | HPA metric + threshold is defensible against measured bottleneck | HPA metric matches load-test bottleneck |
| 15% | Alerts include **both** over- and under-utilization | Two alert rules listed |
| 15% | Alerts include scaling-latency / lag signal, not only utilization | Scaling-lag alert present |

Pass = 80% weighted score with sizing math correct.

## 5. Common mistakes

- No AZ-failure headroom — cluster is exactly peak-sized, so a
  single-AZ outage collapses the SLO.
- Cluster reserve forgotten — pods fit "on paper" but HPA cannot
  actually schedule the last few because system pods took the room.
- Cost estimate assumes 100% on-demand OR 100% spot — the former
  wastes money at scale, the latter drops availability.
- HPA scales on the wrong metric (memory when the bottleneck is
  CPU, or vice versa) — measured, not guessed.
- Only a high-utilization alert; low-utilization waste is invisible
  until the finance review (module-level SOLUTION.md, Decision 5).
- Cost attribution missing the GPU bill — training jobs appear as a
  single mystery line item instead of per-team (module-level
  SOLUTION.md, common mistake #3).

## 6. References

- Module-level rationale: [../SOLUTION.md](../SOLUTION.md), esp.
  Decisions 2, 4, 5.
- NIST AI Risk Management Framework —
  <https://www.nist.gov/itl/ai-risk-management-framework> (Manage
  function: resource + capacity planning as an ongoing activity).
- Worked-example artifact: [CAPACITY.md](CAPACITY.md).
