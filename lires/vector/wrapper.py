""" C++ wrapper """
import sysconfig, platform, dataclasses
import importlib

@dataclasses.dataclass(frozen=True)
class PlatformBasicConfig:
    ext_suffix = sysconfig.get_config_var("EXT_SUFFIX")
    obj_suffix = ".obj" if platform.system() == "Windows" else ".o"
    py_includes = sysconfig.get_config_var('INCLUDEPY')


class FixSizeAlg:
    """
    A class for calculating fixed-dim vectors
    """
    def __init__(self, dim: int):
        self.lib = importlib.import_module("lires.vector.lib.impl{}".format(dim))
    
    @property
    def dim(self) -> int:
        return self.lib.FEAT_DIM
    
    def encode(self, vec: list[float]) -> str:
        assert len(vec) == self.dim
        return self.lib.encode(vec)
    
    def decode(self, enc: str) -> list[float]:
        return self.lib.decode(enc)
    
    def similarityEnc(self, query: str, target: list[str]) -> list[float]:
        return self.lib.similarityBytesEnc(query, target)
    
    def topKIndices(self, scores: list[float], k: int) -> list[int]:
        assert len(scores) >= k
        return self.lib.topKIndices(scores, k)

if __name__ == "__main__":
    import random
    import numpy as np
    alg = FixSizeAlg(768)
    vec = [random.random() for _ in range(768)]
    vec2 = [ v*2 for v in vec]

    enc = alg.encode(vec)
    print(enc)

    dec = alg.decode(enc)
    print(dec)

    assert (np.array(vec) - np.array(dec) < 1e-6).all()

    dist = alg.similarityEnc(enc, [enc, enc, alg.encode(vec2)])
    print(dist)

    print(alg.topKIndices(dist, 3))

        
