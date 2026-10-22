# Robot Dog Companion — HvA TI prototype

A Python prototype for an HvA Technical Informatics robot-companion project. This repository preserves controller scaffolding, an asynchronous logging helper and a standalone LiDAR mapping demonstration adapted from BreezySLAM.

The integrated robot is **not implemented in this snapshot**. The earlier description advertised ROS/Jetson integration, C++ object detection, speech recognition and optimized locomotion; the checked-in files do not demonstrate those capabilities. They are not presented here as completed features.

## What is here

| Component | Status |
| --- | --- |
| [LiDAR mapping example](src/controllers/mapping_test.py) | Adapts Simon D. Levy's BreezySLAM example to collect scans, update a map and display a pose. Requires compatible hardware and external libraries; not hardware-validated in this cleanup. |
| [Logging helper](src/controllers/logging_controller.py) | Writes asynchronous log messages to an explicit file, without reconfiguring the application root logger. |
| [Robot orchestration](src/robot_boi.py) | Scaffold. Construction connects the speech placeholder to the logger; `launch()` explicitly raises `NotImplementedError`. |
| AI, vision, motion, SLAM and text-to-speech controllers | Placeholders with no implemented control pipeline. The speech-to-text controller only holds a logger. |

There is no ROS package/launch configuration, C++ implementation, dependency lock, trained model or integrated hardware-control loop in the current tree.

## Inspect and test without hardware

Use Python 3.10 or newer. The checks below use only the standard library and simulated devices; they do not open a serial port, camera or microphone.

```bash
git clone https://github.com/ObviouslyNotMich/Quadruple-Robot-Dog-Companion.git
cd Quadruple-Robot-Dog-Companion
python -B -m unittest discover -s tests -v
python -m src.controllers.mapping_test --help
```

Importing the package and controllers starts no devices and creates no logs. Instantiating `LoggingController` explicitly creates its output directory/file; callers can close it or use it as a context manager.

## Standalone mapping demonstration

The historical mapping example expects an RPLidar A1-compatible device, the `rplidar` driver, BreezySLAM's `RMHC_SLAM`/`RPLidarA1`, and a `roboviz.MapVisualizer` implementation matching the historical API. A serial connection and graphical display are needed. These hardware dependencies are imported only when the demonstration is explicitly run.

After preparing compatible dependencies and connecting the device:

```bash
python -m src.controllers.mapping_test --device /dev/ttyUSB0 --min-samples 200
```

This command starts scanning; it does not drive the robot's legs or run a navigation controller. The map is 1,000 × 1,000 pixels over 10 × 10 metres. The first scan is skipped. A scan is accepted only when its sample count is strictly greater than the configured threshold; after a valid scan, an inadequate scan reuses the previous measurements, preserving the original demonstration's behavior. Closing the display or interrupting the process triggers device cleanup.

There is no validated deployment environment or tested dependency-version combination recorded for this snapshot. Follow the dependency projects' installation instructions and check compatibility on the target hardware. Passing the unit tests demonstrates software behavior with simulated dependencies, not robot operation or mapping accuracy.

## Contribution and provenance

The two original repository commits, dated 31 December 2024, are an import and a README edit attributed to Michal Kozdon (`ObviouslyNotMich`). They establish the repository import history, not sole authorship of every project component. A preserved source comment references planned integration of **Manar's depth-camera code**; that implementation is absent here. A detailed personal/team division of work has not yet been documented.

The mapping code closely follows **Simon D. Levy's BreezySLAM RPLidar example**. Its original copyright and LGPL-3.0-or-later notice have been restored; see [THIRD_PARTY.md](THIRD_PARTY.md) for the exact source and accompanying license texts. Other project files have no newly assigned blanket license.

The unused `data/audio/stream_.mp3` file was removed from the current tree at the owner's request. Its format and content could not be validated. The original Git history is preserved, including historical copies of that file.
