import numpy as np

from adi.frames import orbit_directions
from adi.render.pillow_backend import render_sphere

BAR_COLOR = (0, 255, 255)
CLAMPED_COLOR = (255, 140, 0)
CONVERGED_COLOR = (80, 255, 80)
PROGRADE_COLOR = (80, 255, 80)
SIZE = 200


def color_pixels(img, color):
    arr = np.asarray(img.convert("RGB")).astype(int)
    return np.argwhere(np.all(arr == color, axis=2))


def test_no_overlays_by_default():
    img = render_sphere(0, 0, 0, size=SIZE)

    for color in (BAR_COLOR, CLAMPED_COLOR, CONVERGED_COLOR, PROGRADE_COLOR):
        assert len(color_pixels(img, color)) == 0


def test_converged_bars_sit_on_crosshair():
    img = render_sphere(10, -5, 20, size=SIZE, command=(10, -5, 20))

    cx = cy = SIZE // 2
    assert img.getpixel((cx, cy - 20)) == CONVERGED_COLOR
    assert img.getpixel((cx - 20, cy)) == CONVERGED_COLOR


def test_yaw_error_does_not_move_bars():
    img = render_sphere(0, 0, 0, size=SIZE, command=(0, 0, 45))

    assert len(color_pixels(img, CONVERGED_COLOR)) > 0
    assert len(color_pixels(img, BAR_COLOR)) == 0


def test_roll_error_moves_vertical_bar_right_for_positive_error():
    img = render_sphere(0, 0, 0, size=SIZE, command=(5, 0, 0))

    pixels = color_pixels(img, BAR_COLOR)
    assert len(pixels) > 0
    assert pixels[:, 1].mean() > SIZE // 2


def test_pitch_error_moves_horizontal_bar_up_for_positive_error():
    img = render_sphere(0, 0, 0, size=SIZE, command=(0, 5, 0))

    pixels = color_pixels(img, BAR_COLOR)
    assert len(pixels) > 0
    assert pixels[:, 0].mean() < SIZE // 2


def test_large_error_is_clamped_and_flagged():
    img = render_sphere(0, 0, 0, size=SIZE, command=(90, 0, 0))

    assert len(color_pixels(img, CLAMPED_COLOR)) > 0
    assert len(color_pixels(img, BAR_COLOR)) == 0


def test_roll_error_wraps_across_180():
    img = render_sphere(-179, 0, 0, size=SIZE, command=(179, 0, 0))

    # Going from -179 to 179 the short way is -2 degrees, not +358.
    pixels = color_pixels(img, BAR_COLOR)
    assert len(pixels) > 0
    assert pixels[:, 1].mean() < SIZE // 2


def test_prograde_marker_is_drawn_at_top_for_velocity_along_y():
    markers = orbit_directions([7000, 0, 0], [0, 7.5, 0])
    img = render_sphere(0, 0, 0, size=SIZE, markers=markers)

    pixels = color_pixels(img, PROGRADE_COLOR)
    assert len(pixels) > 0
    assert pixels[:, 0].min() < SIZE // 2 - 60


def test_back_side_markers_are_hidden():
    markers = {"anti-normal": np.array([0.0, 0.0, -1.0])}
    img = render_sphere(0, 0, 0, size=SIZE, markers=markers)

    assert len(color_pixels(img, (255, 170, 255))) == 0

def test_clamp_and_tolerance_are_adjustable():
    # 3 degrees of error: clamped at a 2 degree clamp, inside a 5 degree tolerance.
    tight = render_sphere(0, 0, 0, size=SIZE, command=(3, 0, 0), bar_clamp=2.0, bar_tolerance=0.1)
    assert len(color_pixels(tight, CLAMPED_COLOR)) > 0

    loose = render_sphere(0, 0, 0, size=SIZE, command=(3, 0, 0), bar_clamp=20.0, bar_tolerance=5.0)
    assert len(color_pixels(loose, CONVERGED_COLOR)) > 0
    assert len(color_pixels(loose, BAR_COLOR)) == 0

def test_add_text_panel_appends_below_original():
    from PIL import Image

    from adi.render.pillow_backend import add_text_panel

    base = Image.new("RGB", (50, 40), (255, 0, 0))
    out = add_text_panel(base, ["one", "two"])

    assert out.size[0] == 50
    assert out.size[1] > 40
    assert out.getpixel((0, 0)) == (255, 0, 0)
