import pytest
from fastapi import HTTPException
from PIL import Image

from examples import fastapi_demo


def call_endpoint(**overrides):
    params = {"roll": 0.0, "pitch": 0.0, "yaw": 0.0, "size": 120, "grid": 15,
              "cmd_roll": None, "cmd_pitch": None, "cmd_yaw": None,
              "rx": None, "ry": None, "rz": None, "vx": None, "vy": None, "vz": None}
    params.update(overrides)
    return fastapi_demo.adi_rpy(**params)


@pytest.fixture
def seen(monkeypatch):
    captured = {}

    def fake_sphere(roll, pitch, yaw, size, grid, command, markers):
        captured.update(command=command, markers=markers)
        return Image.new("RGB", (1, 1))

    monkeypatch.setattr(fastapi_demo, "render_sphere", fake_sphere)
    return captured


def test_defaults_render_without_overlays(seen):
    call_endpoint()

    assert seen == {"command": None, "markers": None}


def test_commanded_attitude_is_passed_through(seen):
    call_endpoint(cmd_roll=5.0, cmd_pitch=-3.0, cmd_yaw=10.0)

    assert seen["command"] == (5.0, -3.0, 10.0)
    assert seen["markers"] is None


def test_partial_commanded_attitude_defaults_missing_axes_to_zero(seen):
    call_endpoint(cmd_roll=7.0)

    assert seen["command"] == (7.0, 0.0, 0.0)


def test_orbit_inputs_produce_markers(seen):
    call_endpoint(rx=7000, ry=0, rz=0, vx=0, vy=7.5, vz=0)

    assert set(seen["markers"]) == {"prograde", "retrograde", "normal", "anti-normal"}
    assert seen["markers"]["prograde"].tolist() == [0.0, 1.0, 0.0]


def test_incomplete_orbit_inputs_are_ignored(seen):
    call_endpoint(rx=7000, ry=0, rz=0)

    assert seen["markers"] is None


def test_collinear_orbit_returns_400(seen):
    with pytest.raises(HTTPException) as exc:
        call_endpoint(rx=1, ry=0, rz=0, vx=2, vy=0, vz=0)

    assert exc.value.status_code == 400
    assert "collinear" in exc.value.detail
