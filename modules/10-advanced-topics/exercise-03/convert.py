"""Convert a PyTorch model to ONNX + quantize for edge."""
import torch
import torch.nn as nn
from onnxruntime.quantization import quantize_dynamic, QuantType


class Tiny(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(4, 16), nn.ReLU(), nn.Linear(16, 3))

    def forward(self, x):
        return self.net(x)


def main():
    model = Tiny()
    model.train(False)
    dummy = torch.randn(1, 4)

    # Export
    torch.onnx.export(model, dummy, "tiny.onnx",
                       input_names=["input"], output_names=["output"],
                       dynamic_axes={"input": {0: "batch"}, "output": {0: "batch"}})

    # Quantize dynamic (int8)
    quantize_dynamic("tiny.onnx", "tiny.int8.onnx", weight_type=QuantType.QInt8)

    import os
    print(f"original: {os.path.getsize('tiny.onnx')} bytes")
    print(f"quantized: {os.path.getsize('tiny.int8.onnx')} bytes")


if __name__ == "__main__":
    main()
