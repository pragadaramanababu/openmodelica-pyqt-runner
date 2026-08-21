"""
runner.py
Wraps QProcess to launch the compiled OpenModelica executable asynchronously,
streaming stdout/stderr back to the GUI without blocking it.
"""
from PyQt6.QtCore import QObject, QProcess, pyqtSignal

from models import SimulationConfig


class SimulationRunner(QObject):
    """Launches a SimulationConfig as a subprocess and emits signals as it progresses."""

    output_received = pyqtSignal(str)
    finished = pyqtSignal(int)
    error_occurred = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._process = None

    def is_running(self) -> bool:
        return self._process is not None and self._process.state() != QProcess.ProcessState.NotRunning

    def run(self, config: SimulationConfig) -> None:
        if self.is_running():
            self.error_occurred.emit("A simulation is already running.")
            return

        self._process = QProcess()
        self._process.setWorkingDirectory(_directory_of(config.executable_path))

        self._process.readyReadStandardOutput.connect(self._handle_stdout)
        self._process.readyReadStandardError.connect(self._handle_stderr)
        self._process.finished.connect(self._handle_finished)
        self._process.errorOccurred.connect(self._handle_process_error)

        self._process.start(config.executable_path, config.to_arguments())

    def stop(self) -> None:
        if self.is_running():
            self._process.kill()

    def _handle_stdout(self) -> None:
        data = self._process.readAllStandardOutput().data().decode(errors="replace")
        if data:
            self.output_received.emit(data)

    def _handle_stderr(self) -> None:
        data = self._process.readAllStandardError().data().decode(errors="replace")
        if data:
            self.output_received.emit(data)

    def _handle_finished(self, exit_code, exit_status) -> None:
        self.finished.emit(exit_code)

    def _handle_process_error(self, error) -> None:
        self.error_occurred.emit(f"Process error: {error}")


def _directory_of(file_path: str) -> str:
    import os
    return os.path.dirname(os.path.abspath(file_path))
