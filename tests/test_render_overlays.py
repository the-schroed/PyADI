import numpy as np

from adi.frames import orbit_directions
from adi.render.pillow_backend import render_sphere

COMMAND_COLOR = (255, 170, 0)
PROGRADE_COLOR = (80, 255, 80)


def color_pixels(img, color):
    arr = np.asarray(img.convert("RGB")).astype(int)
    return np.argwhere(np.all(arr == color, axis=2))


def test_no_overlay_colors_by_default():
    img = render_sphere(0, 0, 0, size=200)

    assert len(color_pixels(img, COMMAND_COLOR)) == 0
    assert len(color_pixels(img, PROGRADE_COLOR)) == 0


def test_command_lines_use_command_color():
    img = render_sphere(0, 0, 0, size=200, command=(10, -5, 20))

    assert len(color_pixels(img, COMMAND_COLOR)) > 0


def test_prograde_marker_is_drawn_at_top_for_velocity_along_y():
    size = 200
    markers = orbit_directions([7000, 0, 0], [0, 7.5, 0])
    img = render_sphere(0, 0, 0, size=size, markers=markers)

    pixels = color_pixels(img, PROGRADE_COLOR)
    assert len(pixels) > 0
    # Prograde (+Y in J2000) should sit above the centre of the disk.
    rows = pixels[:, 0]
    assert rows.min() < size // 2 - 60


def test_back_side_markers_are_hidden():
    markers = {"anti-normal": np.array([0.0, 0.0, -1.0])}
    img = render_sphere(0, 0, 0, size=200, markers=markers)

    assert len(color_pixels(img, (255, 170, 255))) == 0
