
import torch

def auto_torch_device() -> str:
    if torch.cuda.is_available():
        return "cuda"
    else:
        return "cpu"