"""
test_validation.py
Unit tests for InputValidator, covering the required validation matrix:
  0 <= start time < stop time < 5
"""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

from validation import InputValidator


class TestInputValidator(unittest.TestCase):

    def setUp(self):
        self.validator = InputValidator()
        self.temp_exe = tempfile.NamedTemporaryFile(delete=False)
        self.temp_exe.close()
        os.chmod(self.temp_exe.name, 0o755)

    def tearDown(self):
        os.remove(self.temp_exe.name)

    def test_valid_times_pass(self):
        result = self.validator.validate_times("0", "4")
        self.assertTrue(result.is_valid)

    def test_start_time_negative_is_rejected(self):
        result = self.validator.validate_times("-1", "4")
        self.assertFalse(result.is_valid)
        self.assertIn("at least", result.error_message)

    def test_stop_time_at_max_is_rejected(self):
        result = self.validator.validate_times("0", "5")
        self.assertFalse(result.is_valid)
        self.assertIn("less than 5", result.error_message)

    def test_start_greater_than_or_equal_stop_is_rejected(self):
        result = self.validator.validate_times("3", "2")
        self.assertFalse(result.is_valid)
        self.assertIn("less than stop", result.error_message)

    def test_start_equal_stop_is_rejected(self):
        result = self.validator.validate_times("2", "2")
        self.assertFalse(result.is_valid)

    def test_non_integer_start_is_rejected(self):
        result = self.validator.validate_times("abc", "4")
        self.assertFalse(result.is_valid)
        self.assertIn("whole number", result.error_message)

    def test_blank_stop_is_rejected(self):
        result = self.validator.validate_times("0", "")
        self.assertFalse(result.is_valid)
        self.assertIn("blank", result.error_message)

    def test_missing_executable_path_is_rejected(self):
        result = self.validator.validate_executable_path("")
        self.assertFalse(result.is_valid)
        self.assertIn("choose an executable", result.error_message)

    def test_nonexistent_executable_path_is_rejected(self):
        result = self.validator.validate_executable_path("/no/such/file")
        self.assertFalse(result.is_valid)
        self.assertIn("does not exist", result.error_message)

    def test_valid_executable_path_passes(self):
        result = self.validator.validate_executable_path(self.temp_exe.name)
        self.assertTrue(result.is_valid)

    def test_validate_all_succeeds_with_good_input(self):
        result = self.validator.validate_all(self.temp_exe.name, "0", "4")
        self.assertTrue(result.is_valid)

    def test_validate_all_fails_with_bad_executable_before_checking_times(self):
        result = self.validator.validate_all("", "0", "4")
        self.assertFalse(result.is_valid)
        self.assertIn("executable", result.error_message)


if __name__ == "__main__":
    unittest.main()
