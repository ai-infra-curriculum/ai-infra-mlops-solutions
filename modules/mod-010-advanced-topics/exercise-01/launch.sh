#!/usr/bin/env bash
# Launch vLLM with prefix caching + structured-output support.
python -m vllm.entrypoints.openai.api_server \
  --model mistralai/Mistral-7B-Instruct-v0.2 \
  --enable-prefix-caching \
  --max-model-len 4096 \
  --port 8000
