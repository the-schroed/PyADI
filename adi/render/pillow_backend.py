"""Pillow backend: render an ADI to a PIL Image."""
import math
from PIL import Image, ImageDraw, ImageFont
from scipy.spatial.transform import Rotation
import numpy as np


def _shade(base, n, light=(0.4, 0.6, 0.7)):
    dot = max(0.0, n[0]*light[0] + n[1]*light[1] + n[2]*light[2])
    f = 0.35 + 0.65 * dot
    return tuple(int(c * f) for c in base)


def render_sphere(roll, pitch, yaw=0.0, size=400, bg=(10, 10, 20), grid=15, labels=True,
                  sky=(70, 130, 220), ground=(140, 90, 45), grid_color=(200, 200, 200),
                  label_color=(220, 220, 220), horizon_color=(255, 255, 255)):
    """Render a 3D ADI sphere to a PIL Image.

    Parameters
    ----------
    roll, pitch, yaw : float
        Euler angles in degrees.
    size : int
        Image size in pixels.
    bg : tuple
        Background color.
    grid : int
        Grid spacing in degrees.
    labels : bool
        Whether to draw labels.
    sky, ground, grid_color, label_color, horizon_color : tuple
        Colors.

    Returns
    -------
    PIL.Image.Image
    """
    img = Image.new("RGB", (size, size), bg)
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None
    cx, cy = size // 2, size // 2
    r = size // 2 - 10

    # rotation body->inertial from RPY (aerospace ZYX)
    R = Rotation.from_euler("ZYX", [yaw, pitch, roll], degrees=True).as_matrix()

    pass
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            dx = (x - cx) / r
            dy = (y - cy) / r
            rr2 = dx * dx + dy * dy
            if rr2 > 1.0:
                continue
            dz = math.sqrt(max(0.0, 1.0 - rr2))
            # point on sphere in view coords; normal = point
            p_view = np.array([dx, -dy, dz])  # y up
            # body coords
            p_body = R.T @ p_view
            color_base = sky if p_body[2] >= 0 else ground
            color = _shade(color_base, p_view)
            img.putpixel((x, y), color)

    # outline
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(220, 220, 220), width=2)

    # horizon great circle: points with body z = 0
    pts = []
    for i in range(361):
        ang = math.radians(i)
        # circle in body xy-plane
        bx, by, bz = math.cos(ang), math.sin(ang), 0.0
        p_body = np.array([bx, by, bz])
        p_view = R @ p_body
        if p_view[2] < 0:
            continue
        x = cx + p_view[0] * r
        y = cy - p_view[1] * r
        pts.append((x, y))
    # draw as polyline segments (breaks when z<0)
    seg = []
    for i in range(361):
        ang = math.radians(i)
        bx, by, bz = math.cos(ang), math.sin(ang), 0.0
        p_body = np.array([bx, by, bz])
        p_view = R @ p_body
        if p_view[2] < 0:
            if len(seg) > 1:
                draw.line(seg, fill=horizon_color, width=2)
            seg = []
            continue
        x = cx + p_view[0] * r
        y = cy - p_view[1] * r
        seg.append((x, y))
    if len(seg) > 1:
        draw.line(seg, fill=(255, 255, 255), width=2)

    # latitude/longitude grid on sphere
    pass
    # parallels (latitude)
    for lat in range(-90, 91, grid):
        la = math.radians(lat)
        seg = []
        prev_z = None
        for i in range(361):
            lo = math.radians(i)
            bx = math.cos(la) * math.cos(lo)
            by = math.cos(la) * math.sin(lo)
            bz = math.sin(la)
            p_view = R @ np.array([bx, by, bz])
            if p_view[2] < 0:
                if len(seg) > 1:
                    draw.line(seg, fill=grid_color, width=1)
                seg = []
                prev_z = p_view[2]
                continue
            seg.append((cx + p_view[0] * r, cy - p_view[1] * r))
            prev_z = p_view[2]
        if len(seg) > 1:
            draw.line(seg, fill=grid_color, width=1)
        # elevation labels on four meridians for every 30 deg latitude
        if labels and (lat % 30 == 0):
            for lon in (0, 90, 180, 270):
                bx = math.cos(math.radians(lat)) * math.cos(math.radians(lon))
                by = math.cos(math.radians(lat)) * math.sin(math.radians(lon))
                bz = math.sin(math.radians(lat))
                pv = R @ np.array([bx, by, bz])
                if pv[2] >= 0:
                    t = R @ np.array([-math.sin(math.radians(lon)), math.cos(math.radians(lon)), 0.0])
                    ang = math.degrees(math.atan2(-t[1], t[0]))
                    tmp = Image.new("RGBA", (40, 16), (0, 0, 0, 0))
                    ImageDraw.Draw(tmp).text((0, 0), str(lat), fill=label_color, font=font)
                    bb = tmp.getbbox()
                    if bb:
                        tmp = tmp.crop(bb)
                        rot = tmp.rotate(-yaw, expand=True, resample=Image.BICUBIC)
                        ix = int(cx + pv[0]*r - rot.width/2)
                        iy = int(cy - pv[1]*r - rot.height/2)
                        img.paste(rot, (ix, iy), rot)
    # meridians (longitude)
    for lo in range(0, 360, grid):
        lo_r = math.radians(lo)
        seg = []
        prev_z = None
        for i in range(-90, 91):
            la = math.radians(i)
            bx = math.cos(la) * math.cos(lo_r)
            by = math.cos(la) * math.sin(lo_r)
            bz = math.sin(la)
            p_view = R @ np.array([bx, by, bz])
            if p_view[2] < 0:
                if len(seg) > 1:
                    draw.line(seg, fill=grid_color, width=1)
                seg = []
                prev_z = p_view[2]
                continue
            seg.append((cx + p_view[0] * r, cy - p_view[1] * r))
            prev_z = p_view[2]
        if len(seg) > 1:
            draw.line(seg, fill=grid_color, width=1)
        # longitude label for every meridian
        if labels:
            bx = math.cos(0) * math.cos(math.radians(lo))
            by = math.cos(0) * math.sin(math.radians(lo))
            bz = 0.0
            pv = R @ np.array([bx, by, bz])
            if pv[2] >= 0:
                t = R @ np.array([0.0, 0.0, 1.0])
                ang = math.degrees(math.atan2(-t[1], t[0]))
                tmp = Image.new("RGBA", (40, 16), (0, 0, 0, 0))
                ImageDraw.Draw(tmp).text((0, 0), str(lo), fill=label_color, font=font)
                bb = tmp.getbbox()
                if bb:
                    tmp = tmp.crop(bb)
                    rot = tmp.rotate(-yaw, expand=True, resample=Image.BICUBIC)
                    ix = int(cx + pv[0]*r - rot.width/2)
                    iy = int(cy - pv[1]*r - rot.height/2)
                    img.paste(rot, (ix, iy), rot)

    # billboard labels (screen-upright) projected onto sphere
    if labels:
        try:
            font = ImageFont.load_default()
        except Exception:
            font = None
        label_items = [("X", (1, 0, 0)), ("Y", (0, 1, 0)), ("Z", (0, 0, 1)),
                       ("-X", (-1, 0, 0)), ("-Y", (0, -1, 0)), ("-Z", (0, 0, -1))]
        for text, vec in label_items:
            p_view = R @ np.array(vec, dtype=float)
            if p_view[2] < 0:
                continue
            x = cx + p_view[0] * (r + 8)
            y = cy - p_view[1] * (r + 8)
            draw.text((x, y), text, fill=(255, 255, 255), font=font)

    # crosshair
    draw.line((cx - 15, cy, cx + 15, cy), fill=(255, 255, 0), width=2)
    draw.line((cx, cy - 15, cx, cy + 15), fill=(255, 255, 0), width=2)

    try:
        font = ImageFont.load_default()
    except Exception:
        font = None
    draw.text((10, 10), f"Roll {roll:+.1f}  Pitch {pitch:+.1f}  Yaw {yaw:+.1f}", fill=(255, 255, 255), font=font)
    return img


def render_adu(roll, pitch, yaw=0.0, size=400, bg=(20, 20, 30)):
    # keep original 2D ADI
    img = Image.new("RGB", (size, size), bg)
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None
    cx, cy = size // 2, size // 2
    r = size // 2 - 10
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(200, 200, 200), width=2)

    roll_rad = math.radians(roll)
    pitch_px = pitch * 4.0
    sky_top = (100, 170, 230); sky_bot = (40, 90, 160)
    gnd_top = (170, 110, 60); gnd_bot = (90, 55, 30)
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            if (x - cx) ** 2 + (y - cy) ** 2 > r * r:
                continue
            dx = x - cx; dy = y - cy
            v = -dx * math.sin(roll_rad) + dy * math.cos(roll_rad)
            dist = math.hypot(dx, dy) / r
            shade = 1.0 - 0.35 * dist
            if v < -pitch_px:
                t = (v + r) / (2 * r)
                base = tuple(int(sky_top[i] * (1 - t) + sky_bot[i] * t) for i in range(3))
            else:
                t = (v + r) / (2 * r)
                base = tuple(int(gnd_top[i] * (1 - t) + gnd_bot[i] * t) for i in range(3))
            color = tuple(int(c * shade) for c in base)
            img.putpixel((x, y), color)

    pts = []
    for t in range(-r, r + 1):
        u = t; v = -pitch_px
        x = cx + u * math.cos(roll_rad) + v * math.sin(roll_rad)
        y = cy + u * math.sin(roll_rad) - v * math.cos(roll_rad)
        if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
            pts.append((x, y))
    if len(pts) > 1:
        draw.line(pts, fill=(255, 255, 255), width=2)

    for deg in range(-30, 31, 5):
        if deg == 0:
            continue
        v0 = -pitch_px + (deg * 4.0)
        def to_xy(u, v):
            x = cx + u * math.cos(roll_rad) + v * math.sin(roll_rad)
            y = cy + u * math.sin(roll_rad) - v * math.cos(roll_rad)
            return (x, y)
        p1 = to_xy(-60, v0); p2 = to_xy(60, v0)
        draw.line((p1[0], p1[1], p2[0], p2[1]), fill=(255, 255, 255), width=1)
        draw.text((p2[0] + 4, p2[1]), str(deg), fill=(255, 255, 255))

    draw.line((cx - 31, cy + 1, cx - 11, cy + 1), fill=(80, 80, 0), width=3)
    draw.line((cx + 9, cy + 1, cx + 29, cy + 1), fill=(80, 80, 0), width=3)
    draw.line((cx - 30, cy, cx - 10, cy), fill=(255, 255, 0), width=3)
    draw.line((cx + 10, cy, cx + 30, cy), fill=(255, 255, 0), width=3)
    draw.line((cx, cy - 5, cx, cy + 5), fill=(255, 255, 0), width=3)

    for deg in (-60, -30, -20, -10, 0, 10, 20, 30, 60):
        a = math.radians(deg)
        x1 = cx + (r - 12) * math.sin(a)
        y1 = cy - (r - 12) * math.cos(a)
        x2 = cx + r * math.sin(a)
        y2 = cy - r * math.cos(a)
        draw.line((x1, y1, x2, y2), fill=(255, 255, 255), width=2)

    ba = math.radians(roll)
    px = cx + (r - 6) * math.sin(ba)
    py = cy - (r - 6) * math.cos(ba)
    draw.polygon([(px, py), (px - 6, py + 10), (px + 6, py + 10)], fill=(255, 255, 0))

    try:
        font = ImageFont.load_default()
    except Exception:
        font = None
    draw.text((10, 10), f"Roll {roll:+.1f}  Pitch {pitch:+.1f}  Yaw {yaw:+.1f}", fill=(255, 255, 255), font=font)
    return img


def render(q, size=400, mode="3d", grid=15, labels=True):
    from ..frames import rpy_deg
    roll, pitch, yaw = rpy_deg(q)
    if mode == "3d":
        return render_sphere(roll, pitch, yaw, size=size, grid=grid, labels=labels)
    return render_adu(roll, pitch, yaw, size=size)
