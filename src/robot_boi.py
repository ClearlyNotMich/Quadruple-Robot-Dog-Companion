"""Unfinished robot orchestration scaffold, retained for project context."""

from .controllers.logging_controller import LoggingController
from .controllers.speech_to_text_controller import SpeechToTextController


class RobotBoi:
    """Hold prototype components without claiming an implemented robot loop."""

    def __init__(self, logger=None):
        self.mode = None
        self.logger = logger if logger is not None else LoggingController()
        self.speech = SpeechToTextController(session=self)

    def launch(self):
        """Fail explicitly until the robot orchestration is implemented."""
        raise NotImplementedError(
            "Robot orchestration is not implemented in this prototype. "
            "The standalone mapping example is documented in README.md."
        )
