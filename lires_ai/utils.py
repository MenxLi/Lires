
import torch
from typing import Callable, Optional
from logging.handlers import RotatingFileHandler
import sys, os, time, logging

def autoTorchDevice() -> str:
    if torch.cuda.is_available():
        return "cuda"
    # elif torch.has_mps:
    #     return "mps"
    else:
        return "cpu"