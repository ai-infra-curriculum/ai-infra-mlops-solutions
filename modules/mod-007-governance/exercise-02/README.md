# Bias Mitigation — Solution

Reference for [learning ex-02](https://github.com/ai-infra-curriculum/ai-infra-mlops-learning/blob/main/lessons/mod-007-governance/exercises/exercise-02-bias-mitigation-strategies.md).

Three approaches:
- **Pre-processing**: `reweight_samples` — sample weights at training time
- **In-processing**: ExponentiatedGradient with a constraint (DemographicParity)
- **Post-processing**: ThresholdOptimizer — adjust per-group thresholds after training

Pick by constraint: if you can change the loss, in-process is most powerful.
If you can't retrain, post-process is your only option.
