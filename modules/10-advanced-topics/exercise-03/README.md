# Edge ML Optimization — Solution

Reference for [learning ex-03](https://github.com/ai-infra-curriculum/ai-infra-mlops-learning/blob/main/lessons/10-advanced-topics/exercises/exercise-03-edge-ml-optimization.md).

ONNX export + dynamic int8 quantization. For large models, see also AWQ/GPTQ
(LLM-specific) and TensorRT (NVIDIA edge).

```bash
pip install torch onnx onnxruntime
python convert.py
```

Typical wins: 3-4× smaller, 2-3× faster inference, with < 1% accuracy loss
for most architectures.
