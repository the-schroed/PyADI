import numpy as np
import pytest
from PIL import Image

from adi.cli import main


def run_cli(monkeypatch, *args):
    monkeypatch.setattr("sys.argv", ["adi", *args])
    main()


def test_rpy_writes_image(monkeypatch, tmp_path, capsys):
    out = tmp_path / "adi.png"
    run_cli(monkeypatch, "--roll", "20", "--pitch", "-10", "--yaw", "30", "--out", str(out), "--size", "120")

    img = Image.open(out)
    assert img.size == (120, 120)
    assert f"saved {out}" in capsys.readouterr().out


def test_quat_input_is_converted_to_rpy(monkeypatch, tmp_path, capsys):
    out = tmp_path / "q.png"
    run_cli(monkeypatch, "--quat", "1", "0", "0", "0", "--out", str(out), "--size", "100")

    assert "roll=0.00 pitch=0.00 yaw=0.00" in capsys.readouterr().out
    assert Image.open(out).size == (100, 100)


def test_2d_flag_renders_classic_adi(monkeypatch, tmp_path):
    out = tmp_path / "adu.png"
    run_cli(monkeypatch, "--2d", "--roll", "10", "--out", str(out), "--size", "150")

    assert Image.open(out).size == (150, 150)


def test_2d_flag_selects_render_adu(monkeypatch, tmp_path):
    calls = []
    monkeypatch.setattr("adi.cli.render_adu", lambda *a, **k: calls.append("adu") or Image.new("RGB", (1, 1)))
    monkeypatch.setattr("adi.cli.render_sphere", lambda *a, **k: calls.append("sphere") or Image.new("RGB", (1, 1)))

    run_cli(monkeypatch, "--2d", "--out", str(tmp_path / "a.png"))
    run_cli(monkeypatch, "--out", str(tmp_path / "b.png"))

    assert calls == ["adu", "sphere"]


@pytest.mark.parametrize("extra, expected", [
    ([], {"grid": 15, "labels": True}),
    (["--grid", "30"], {"grid": 30, "labels": True}),
    (["--no-labels"], {"grid": 15, "labels": False}),
])
def test_sphere_options_are_passed_through(monkeypatch, tmp_path, extra, expected):
    seen = {}

    def fake_sphere(roll, pitch, yaw, size, grid, labels, command, markers, bar_clamp, bar_tolerance):
        seen.update(size=size, grid=grid, labels=labels)
        return Image.new("RGB", (1, 1))

    monkeypatch.setattr("adi.cli.render_sphere", fake_sphere)
    run_cli(monkeypatch, "--out", str(tmp_path / "s.png"), "--size", "77", *extra)

    assert seen == dict(size=77, **expected)

def test_overlay_inputs_are_passed_to_renderer(monkeypatch, tmp_path):
    seen = {}

    def fake_sphere(roll, pitch, yaw, size, grid, labels, command, markers, bar_clamp, bar_tolerance):
        seen.update(command=command, markers=markers)
        return Image.new("RGB", (1, 1))

    monkeypatch.setattr("adi.cli.render_sphere", fake_sphere)
    run_cli(monkeypatch, "--out", str(tmp_path / "o.png"),
            "--cmd-quat", "1", "0", "0", "0",
            "--r", "7000", "0", "0", "--v", "0", "7.5", "0")

    assert seen["command"] == (0.0, 0.0, 0.0)
    assert np.allclose(seen["markers"]["prograde"], [0, 1, 0])
    assert np.allclose(seen["markers"]["normal"], [0, 0, 1])


def test_no_overlays_by_default(monkeypatch, tmp_path):
    seen = {}

    def fake_sphere(roll, pitch, yaw, size, grid, labels, command, markers, bar_clamp, bar_tolerance):
        seen.update(command=command, markers=markers)
        return Image.new("RGB", (1, 1))

    monkeypatch.setattr("adi.cli.render_sphere", fake_sphere)
    run_cli(monkeypatch, "--out", str(tmp_path / "o.png"))

    assert seen == {"command": None, "markers": None}


def test_r_without_v_is_an_error(monkeypatch, tmp_path, capsys):
    with pytest.raises(SystemExit):
        run_cli(monkeypatch, "--r", "1", "0", "0", "--out", str(tmp_path / "o.png"))
    assert "--r and --v must be given together" in capsys.readouterr().err


def test_overlays_rejected_with_2d(monkeypatch, tmp_path, capsys):
    with pytest.raises(SystemExit):
        run_cli(monkeypatch, "--2d", "--cmd-quat", "1", "0", "0", "0", "--out", str(tmp_path / "o.png"))
    assert "only supported in the 3D view" in capsys.readouterr().err



def test_bar_settings_are_passed_through(monkeypatch, tmp_path):
    seen = {}

    def fake_sphere(roll, pitch, yaw, size, grid, labels, command, markers, bar_clamp, bar_tolerance):
        seen.update(bar_clamp=bar_clamp, bar_tolerance=bar_tolerance)
        return Image.new("RGB", (1, 1))

    monkeypatch.setattr("adi.cli.render_sphere", fake_sphere)
    run_cli(monkeypatch, "--out", str(tmp_path / "o.png"), "--cmd-clamp", "10", "--cmd-tol", "0.1")

    assert seen == {"bar_clamp": 10.0, "bar_tolerance": 0.1}


def test_invalid_bar_settings_are_errors(monkeypatch, tmp_path, capsys):
    with pytest.raises(SystemExit):
        run_cli(monkeypatch, "--cmd-clamp", "0", "--out", str(tmp_path / "o.png"))
    assert "--cmd-clamp must be positive" in capsys.readouterr().err

def test_angles_with_sequence_match_quaternion(monkeypatch, tmp_path, capsys):
    run_cli(monkeypatch, "--angles", "30", "10", "20", "--seq", "XYZ", "--out", str(tmp_path / "a.png"), "--size", "60")
    from adi.frames import euler_to_quat, rpy_deg

    expected = rpy_deg(euler_to_quat([30, 10, 20], "XYZ"))
    assert f"roll={expected[0]:.2f}" in capsys.readouterr().out


def test_angles_default_to_zyx(monkeypatch, tmp_path, capsys):
    run_cli(monkeypatch, "--angles", "30", "10", "20", "--out", str(tmp_path / "a.png"), "--size", "60")

    assert "roll=20.00 pitch=10.00 yaw=30.00" in capsys.readouterr().out


def test_unknown_sequence_is_an_error(monkeypatch, tmp_path, capsys):
    with pytest.raises(SystemExit):
        run_cli(monkeypatch, "--angles", "1", "2", "3", "--seq", "XYY", "--out", str(tmp_path / "a.png"))
    assert "unknown Euler sequence" in capsys.readouterr().err


def test_seq_requires_angles(monkeypatch, tmp_path, capsys):
    with pytest.raises(SystemExit):
        run_cli(monkeypatch, "--seq", "XYZ", "--out", str(tmp_path / "a.png"))
    assert "--seq requires --angles" in capsys.readouterr().err


def test_angles_and_quat_are_exclusive(monkeypatch, tmp_path, capsys):
    with pytest.raises(SystemExit):
        run_cli(monkeypatch, "--angles", "1", "2", "3", "--quat", "1", "0", "0", "0", "--out", str(tmp_path / "a.png"))
    assert "mutually exclusive" in capsys.readouterr().err


def test_commanded_angles_are_converted(monkeypatch, tmp_path):
    seen = {}

    def fake_sphere(roll, pitch, yaw, size, grid, labels, command, markers, bar_clamp, bar_tolerance):
        seen["command"] = command
        return Image.new("RGB", (1, 1))

    monkeypatch.setattr("adi.cli.render_sphere", fake_sphere)
    run_cli(monkeypatch, "--out", str(tmp_path / "o.png"), "--cmd-angles", "0", "0", "15", "--cmd-seq", "ZYX")

    assert np.allclose(seen["command"], (15.0, 0.0, 0.0))

