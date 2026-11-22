import numpy as np

from adi.frames import normalize, rpy_deg


def test_gimbal_lock():
    # pitch near 90
    _, p, _ = rpy_deg([0.7071, 0, 0.7071, 0])
    assert abs(p) > 80


def test_nonunit_input():
    q = normalize([2, 0, 0, 0])
    assert np.allclose(q, [1, 0, 0, 0])
