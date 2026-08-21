import json
from pathlib import Path

import pytest

from video_contact_sheet.input_source import is_url, resolve_local_input
from video_contact_sheet.media import MediaToolError, build_download_command, parse_probe_metadata, require_backend


def test_resolves_existing_local_video(tmp_path: Path):
    video = tmp_path / "video.mp4"
    video.write_bytes(b"video")

    assert resolve_local_input(video) == video.resolve()
    assert not is_url(str(video))
    assert is_url("https://www.bilibili.com/video/BV1xx")


def test_rejects_missing_local_video(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        resolve_local_input(tmp_path / "missing.mp4")


def test_accepts_any_http_or_https_url_for_yt_dlp_to_resolve():
    assert is_url("https://www.bilibili.com/video/BV1xx")
    assert is_url("https://example.invalid/video")


def test_builds_yt_dlp_command_without_shell_interpolation(tmp_path: Path):
    command = build_download_command("https://example.test/video?a=1&b=2", tmp_path)

    assert command[:3] == ["yt-dlp", "--no-playlist", "--output"]
    assert command[-1] == "https://example.test/video?a=1&b=2"


def test_parses_video_stream_metadata():
    metadata = parse_probe_metadata(
        json.dumps(
            {
                "format": {"duration": "12.5"},
                "streams": [{"codec_type": "audio"}, {"codec_type": "video", "width": 1920, "height": 1080}],
            }
        )
    )

    assert metadata.duration_ms == 12_500
    assert metadata.width == 1920
    assert metadata.height == 1080


def test_rejects_probe_result_without_video_stream():
    with pytest.raises(MediaToolError):
        parse_probe_metadata('{"format": {"duration": "1"}, "streams": []}')


def test_rejects_unknown_media_backend():
    with pytest.raises(MediaToolError):
        require_backend("unknown")
