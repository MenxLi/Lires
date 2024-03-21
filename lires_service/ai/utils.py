
import torch

def autoTorchDevice() -> str:
    if torch.cuda.is_available():
        return "cuda"
    else:
        return "cpu"