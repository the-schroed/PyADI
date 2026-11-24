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

    def fake_sphere(roll, pitch, yaw, size, grid, labels):
        seen.update(size=size, grid=grid, labels=labels)
        return Image.new("RGB", (1, 1))

    monkeypatch.setattr("adi.cli.render_sphere", fake_sphere)
    run_cli(monkeypatch, "--out", str(tmp_path / "s.png"), "--size", "77", *extra)

    assert seen == dict(size=77, **expected)
