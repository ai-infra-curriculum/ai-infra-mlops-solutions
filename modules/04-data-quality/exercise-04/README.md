# Profiling + Anomaly Detection — Solution

Reference for [learning ex-04](https://github.com/ai-infra-curriculum/ai-infra-mlops-learning/blob/main/lessons/04-data-quality/exercises/exercise-04-data-profiling-anomaly-detection.md).

```python
from profile import profile, diff_profiles
ref_p = profile(reference_df)
cur_p = profile(current_df)
alerts = diff_profiles(ref_p, cur_p)
```

Profile diffs catch the "silent" quality issues that GE rules miss because no
explicit rule covered the new failure mode.
