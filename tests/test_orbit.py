import numpy as np
import pytest

from adi.frames import orbit_directions


def test_prograde_follows_velocity_and_normal_follows_h():
    d = orbit_directions([7000, 0, 0], [0, 7.5, 0])

    assert np.allclose(d["prograde"], [0, 1, 0])
    assert np.allclose(d["normal"], [0, 0, 1])


def test_retrograde_and_anti_normal_are_negatives():
    d = orbit_directions([7000, 0, 0], [0, 7.5, 0])

    assert np.allclose(d["retrograde"], -d["prograde"])
    assert np.allclose(d["anti-normal"], -d["normal"])


def test_results_are_unit_vectors_for_arbitrary_input():
    d = orbit_directions([1.0, 2.0, 3.0], [-0.5, 4.0, 0.2])

    for name, vec in d.items():
        assert np.isclose(np.linalg.norm(vec), 1.0), name


def test_normal_is_orthogonal_to_prograde():
    d = orbit_directions([1.0, 2.0, 3.0], [-0.5, 4.0, 0.2])

    assert np.isclose(np.dot(d["prograde"], d["normal"]), 0.0)


def test_collinear_inputs_raise():
    with pytest.raises(ValueError, match="collinear"):
        orbit_directions([1, 0, 0], [2, 0, 0])


def test_zero_velocity_raises():
    with pytest.raises(ValueError, match="zero velocity"):
        orbit_directions([1, 0, 0], [0, 0, 0])

from adi.frames import lvlh_matrix


def test_lvlh_axes_for_circular_orbit():
    # r along +X, v along +Y: nadir is -X, orbit normal is +Z, so Y(LVLH) = -Z.
    M = lvlh_matrix([7000, 0, 0], [0, 7.5, 0])

    assert np.allclose(M[2], [-1, 0, 0])
    assert np.allclose(M[1], [0, 0, -1])
    assert np.allclose(M[0], [0, 1, 0])


def test_lvlh_matrix_is_a_proper_rotation():
    M = lvlh_matrix([1.0, 2.0, 3.0], [-0.5, 4.0, 0.2])

    assert np.allclose(M @ M.T, np.eye(3))
    assert np.isclose(np.linalg.det(M), 1.0)


def test_prograde_is_along_track_x_in_lvlh():
    d = orbit_directions([7000, 0, 0], [0, 7.5, 0], frame="LVLH")

    assert np.allclose(d["prograde"], [1, 0, 0])
    assert np.allclose(d["normal"], [0, -1, 0])


def test_unknown_frame_raises():
    with pytest.raises(ValueError, match="unknown frame"):
        orbit_directions([1, 0, 0], [0, 1, 0], frame="ECI")
