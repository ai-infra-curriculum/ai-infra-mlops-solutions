# Model Registry Lifecycle — Solution

Reference for [learning ex-02](https://github.com/ai-infra-curriculum/ai-infra-mlops-learning/blob/main/lessons/02-experiment-tracking/exercises/exercise-02-model-registry-lifecycle-management.md).

Companion: [engineer-solutions/mod-106 ex-03](https://github.com/ai-infra-curriculum/ai-infra-engineer-solutions/tree/main/modules/mod-106-mlops/exercise-03-model-registry-promotion) for full audit log + Slack approval.

```bash
python promote.py iris-rf 5 --to staging
python promote.py iris-rf 5 --to production    # gated on accuracy delta
```
