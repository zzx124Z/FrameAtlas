import pytest

from video_contact_sheet.models import SamplingConfig, sampling_timestamps_ms


def test_defaults_match_recommended_contact_sheet_settings():
    assert SamplingConfig() == SamplingConfig(fps=1, rows=3, columns=3)


@pytest.mark.parametrize("kwargs", [{"fps": 0}, {"rows": 0}, {"columns": -1}])
def test_rejects_non_positive_grid_settings(kwargs):
    with pytest.raises(ValueError):
        SamplingConfig(**kwargs)


def test_rejects_fps_above_millisecond_precision_limit():
    with pytest.raises(ValueError):
        SamplingConfig(fps=1001)


def test_sampling_uses_frame_index_without_accumulation_error():
    assert sampling_timestamps_ms(3, fps=2) == [0, 500, 1000]
