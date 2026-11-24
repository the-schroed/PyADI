# Changelog

## 0.1.1
- Sphere renderer rewritten with numpy; about 30x faster at 800px. Output matches 0.1.0 except for single-level rounding differences in a few pixels.
- Horizon line now honors `horizon_color`.
- CLI: imports moved to module level; `--2d` flag read reliably.
- Added CLI tests; test coverage now covers the CLI.
- Added `.gitignore`; build, cache, and coverage artifacts are no longer tracked.

## 0.1.0
- Initial release: quaternion math, 3D ADI sphere, FastAPI demo, CLI, tests, docs.
