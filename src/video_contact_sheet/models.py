from dataclasses import dataclass


@dataclass(frozen=True)
class SamplingConfig:
    fps: int = 1
    rows: int = 3
    columns: int = 3

    def __post_init__(self) -> None:
        for value in (self.fps, self.rows, self.columns):
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                raise ValueError("fps, rows, and columns must be positive integers")
        if self.fps > 1000:
            raise ValueError("fps must not exceed 1000 because timestamps use millisecond precision")

    @property
    def slots_per_sheet(self) -> int:
        return self.rows * self.columns


def sampling_timestamps_ms(frame_count: int, fps: int) -> list[int]:
    if not isinstance(frame_count, int) or frame_count < 0:
        raise ValueError("frame_count must be a non-negative integer")
    if not isinstance(fps, int) or isinstance(fps, bool) or fps <= 0:
        raise ValueError("fps must be a positive integer")
    return [(index * 1000) // fps for index in range(frame_count)]
