"""
models.py
Holds the data structure for a single simulation run configuration.
"""
from dataclasses import dataclass


@dataclass
class SimulationConfig:
    """Represents one set of inputs the user wants to run the executable with."""
    executable_path: str
    start_time: int
    stop_time: int

    def to_arguments(self) -> list[str]:
        """Builds the command-line argument list to pass to the executable."""
        return [
            f"-startTime={self.start_time}",
            f"-stopTime={self.stop_time}",
        ]
