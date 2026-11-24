# Attitude Determination Indicator (ADI)

Python-based ADI that ingests LVLH or Body→J2000 quaternions and renders
a 3D attitude sphere (Pillow-based, headless/web-friendly).

## Features
- Quaternion math (normalize, multiply, conjugate, frame conversion)
- RPY extraction (aerospace ZYX)
- 3D sphere rendering with grid, labels, configurable colors
- FastAPI demo with interactive controls
- CLI for single-shot image generation
- Tests + CI + docs

## Install
```
pip install -r requirements.txt
```

## Usage
```
python -m adi.cli --roll 20 --pitch -10 --yaw 30 --out adi.png
python -m adi.cli --quat 1 0 0 0 --out q.png
python -m adi.cli --2d --roll 20 --pitch -10 --out classic.png
python -m adi.cli --quat 0.99 0 0.1 0 --cmd-quat 1 0 0 0 --r 7000 0 0 --v 0 7.5 0 --out ops.png
```

Options:
- `--quat W X Y Z`: actual attitude, scalar-first, body→J2000 (overrides `--roll/--pitch/--yaw`)
- `--roll`, `--pitch`, `--yaw`: actual attitude as Euler angles in degrees (default 0)
- `--cmd-quat W X Y Z`: commanded attitude, body→J2000. Roll and pitch error are shown as bars: a vertical bar for roll and a horizontal bar for pitch. Each bar is offset toward the command, and converges onto the crosshair within 0.5°. Bars turn orange when the error exceeds the clamp, where they pin at the edge. Yaw is not shown.
- `--cmd-clamp DEG`: error at which bars clamp (default 20)
- `--cmd-tol DEG`: error below which bars converge and turn green (default 0.5)
- `--r X Y Z` and `--v X Y Z`: J2000 position and velocity. Draws markers for prograde, retrograde, normal and anti-normal. Give both or neither.
- `--2d`: render the classic 2D ADI instead of the 3D sphere (not compatible with `--cmd-quat` or `--r/--v`)
- `--size`: image size in pixels (default 400)
- `--grid`: grid spacing in degrees for the 3D sphere (default 15)
- `--no-labels`: hide axis and angle labels
- `--out`: output file path (default `adi.png`)

Orbit markers are computed as prograde = v̂, normal = (r × v)̂, with retrograde and anti-normal as their negatives. Markers are fixed to the reference (J2000) frame, so they move relative to the body features as the actual attitude changes. Markers on the far side of the ball are hidden.

The FastAPI demo (`uvicorn examples.fastapi_demo:app`) has controls for both the commanded attitude and orbit markers.

## FastAPI demo
```
uvicorn examples.fastapi_demo:app
```
Open http://localhost:8000

## Tests
```
pytest --cov=adi
```
