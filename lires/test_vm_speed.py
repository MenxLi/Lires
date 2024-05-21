
import numpy as np
from lires.vector.wrapper import FixSizeAlg
from lires.utils import Timer


N_LEN = 20000

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

