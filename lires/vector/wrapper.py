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
    
    def encode(self, vec: list[float]) -> bytes:
        assert len(vec) == self.dim
        return self.lib.encode(vec)
    
    def decode(self, enc: bytes) -> list[float]:
        return self.lib.decode(enc)
    
    def similarityEnc(self, query: bytes, target: list[bytes]) -> list[float]:
        return self.lib.similarityBytesEnc(query, target)
    
    def topKIndices(self, scores: list[float], k: int) -> list[int]:
        assert len(scores) >= k
        return self.lib.topKIndices(scores, k)


# Below is the test code ========================================
if __name__ == "__main__":
    import random
    import numpy as np
    from lires.utils import Timer

    alg = FixSizeAlg(768)
    vec = [random.random() for _ in range(768)]
    vec2 = [ v*2 for v in vec]

    enc = alg.encode(vec)
    dec = alg.decode(enc)

    assert (np.array(vec) - np.array(dec) < 1e-6).all()

    dist = alg.similarityEnc(enc, [enc, enc, alg.encode(vec2)])
    print(dist)

    print(alg.topKIndices(dist, 3))

    N_LEN = 10000

    alg = FixSizeAlg(768)

    q_np = np.random.rand(768)
    q_np_blob = q_np.tobytes()
    q_enc = alg.encode(q_np.tolist())
    q = alg.decode(q_enc)

    m_np = np.random.rand(N_LEN, 768)
    m_enc = [alg.encode(m) for m in m_np.tolist()]
    m = [alg.decode(m) for m in m_enc]
    m_np_blob = m_np.tobytes()

    def cosSim(v1: np.ndarray, m1: np.ndarray) -> np.ndarray:
        # v1: 1d array of size (d), m1: 2d array of size (n, d)
        # return : 1d array of size (n)
        return np.dot(m1, v1) / (np.linalg.norm(m1, axis=1) * np.linalg.norm(v1))

    with Timer("similarity") as t0:
        dist = alg.similarityEnc(q_enc, m_enc)
        t0 = t0.duration

    with Timer("similarity-np") as t1:
        dist_np = cosSim(q_np, m_np)
        t1 = t1.duration

    with Timer("similarity-np-blob") as t1:
        q_np_loaded = np.frombuffer(q_np_blob, dtype=np.float64)
        m_np_loaded = np.frombuffer(m_np_blob, dtype=np.float64).reshape(N_LEN, 768)
        dist_np = cosSim(q_np_loaded, m_np_loaded)
        t1 = t1.duration

    assert (np.array(dist) - dist_np < 1e-6).all()



            