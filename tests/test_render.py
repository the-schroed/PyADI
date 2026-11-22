from adi.render.pillow_backend import render_sphere, render_adu


def test_render_sphere_size():
    img = render_sphere(10, 5, 2, size=100)
    assert img.size == (100, 100)


def test_render_adu_size():
    img = render_adu(10, 5, 2, size=120)
    assert img.size == (120, 120)
