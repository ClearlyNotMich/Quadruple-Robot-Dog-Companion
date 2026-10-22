#!/usr/bin/env python3
"""
rpslam.py : BreezySLAM Python with SLAMTECH RP A1 Lidar

Copyright (C) 2018 Simon D. Levy

This code is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This code is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this code. If not, see <http://www.gnu.org/licenses/>.

Adapted from BreezySLAM examples/rpslam.py, commit
0aadd46aaf9708bf7d708e1b67d75ff99b9ea8a0. Modified on 2026-10-22 for explicit
configuration, lazy hardware imports, resource cleanup, and offline tests.
The original scan-update criterion and first-scan skip are preserved.
"""

import argparse

MAP_SIZE_PIXELS = 1000
MAP_SIZE_METERS = 10
LIDAR_DEVICE = "/dev/ttyUSB0"

# The original example reuses the last adequate scan when fewer samples arrive.
MIN_SAMPLES = 200


def _make_lidar(device):
    from rplidar import RPLidar

    return RPLidar(device)


def _make_slam(map_size_pixels, map_size_meters):
    from breezyslam.algorithms import RMHC_SLAM
    from breezyslam.sensors import RPLidarA1

    return RMHC_SLAM(RPLidarA1(), map_size_pixels, map_size_meters)


def _make_visualizer(map_size_pixels, map_size_meters, title):
    from roboviz import MapVisualizer

    return MapVisualizer(map_size_pixels, map_size_meters, title)


def run_mapping(
    device=LIDAR_DEVICE,
    min_samples=MIN_SAMPLES,
    *,
    lidar_factory=_make_lidar,
    slam_factory=_make_slam,
    visualizer_factory=_make_visualizer,
):
    """Run the mapping prototype and always release a created LiDAR connection.

    Calling this function with default factories opens the serial device and a
    viewer. Factories can be supplied for offline tests. Setup, scan, and viewer
    errors propagate after shutdown; interrupt handling belongs to ``main``.
    An adequate scan has strictly more than ``min_samples`` measurements.
    """
    if not isinstance(device, str) or not device.strip():
        raise ValueError("device must be a nonempty serial-device path")
    if (
        isinstance(min_samples, bool)
        or not isinstance(min_samples, int)
        or min_samples < 0
    ):
        raise ValueError("min_samples must be a nonnegative integer")

    lidar = lidar_factory(device)
    try:
        slam = slam_factory(MAP_SIZE_PIXELS, MAP_SIZE_METERS)
        viz = visualizer_factory(MAP_SIZE_PIXELS, MAP_SIZE_METERS, "SLAM")
        mapbytes = bytearray(MAP_SIZE_PIXELS * MAP_SIZE_PIXELS)
        iterator = lidar.iter_scans()
        previous_distances = None
        previous_angles = None

        # The first scan is discarded, as in the original hardware example.
        next(iterator)

        while True:
            items = list(next(iterator))
            distances = [item[2] for item in items]
            angles = [item[1] for item in items]

            if len(distances) > min_samples:
                slam.update(distances, scan_angles_degrees=angles)
                previous_distances = distances.copy()
                previous_angles = angles.copy()
            elif previous_distances is not None:
                slam.update(
                    previous_distances,
                    scan_angles_degrees=previous_angles,
                )

            x, y, theta = slam.getpos()
            slam.getmap(mapbytes)
            if not viz.display(x / 1000.0, y / 1000.0, theta, mapbytes):
                break
    finally:
        # A failed stop must not prevent closing the serial connection.
        try:
            lidar.stop()
        finally:
            lidar.disconnect()


def _nonnegative_int(value):
    try:
        number = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("must be a nonnegative integer") from error
    if number < 0:
        raise argparse.ArgumentTypeError("must be a nonnegative integer")
    return number


def _device_path(value):
    if not value.strip():
        raise argparse.ArgumentTypeError("must be a nonempty serial-device path")
    return value


def main(argv=None):
    """Parse explicit hardware-run options; importing this module does no I/O."""
    parser = argparse.ArgumentParser(
        description="Run the standalone RPLidar A1 mapping prototype (hardware required).",
    )
    parser.add_argument(
        "--device",
        default=LIDAR_DEVICE,
        type=_device_path,
        help=f"serial-device path (default: {LIDAR_DEVICE})",
    )
    parser.add_argument(
        "--min-samples",
        default=MIN_SAMPLES,
        type=_nonnegative_int,
        help=f"a scan must exceed this measurement count (default: {MIN_SAMPLES})",
    )
    args = parser.parse_args(argv)
    try:
        run_mapping(device=args.device, min_samples=args.min_samples)
    except KeyboardInterrupt:
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
