# Pydantic Schema Validation — Solution

Reference for [learning ex-01](https://github.com/ai-infra-curriculum/ai-infra-mlops-learning/blob/main/lessons/mod-004-data-quality/exercises/exercise-01-pydantic-schema-validation.md).

Pydantic v2 enforces types, ranges, regex patterns, and cross-field invariants
at ingestion time. Combine with `validate_batch` to separate bad rows for a DLQ.

```python
from schema import UserEvent, validate_batch
valid, errors = validate_batch(rows, UserEvent)
```
