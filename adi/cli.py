"""CLI entry point."""
import argparse

from .frames import orbit_directions, rpy_deg
from .render.pillow_backend import render_adu, render_sphere


def main():
    p = argparse.ArgumentParser(description="ADI image generator")
    p.add_argument("--quat", nargs=4, type=float, metavar=("W", "X", "Y", "Z"),
                   help="actual attitude quaternion, body->J2000 (overrides --roll/--pitch/--yaw)")
    p.add_argument("--roll", type=float, default=0.0)
    p.add_argument("--pitch", type=float, default=0.0)
    p.add_argument("--yaw", type=float, default=0.0)
    p.add_argument("--cmd-quat", nargs=4, type=float, metavar=("W", "X", "Y", "Z"),
                   help="commanded attitude quaternion, body->J2000, drawn as dashed lines")
    p.add_argument("--r", nargs=3, type=float, metavar=("X", "Y", "Z"),
                   help="position vector in J2000; with --v, marks prograde/retrograde/normal/anti-normal")
    p.add_argument("--v", nargs=3, type=float, metavar=("X", "Y", "Z"),
                   help="velocity vector in J2000; requires --r")
    p.add_argument("--out", default="adi.png")
    p.add_argument("--size", type=int, default=400)
    p.add_argument("--grid", type=int, default=15, help="grid spacing in degrees")
    p.add_argument("--no-labels", action="store_true", help="disable axis labels")
    p.add_argument("--2d", action="store_true", help="render classic 2D ADI instead of 3D")
    args = p.parse_args()

    if (args.r is None) != (args.v is None):
        p.error("--r and --v must be given together")
    overlays = args.cmd_quat is not None or args.r is not None
    if getattr(args, "2d") and overlays:
        p.error("--cmd-quat and --r/--v are only supported in the 3D view")

    if args.quat:
        roll, pitch, yaw = rpy_deg(args.quat)
    else:
        roll, pitch, yaw = args.roll, args.pitch, args.yaw

    if getattr(args, "2d"):
        img = render_adu(roll, pitch, yaw, size=args.size)
    else:
        command = rpy_deg(args.cmd_quat) if args.cmd_quat else None
        markers = orbit_directions(args.r, args.v) if args.r else None
        img = render_sphere(roll, pitch, yaw, size=args.size, grid=args.grid, labels=not args.no_labels,
                            command=command, markers=markers)
    img.save(args.out)
    print(f"saved {args.out}  roll={roll:.2f} pitch={pitch:.2f} yaw={yaw:.2f}")


if __name__ == "__main__":
    main()
