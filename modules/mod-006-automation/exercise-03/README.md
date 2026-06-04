# Error Handling + Retries — Solution

Reference for [learning ex-03](https://github.com/ai-infra-curriculum/ai-infra-mlops-learning/blob/main/lessons/mod-006-automation/exercises/exercise-03-workflow-error-handling-retry-logic.md).

Three composable primitives:
- `@retry(...)` — exponential backoff + jitter
- `CircuitBreaker` — opens after N failures; sleeps `recovery_time_s`
- `send_to_dlq(...)` — last resort for poison-pill messages

Use Airflow's built-in retries for whole-task retry. Use these patterns for
within-task resilience (downstream API calls, flaky data fetches).
