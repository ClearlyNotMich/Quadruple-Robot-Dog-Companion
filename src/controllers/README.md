# Controllers and examples

- `logging_controller.py`: asynchronous file logging with an explicitly owned handler; close it when finished.
- `mapping_test.py`: standalone BreezySLAM/RPLidar mapping example. It is not integrated into `SlamController` or `RobotBoi`.
- `speech_to_text_controller.py`: stores a session logger; it does not recognize speech.
- `AI_controller.py`, `motion_controller.py`, `slam_controller.py`, `system_controller.py`, `text_to_speech_controller.py`, `vision_controller.py`: implementation placeholders.

No controller is started by importing these modules. The vision placeholder retains the original note about Manar's depth-camera work without implying that code is included. See the [project README](../../README.md) and [third-party notices](../../THIRD_PARTY.md).
