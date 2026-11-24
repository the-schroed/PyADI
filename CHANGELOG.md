# Changelog

## Unreleased
- Added prograde, retrograde, normal and anti-normal markers, computed from J2000 position and velocity (`orbit_directions`, `--r/--v`).
- Added a commanded attitude option: roll and pitch error bars that converge onto the crosshair as the attitude reaches the command (`--cmd-quat`).
- FastAPI demo: new controls and query parameters for the commanded attitude and orbit markers. Invalid orbit input returns HTTP 400.
- `normalize()`: removed a dead branch with no behavior change.
- FastAPI demo: grid slider now starts at 15 to match its number input.
- Tests: gimbal-lock warning is expected explicitly, so test output is clean.
- README: documented CLI options, including `--2d` and `--quat`.

## 0.1.1
- Sphere renderer rewritten with numpy; about 30x faster at 800px. Output matches 0.1.0 except for single-level rounding differences in a few pixels.
- Horizon line now honors `horizon_color`.
- CLI: imports moved to module level; `--2d` flag read reliably.
- Added CLI tests; test coverage now covers the CLI.
- Added `.gitignore`; build, cache, and coverage artifacts are no longer tracked.

## 0.1.0
- Initial release: quaternion math, 3D ADI sphere, FastAPI demo, CLI, tests, docs.
