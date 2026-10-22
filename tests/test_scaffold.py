"""Check scaffold imports and file logging without robot hardware."""

import asyncio
import logging
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock

from src.controllers.logging_controller import LoggingController
from src.robot_boi import RobotBoi


class ScaffoldTests(unittest.TestCase):
    def test_imports_have_no_filesystem_or_optional_dependency_side_effects(self):
        root = Path(__file__).resolve().parents[1]
        code = (
            f"import sys; sys.path.insert(0, {str(root)!r}); "
            "import src; import src.robot_boi; "
            "import src.controllers.AI_controller; "
            "import src.controllers.vision_controller; "
            "import src.controllers.speech_to_text_controller"
        )
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [sys.executable, "-B", "-c", code], cwd=directory,
                text=True, capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(list(Path(directory).iterdir()), [])

    def test_scaffold_shares_logger_and_refuses_unimplemented_launch(self):
        logger = Mock()
        robot = RobotBoi(logger=logger)
        self.assertIs(robot.speech.logger, logger)
        with self.assertRaisesRegex(NotImplementedError, "not implemented"):
            robot.launch()
        logger.assert_not_called()

    def test_logging_respects_requested_file_and_existing_root_configuration(self):
        root = logging.getLogger()
        original_handlers = list(root.handlers)
        original_level = root.level
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "one" / "log.txt"
            second = Path(directory) / "two.txt"
            with LoggingController(first) as a, LoggingController(second) as b:
                asyncio.run(a.log("first-only", logging.INFO))
                asyncio.run(b.log("second-only", logging.ERROR))
                asyncio.run(b.log("custom-level", 25))
            self.assertIn("first-only", first.read_text())
            self.assertNotIn("second-only", first.read_text())
            self.assertIn("second-only", second.read_text())
            self.assertNotIn("first-only", second.read_text())
            self.assertIn("WARNING", second.read_text())
            self.assertIn("custom-level", second.read_text())
            self.assertIsNone(a._handler.stream)
            self.assertIsNone(b._handler.stream)
        self.assertEqual(root.handlers, original_handlers)
        self.assertEqual(root.level, original_level)

    def test_bare_filename_is_supported(self):
        root = Path(__file__).resolve().parents[1]
        code = (
            f"import sys; sys.path.insert(0, {str(root)!r}); "
            "import asyncio, logging; "
            "from src.controllers.logging_controller import LoggingController; "
            "logger=LoggingController('test.log'); "
            "asyncio.run(logger.log('written', logging.INFO)); logger.close()"
        )
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [sys.executable, "-B", "-c", code], cwd=directory,
                text=True, capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("written", (Path(directory) / "test.log").read_text())


if __name__ == "__main__":
    unittest.main()
