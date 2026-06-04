# Complete Monitoring Pipeline — Solution

Reference for [learning ex-05](https://github.com/ai-infra-curriculum/ai-infra-mlops-learning/blob/main/lessons/mod-003-model-monitoring/exercises/exercise-05-complete-monitoring-pipeline.md).

```bash
python monitor.py    # /metrics on :8000
# Wire to Prometheus from ../exercise-04/alerts.yml
```

In production, replace `load_current_window()` with a real query to your
inference log store (e.g., Kafka consumer, S3 partition scan, or warehouse query).
