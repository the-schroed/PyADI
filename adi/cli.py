"""CLI entry point."""
import argparse

import numpy as np

from .frames import (
    EULER_SEQUENCES,
    euler_to_quat,
    orbit_directions,
    quat_to_euler,
    rpy_deg,
)
from .render.pillow_backend import (
    add_text_panel,
    angle_panel_lines,
    render_adu,
    render_sphere,
)


def main():
    p = argparse.ArgumentParser(description="ADI image generator")
    p.add_argument("--quat", nargs=4, type=float, metavar=("W", "X", "Y", "Z"),
                   help="actual attitude quaternion, body->J2000 (overrides --roll/--pitch/--yaw)")
    p.add_argument("--angles", nargs=3, type=float, metavar=("A", "B", "C"),
                   help="actual attitude as Euler angles in degrees, in the order given by --seq")
    p.add_argument("--seq", metavar="SEQ",
                   help="Euler sequence for --angles, e.g. ZYX, XYZ, ZXZ; lowercase is extrinsic (default ZYX)")
    p.add_argument("--roll", type=float, default=0.0)
    p.add_argument("--pitch", type=float, default=0.0)
    p.add_argument("--yaw", type=float, default=0.0)
    p.add_argument("--cmd-quat", nargs=4, type=float, metavar=("W", "X", "Y", "Z"),
                   help="commanded attitude quaternion, body->J2000, shown as roll/pitch error bars")
    p.add_argument("--cmd-angles", nargs=3, type=float, metavar=("A", "B", "C"),
                   help="commanded attitude as Euler angles in degrees, in the order given by --cmd-seq")
    p.add_argument("--cmd-seq", metavar="SEQ",
                   help="Euler sequence for --cmd-angles (default ZYX)")
    p.add_argument("--cmd-clamp", type=float, default=20.0,
                   help="error (degrees) at which command bars pin to the edge (default 20)")
    p.add_argument("--cmd-tol", type=float, default=0.5,
                   help="error (degrees) below which command bars converge on the crosshair (default 0.5)")
    p.add_argument("--r", nargs=3, type=float, metavar=("X", "Y", "Z"),
                   help="position vector in J2000; with --v, marks prograde/retrograde/normal/anti-normal")
    p.add_argument("--v", nargs=3, type=float, metavar=("X", "Y", "Z"),
                   help="velocity vector in J2000; requires --r")
    p.add_argument("--out", default="adi.png")
    p.add_argument("--size", type=int, default=400)
    p.add_argument("--grid", type=int, default=15, help="grid spacing in degrees")
    p.add_argument("--no-labels", action="store_true", help="disable axis labels")
    p.add_argument("--2d", action="store_true", help="render classic 2D ADI instead of 3D")
    p.add_argument("--frame", choices=("j2000", "lvlh"), default="j2000",
                   help="frame of the attitude inputs and the view: J2000 (body->J2000) or LVLH (body->LVLH, "
                        "needs --r/--v for markers); default j2000")
    p.add_argument("--panel", action="store_true",
                   help="show Euler angles below the ADI, plus commanded and delta angles if --cmd-quat/--cmd-angles is given")
    args = p.parse_args()

    if (args.r is None) != (args.v is None):
        p.error("--r and --v must be given together")
    if args.cmd_clamp <= 0 or args.cmd_tol < 0:
        p.error("--cmd-clamp must be positive and --cmd-tol must be non-negative")
    overlays = args.cmd_quat is not None or args.cmd_angles is not None or args.r is not None
    if getattr(args, "2d") and overlays:
        p.error("--cmd-quat and --r/--v are only supported in the 3D view")

    if args.angles and args.quat:
        p.error("--angles and --quat are mutually exclusive")
    if args.cmd_angles and args.cmd_quat:
        p.error("--cmd-angles and --cmd-quat are mutually exclusive")
    if args.seq and not args.angles:
        p.error("--seq requires --angles")
    if args.cmd_seq and not args.cmd_angles:
        p.error("--cmd-seq requires --cmd-angles")
    for seq in (args.seq, args.cmd_seq):
        if seq and seq not in EULER_SEQUENCES:
            p.error(f"unknown Euler sequence {seq!r}; expected one of {', '.join(EULER_SEQUENCES)}")

    if args.angles:
        quat = euler_to_quat(args.angles, args.seq or "ZYX")
    elif args.quat:
        quat = np.asarray(args.quat, dtype=float)
    else:
        quat = euler_to_quat([args.yaw, args.pitch, args.roll], "ZYX")
    roll, pitch, yaw = rpy_deg(quat)

    cmd_quat = None
    if args.cmd_angles:
        cmd_quat = euler_to_quat(args.cmd_angles, args.cmd_seq or "ZYX")
    elif args.cmd_quat:
        cmd_quat = np.asarray(args.cmd_quat, dtype=float)

    if getattr(args, "2d"):
        img = render_adu(roll, pitch, yaw, size=args.size)
    else:
        command = rpy_deg(cmd_quat) if cmd_quat is not None else None
        markers = orbit_directions(args.r, args.v, frame=args.frame.upper()) if args.r else None
        img = render_sphere(roll, pitch, yaw, size=args.size, grid=args.grid, labels=not args.no_labels,
                            command=command, markers=markers,
                            bar_clamp=args.cmd_clamp, bar_tolerance=args.cmd_tol)
    if args.panel:
        seq = args.seq or "ZYX"
        cmd_angles = quat_to_euler(cmd_quat, seq) if cmd_quat is not None else None
        img = add_text_panel(img, angle_panel_lines(seq, quat_to_euler(quat, seq), cmd_angles))
    img.save(args.out)
    print(f"saved {args.out}  roll={roll:.2f} pitch={pitch:.2f} yaw={yaw:.2f}")


if __name__ == "__main__":
    main()
