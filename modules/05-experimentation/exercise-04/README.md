# Progressive Rollout — Solution

Reference for [learning ex-04](https://github.com/ai-infra-curriculum/ai-infra-mlops-learning/blob/main/lessons/05-experimentation/exercises/exercise-04-progressive-rollout-with-istio.md).

Two options shown:
- `virtualservice.yaml` — Istio weighted routing (manual stepping)
- `argo-rollout.yaml` — Argo Rollouts (auto-stepping with success-rate analysis)

Pick Argo Rollouts if you have it; falls back to Istio VS for manual control.

Companion: [engineer-solutions/mod-106 ex-08](https://github.com/ai-infra-curriculum/ai-infra-engineer-solutions/tree/main/modules/mod-106-mlops/exercise-08-deployment-strategies).
