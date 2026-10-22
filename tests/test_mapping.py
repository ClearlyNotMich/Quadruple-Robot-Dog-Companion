"""Offline tests: all mapping devices, algorithms, and displays are fakes."""

import contextlib
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

from src.controllers import mapping_test as mapping


def scan(count, offset=0):
    return [(10, offset + index, 100 + index) for index in range(count)]


class MappingTests(unittest.TestCase):
    def setUp(self):
        self.lidar = Mock()
        self.slam = Mock()
        self.slam.getpos.return_value = (1500, 2500, 30)
        self.viewer = Mock()
        self.viewer.display.return_value = False
        self.lidar_factory = Mock(return_value=self.lidar)
        self.slam_factory = Mock(return_value=self.slam)
        self.viewer_factory = Mock(return_value=self.viewer)

    def run_mapping(self, scans, **kwargs):
        self.lidar.iter_scans.return_value = iter(scans)
        mapping.run_mapping(
            lidar_factory=self.lidar_factory,
            slam_factory=self.slam_factory,
            visualizer_factory=self.viewer_factory,
            **kwargs,
        )

    def assert_shutdown(self):
        self.lidar.stop.assert_called_once_with()
        self.lidar.disconnect.assert_called_once_with()
        self.assertEqual(
            [call[0] for call in self.lidar.mock_calls[-2:]],
            ["stop", "disconnect"],
        )

    def test_first_scan_is_skipped_and_coordinates_are_converted(self):
        self.run_mapping(
            [scan(5, 90), scan(3, 10)], device="/fake/lidar", min_samples=2,
        )

        self.lidar_factory.assert_called_once_with("/fake/lidar")
        self.slam_factory.assert_called_once_with(1000, 10)
        self.viewer_factory.assert_called_once_with(1000, 10, "SLAM")
        self.slam.update.assert_called_once_with(
            [100, 101, 102], scan_angles_degrees=[10, 11, 12],
        )
        pose = self.viewer.display.call_args.args
        self.assertEqual(pose[:3], (1.5, 2.5, 30))
        self.assertIsInstance(pose[3], bytearray)
        self.assertEqual(len(pose[3]), 1000 * 1000)
        self.assertIs(self.slam.getmap.call_args.args[0], pose[3])
        self.assert_shutdown()

    def test_threshold_is_strict_and_no_update_precedes_an_adequate_scan(self):
        self.run_mapping([scan(4), scan(2)], min_samples=2)

        self.slam.update.assert_not_called()
        self.viewer.display.assert_called_once()
        self.assert_shutdown()

    def test_inadequate_scan_reuses_the_last_adequate_scan(self):
        self.viewer.display.side_effect = [True, False]
        self.run_mapping([scan(3, 90), scan(3, 10), scan(1, 70)], min_samples=2)

        self.assertEqual(self.slam.update.call_count, 2)
        self.assertEqual(
            self.slam.update.call_args_list[0], self.slam.update.call_args_list[1],
        )
        self.assert_shutdown()

    def test_invalid_configuration_does_not_construct_hardware(self):
        for options in (
            {"device": ""}, {"device": "  "}, {"device": None},
            {"min_samples": -1}, {"min_samples": 1.5},
            {"min_samples": True}, {"min_samples": "2"},
        ):
            with self.subTest(options=options), self.assertRaises(ValueError):
                self.run_mapping([], **options)
        self.lidar_factory.assert_not_called()
        self.slam_factory.assert_not_called()
        self.viewer_factory.assert_not_called()

    def test_slam_setup_failure_releases_lidar(self):
        self.slam_factory.side_effect = RuntimeError("slam setup failed")
        with self.assertRaisesRegex(RuntimeError, "slam setup failed"):
            self.run_mapping([])
        self.assert_shutdown()

    def test_viewer_setup_failure_releases_lidar(self):
        self.viewer_factory.side_effect = RuntimeError("viewer setup failed")
        with self.assertRaisesRegex(RuntimeError, "viewer setup failed"):
            self.run_mapping([])
        self.assert_shutdown()

    def test_scan_iterator_setup_failure_releases_lidar(self):
        self.lidar.iter_scans.side_effect = RuntimeError("scan setup failed")
        with self.assertRaisesRegex(RuntimeError, "scan setup failed"):
            self.run_mapping([])
        self.assert_shutdown()

    def test_scan_failure_and_interrupt_release_lidar(self):
        for error in (RuntimeError("scan failed"), KeyboardInterrupt()):
            with self.subTest(error=type(error).__name__):
                self.lidar.reset_mock()

                def failing_scans():
                    yield scan(1)
                    raise error

                with self.assertRaises(type(error)):
                    self.run_mapping(failing_scans())
                self.assert_shutdown()

    def test_empty_scan_stream_releases_lidar(self):
        with self.assertRaises(StopIteration):
            self.run_mapping([])
        self.assert_shutdown()

    def test_slam_update_failure_releases_lidar(self):
        self.slam.update.side_effect = RuntimeError("update failed")
        with self.assertRaisesRegex(RuntimeError, "update failed"):
            self.run_mapping([scan(1), scan(2)], min_samples=1)
        self.assert_shutdown()

    def test_display_failure_releases_lidar(self):
        self.viewer.display.side_effect = RuntimeError("display failed")
        with self.assertRaisesRegex(RuntimeError, "display failed"):
            self.run_mapping([scan(1), scan(1)])
        self.assert_shutdown()

    def test_disconnect_is_attempted_when_stop_fails(self):
        self.lidar.stop.side_effect = RuntimeError("stop failed")
        with self.assertRaisesRegex(RuntimeError, "stop failed"):
            self.run_mapping([scan(1), scan(1)])
        self.assert_shutdown()


class CommandLineTests(unittest.TestCase):
    def test_configuration_is_passed_to_explicit_run(self):
        with patch.object(mapping, "run_mapping") as run:
            status = mapping.main(["--device", "/fake/lidar", "--min-samples", "0"])
        self.assertEqual(status, 0)
        run.assert_called_once_with(device="/fake/lidar", min_samples=0)

    def test_interrupt_returns_conventional_exit_status(self):
        with patch.object(mapping, "run_mapping", side_effect=KeyboardInterrupt):
            self.assertEqual(mapping.main([]), 130)

    def test_help_and_invalid_arguments_do_not_run_hardware(self):
        for arguments, expected_status in (
            (["--help"], 0),
            (["--min-samples", "-1"], 2),
            (["--min-samples", "1.5"], 2),
            (["--device", "  "], 2),
        ):
            with self.subTest(arguments=arguments):
                with (
                    patch.object(mapping, "run_mapping") as run,
                    contextlib.redirect_stdout(io.StringIO()),
                    contextlib.redirect_stderr(io.StringIO()),
                    self.assertRaises(SystemExit) as raised,
                ):
                    mapping.main(arguments)
                self.assertEqual(raised.exception.code, expected_status)
                run.assert_not_called()

    def test_import_does_not_load_optional_dependencies_or_create_files(self):
        module_path = Path(mapping.__file__).resolve()
        script = """
import builtins
import runpy
import sys

real_import = builtins.__import__
def guarded_import(name, *args, **kwargs):
    if name.split('.')[0] in {'rplidar', 'breezyslam', 'roboviz'}:
        raise AssertionError('Optional dependency imported: ' + name)
    return real_import(name, *args, **kwargs)
builtins.__import__ = guarded_import
runpy.run_path(sys.argv[1], run_name='mapping_import_check')
"""
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [sys.executable, "-I", "-c", script, str(module_path)],
                cwd=directory,
                capture_output=True,
                text=True,
                check=False,
                timeout=10,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(list(Path(directory).iterdir()), [])


if __name__ == "__main__":
    unittest.main()
