from pathlib import Path
import pytest

from video_contact_sheet.cli import _video_id, build_parser, estimate_sheet_count
from video_contact_sheet.models import SamplingConfig


def test_cli_defaults_to_recommended_sampling_settings(tmp_path: Path):
    arguments = build_parser().parse_args([str(tmp_path / "video.mp4")])

    assert arguments.fps == 1
    assert arguments.rows == 3
    assert arguments.columns == 3
    assert arguments.output == Path("video-reference")
    assert arguments.backend == "opencv"


def test_estimates_number_of_contact_sheets_before_extraction():
    assert estimate_sheet_count(3_600_000, fps=1, slots_per_sheet=9) == 400


def test_parser_rejects_invalid_sampling_values(tmp_path: Path):
    arguments = build_parser().parse_args([str(tmp_path / "video.mp4"), "--fps", "0"])
    with pytest.raises(ValueError):
        SamplingConfig(fps=arguments.fps, rows=arguments.rows, columns=arguments.columns)


def test_url_video_ids_include_a_stable_source_specific_suffix():
    assert _video_id("https://one.example/a") != _video_id("https://two.example/a")
