# LLMOps with vLLM — Solution

Reference for [learning ex-01](https://github.com/ai-infra-curriculum/ai-infra-mlops-learning/blob/main/lessons/10-advanced-topics/exercises/exercise-01-llmops-with-vllm-serving.md).

```bash
./launch.sh
curl -X POST localhost:8000/v1/completions \
  -H 'content-type: application/json' \
  -d '{"model":"mistralai/Mistral-7B-Instruct-v0.2","prompt":"Write 3 facts about Saturn:","max_tokens":100}'
```

Companion: [engineer-solutions/mod-110 ex-03 (vllm-deep-dive)](https://github.com/ai-infra-curriculum/ai-infra-engineer-solutions/tree/main/modules/mod-110-llm-infrastructure/exercise-03-vllm-deep-dive) for tensor-parallel + LoRA hot-swap + speculative decoding benchmarks.
