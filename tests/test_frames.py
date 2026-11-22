import numpy as np

from adi.frames import normalize, quat_conj, quat_mul, rpy_deg


def test_normalize():
    q = normalize([2, 0, 0, 0])
    assert np.allclose(q, [1, 0, 0, 0])


def test_identity_rpy():
    r, p, y = rpy_deg([1, 0, 0, 0])
    assert abs(r) < 1e-9 and abs(p) < 1e-9 and abs(y) < 1e-9


def test_quat_conj_mul():
    q = normalize([0.9239, 0, 0, 0.3827])
    qi = quat_conj(q)
    prod = quat_mul(q, qi)
    assert np.allclose(prod, [1, 0, 0, 0], atol=1e-6)
