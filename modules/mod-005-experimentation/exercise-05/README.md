# Complete Experimentation Platform — Solution

Reference for [learning ex-05](https://github.com/ai-infra-curriculum/ai-infra-mlops-learning/blob/main/lessons/mod-005-experimentation/exercises/exercise-05-complete-experimentation-platform.md).

Composition of the previous exercises:

```
gateway.py  ──▶  ab.assign()       (consistent hashing — ex-01)
               ▶  variant endpoint  (Argo Rollout — ex-04)
               ▶  exposure log      (Kafka → S3)
               
analyze.py  ◀──  exposure log       (ex-02 significance tests)
bandit.py   ◀──  exposure log       (ex-03 Thompson sampling — optional)
```

## Layout
```
exercise-05/
├── README.md
├── gateway.py            # serves predictions from variant + logs exposure
└── experiments.yaml       # config: experiment_id + variants + guardrails
```

See [engineer-solutions/mod-106 ex-09](https://github.com/ai-infra-curriculum/ai-infra-engineer-solutions/tree/main/modules/mod-106-mlops/exercise-09-ab-testing-infrastructure) for the working serving wrapper.
