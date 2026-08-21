"""
validation.py
Implements the validation matrix required by the task:
  - start must be >= 0
  - stop must be < 5
  - start must be < stop
  - inputs must be integers, not blank
  - executable path must be chosen and exist
"""
import os
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Represents the outcome of validating user input."""
    is_valid: bool
    error_message: str = ""


class InputValidator:
    """Validates raw string inputs from the GUI before launching a simulation."""

    MIN_START = 0
    MAX_STOP = 5

    def validate_executable_path(self, path: str) -> ValidationResult:
        if not path or not path.strip():
            return ValidationResult(False, "Please choose an executable.")
        if not os.path.isfile(path):
            return ValidationResult(False, "Selected executable does not exist.")
        if not os.access(path, os.X_OK):
            return ValidationResult(False, "Selected file is not executable.")
        return ValidationResult(True)

    def _parse_integer(self, raw_value: str, field_name: str):
        if raw_value is None or raw_value.strip() == "":
            return None, ValidationResult(False, f"{field_name} cannot be blank.")
        try:
            value = int(raw_value.strip())
            return value, ValidationResult(True)
        except ValueError:
            return None, ValidationResult(False, f"{field_name} must be a whole number.")

    def validate_times(self, start_raw: str, stop_raw: str) -> ValidationResult:
        start_value, start_check = self._parse_integer(start_raw, "Start time")
        if not start_check.is_valid:
            return start_check

        stop_value, stop_check = self._parse_integer(stop_raw, "Stop time")
        if not stop_check.is_valid:
            return stop_check

        if start_value < self.MIN_START:
            return ValidationResult(False, f"Start time must be at least {self.MIN_START}.")

        if stop_value >= self.MAX_STOP:
            return ValidationResult(False, f"Stop time must be less than {self.MAX_STOP}.")

        if start_value >= stop_value:
            return ValidationResult(False, "Start time must be less than stop time.")

        return ValidationResult(True)

    def validate_all(self, exe_path: str, start_raw: str, stop_raw: str) -> ValidationResult:
        """Runs every check; returns the first failure found, or success."""
        exe_check = self.validate_executable_path(exe_path)
        if not exe_check.is_valid:
            return exe_check

        return self.validate_times(start_raw, stop_raw)
