"""CLI entry point."""
import argparse

from .render.pillow_backend import render_sphere


def main():
    p = argparse.ArgumentParser(description="ADI image generator")
    p.add_argument("--quat", nargs=4, type=float, metavar=("W", "X", "Y", "Z"))
    p.add_argument("--roll", type=float, default=0.0)
    p.add_argument("--pitch", type=float, default=0.0)
    p.add_argument("--yaw", type=float, default=0.0)
    p.add_argument("--out", default="adi.png")
    p.add_argument("--size", type=int, default=400)
    p.add_argument("--grid", type=int, default=15, help="grid spacing in degrees")
    p.add_argument("--no-labels", action="store_true", help="disable axis labels")
    p.add_argument("--2d", action="store_true", help="render classic 2D ADI instead of 3D")
    args = p.parse_args()

    if args.quat:
        from .frames import rpy_deg
        roll, pitch, yaw = rpy_deg(args.quat)
    else:
        roll, pitch, yaw = args.roll, args.pitch, args.yaw

    from .render.pillow_backend import render_adu
    img = render_adu(roll, pitch, yaw, size=args.size) if args.__dict__.get("2d") else render_sphere(roll, pitch, yaw, size=args.size, grid=args.grid, labels=not args.no_labels)
    img.save(args.out)
    print(f"saved {args.out}  roll={roll:.2f} pitch={pitch:.2f} yaw={yaw:.2f}")


if __name__ == "__main__":
    main()
