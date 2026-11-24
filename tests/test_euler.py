import numpy as np
import pytest

from adi.frames import EULER_SEQUENCES, euler_to_quat, quat_to_euler, rpy_deg

ANGLES = [23.0, 41.0, 67.0]


@pytest.mark.parametrize("seq", EULER_SEQUENCES)
def test_round_trip_for_every_sequence(seq):
    q = euler_to_quat(ANGLES, seq)
    back = quat_to_euler(q, seq)

    assert np.allclose(back, ANGLES, atol=1e-9)
    assert np.allclose(np.abs(np.dot(q, euler_to_quat(back, seq))), 1.0)


def test_all_24_sequences_are_supported():
    assert len(EULER_SEQUENCES) == 24
    assert len(set(EULER_SEQUENCES)) == 24


@pytest.mark.parametrize("seq", EULER_SEQUENCES)
def test_each_sequence_gives_a_unit_quaternion(seq):
    assert np.isclose(np.linalg.norm(euler_to_quat(ANGLES, seq)), 1.0)


def test_zyx_matches_rpy_convention():
    roll, pitch, yaw = 12.0, -7.0, 30.0
    q = euler_to_quat([yaw, pitch, roll], "ZYX")

    assert np.allclose(rpy_deg(q), [roll, pitch, yaw])


def test_intrinsic_and_extrinsic_differ():
    intrinsic = euler_to_quat(ANGLES, "XYZ")
    extrinsic = euler_to_quat(ANGLES, "xyz")

    assert not np.allclose(intrinsic, extrinsic)


def test_unknown_sequence_raises():
    with pytest.raises(ValueError, match="unknown Euler sequence"):
        euler_to_quat(ANGLES, "XYY")

