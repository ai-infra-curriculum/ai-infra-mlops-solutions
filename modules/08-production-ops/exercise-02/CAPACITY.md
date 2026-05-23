# Capacity Planning — Worked Example

Reference for [learning ex-02](https://github.com/ai-infra-curriculum/ai-infra-mlops-learning/blob/main/lessons/08-production-ops/exercises/exercise-02-capacity-planning-resource-management.md).

## Scenario: ML inference for product recommendations

- Target: 5K RPS sustained, 15K RPS peak, p95 < 150ms
- Single pod: 200 RPS at 80% CPU, 1 GB memory

## Sizing

| Metric | Calculation | Result |
|---|---|---|
| Min replicas | 5000 / 200 = 25 | 25 |
| Replicas at peak | 15000 / 200 = 75 | 75 (HPA max) |
| Headroom | +20% over peak (zone failure) | 90 HPA max |
| CPU request | 0.8 CPU / replica × 90 | 72 vCPU at peak |
| Memory request | 1 GB / replica × 90 | 90 GB at peak |

## Cluster

- 6 × m5.4xlarge (16 vCPU, 64 GB each) = 96 vCPU / 384 GB across AZs
- Headroom: 25% of cluster reserved for HPA + system overhead

## Cost

- m5.4xlarge: $0.768/hr on-demand
- 6 × $0.768 × 24 × 30 = $3,317/month
- Spot for ~50% of capacity: ~$2,200/month effective

## Triggers + alerts

- HPA: scale on CPU > 70% utilization
- VPA recommendation: revisit per-pod resources every 30d
- Alert: scaling latency p95 > 60s (means HPA is lagging)
