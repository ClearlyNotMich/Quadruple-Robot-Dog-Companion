# Source layout

`robot_boi.py` holds the unfinished orchestration scaffold. It can be imported safely, but `RobotBoi.launch()` explicitly raises `NotImplementedError`; no integrated robot launch is available.

`controllers/logging_controller.py` implements file logging. `controllers/mapping_test.py` is an independently runnable, adapted LiDAR mapping example. The remaining controllers are placeholders or store a logger only.

Use package imports from the repository root, for example `from src.robot_boi import RobotBoi`. See the [project README](../README.md) for standard-library tests, mapping options and hardware limitations, and [third-party notices](../THIRD_PARTY.md) for the mapping example's origin.
