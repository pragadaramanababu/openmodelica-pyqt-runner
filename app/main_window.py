"""
main_window.py
The main application window: 3 inputs, Browse button, Run/Stop controls,
live log panel, and validation before launch.
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QFileDialog, QMessageBox
)

from models import SimulationConfig
from validation import InputValidator
from runner import SimulationRunner


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulation Runner Workbench")
        self.setMinimumSize(600, 500)

        self.validator = InputValidator()
        self.runner = SimulationRunner()
        self.runner.output_received.connect(self._append_log)
        self.runner.finished.connect(self._on_finished)
        self.runner.error_occurred.connect(self._on_error)

        self._build_ui()

    def _build_ui(self) -> None:
        central = QWidget()
        layout = QVBoxLayout()

        exe_row = QHBoxLayout()
        self.exe_input = QLineEdit()
        self.exe_input.setPlaceholderText("Path to compiled executable")
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_for_executable)
        exe_row.addWidget(QLabel("Executable:"))
        exe_row.addWidget(self.exe_input)
        exe_row.addWidget(browse_btn)
        layout.addLayout(exe_row)

        time_row = QHBoxLayout()
        self.start_input = QLineEdit()
        self.start_input.setPlaceholderText("e.g. 0")
        self.stop_input = QLineEdit()
        self.stop_input.setPlaceholderText("e.g. 4")
        time_row.addWidget(QLabel("Start time:"))
        time_row.addWidget(self.start_input)
        time_row.addWidget(QLabel("Stop time:"))
        time_row.addWidget(self.stop_input)
        layout.addLayout(time_row)

        button_row = QHBoxLayout()
        self.run_button = QPushButton("Run")
        self.run_button.clicked.connect(self._on_run_clicked)
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self._on_stop_clicked)
        self.stop_button.setEnabled(False)
        button_row.addWidget(self.run_button)
        button_row.addWidget(self.stop_button)
        layout.addLayout(button_row)

        self.status_label = QLabel("Idle")
        layout.addWidget(self.status_label)

        layout.addWidget(QLabel("Log:"))
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        layout.addWidget(self.log_view)

        central.setLayout(layout)
        self.setCentralWidget(central)

    def _browse_for_executable(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Select executable")
        if path:
            self.exe_input.setText(path)

    def _on_run_clicked(self) -> None:
        exe_path = self.exe_input.text()
        start_raw = self.start_input.text()
        stop_raw = self.stop_input.text()

        result = self.validator.validate_all(exe_path, start_raw, stop_raw)
        if not result.is_valid:
            QMessageBox.warning(self, "Invalid input", result.error_message)
            return

        config = SimulationConfig(
            executable_path=exe_path,
            start_time=int(start_raw),
            stop_time=int(stop_raw),
        )

        self.log_view.clear()
        self.status_label.setText("Running...")
        self.run_button.setEnabled(False)
        self.stop_button.setEnabled(True)

        self.runner.run(config)

    def _on_stop_clicked(self) -> None:
        self.runner.stop()
        self.status_label.setText("Stopped by user")
        self._reset_buttons()

    def _append_log(self, text: str) -> None:
        self.log_view.append(text.rstrip())

    def _on_finished(self, exit_code: int) -> None:
        if exit_code == 0:
            self.status_label.setText("Finished successfully (exit code 0)")
        else:
            self.status_label.setText(f"Finished with errors (exit code {exit_code})")
        self._reset_buttons()

    def _on_error(self, message: str) -> None:
        QMessageBox.critical(self, "Error", message)
        self.status_label.setText("Error")
        self._reset_buttons()

    def _reset_buttons(self) -> None:
        self.run_button.setEnabled(True)
        self.stop_button.setEnabled(False)
