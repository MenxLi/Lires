
import torch
from lires.core.utils import *     # needed, for chain import

def autoTorchDevice() -> str:
    if torch.cuda.is_available():
        return "cuda"
    # elif torch.has_mps:
    #     return "mps"
    else:
        return "cpu"