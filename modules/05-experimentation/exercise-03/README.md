# Multi-Armed Bandits — Solution

Reference for [learning ex-03](https://github.com/ai-infra-curriculum/ai-infra-mlops-learning/blob/main/lessons/05-experimentation/exercises/exercise-03-multi-armed-bandits.md).

Thompson sampling is the production default: simple, regret-optimal, easy to
explain ("each arm gets a posterior; we sample from it"). Use when you don't
need rigorous p-values + can tolerate exploration.

```bash
python bandit.py
```
