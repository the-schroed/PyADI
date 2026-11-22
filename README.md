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
```

## FastAPI demo
```
uvicorn examples.fastapi_demo:app
```
Open http://localhost:8000

## Tests
```
pytest --cov=adi
```
