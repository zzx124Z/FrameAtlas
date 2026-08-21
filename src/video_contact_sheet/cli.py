import argparse
import hashlib
import math
import re
import tempfile
import time
import json
from pathlib import Path
from urllib.parse import urlparse

from PIL import Image

from .input_source import is_url, resolve_local_input
from .media import (
    MediaToolError,
    download_video,
    extract_frame,
    extract_frame_opencv,
    probe_video,
    probe_video_opencv,
    require_backend,
    require_executable,
)
from .models import SamplingConfig, sampling_timestamps_ms
from .output import write_reference_package
from .render import render_contact_sheets


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create timestamped video contact sheets for multimodal reference.")
    parser.add_argument("input", help="Local video path or public HTTP(S) URL")
    parser.add_argument("--fps", type=int, default=1, help="Frames per second; default: 1")
    parser.add_argument("--rows", type=int, default=3, help="Grid rows; default: 3")
    parser.add_argument("--columns", type=int, default=3, help="Grid columns; default: 3")
    parser.add_argument("--output", type=Path, default=Path("video-reference"), help="Output parent directory")
    parser.add_argument("--overwrite", action="store_true", help="Replace an existing package")
    parser.add_argument("--backend", choices=("opencv", "ffmpeg"), default="opencv", help="Video decoding backend; default: opencv")
    parser.add_argument("--stage", choices=("all", "download", "analyze"), default="all", help="Pipeline stage; default: all")
    parser.add_argument("--download-dir", type=Path, default=Path("video-downloads"), help="Persistent download directory")
    parser.add_argument("--retry-preset", choices=("fast-fail", "balanced", "reliable"), default="balanced", help="URL download retry profile")
    parser.add_argument("--format-profile", choices=("balanced", "small"), default="balanced", help="URL download format profile")
    parser.add_argument("--timing", action="store_true", help="Print stage timings")
    parser.add_argument(
        "--parameter-source",
        choices=("explicit", "default"),
        default="explicit",
        help="How sampling parameters were selected",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    try:
        config = SamplingConfig(fps=arguments.fps, rows=arguments.rows, columns=arguments.columns)
        return _run(arguments, config)
    except (FileNotFoundError, MediaToolError, ValueError) as error:
        raise SystemExit(f"error: {error}") from error


def _run(arguments: argparse.Namespace, config: SamplingConfig) -> int:
    if arguments.stage == "download":
        _require_tools(arguments.input, arguments.backend, download_only=True)
        video, attempts, elapsed = _download_input(arguments)
        result = {"video": str(video), "attempts": attempts, "elapsed_ms": elapsed}
        print(json.dumps(result, indent=2))
        return 0
    _require_tools(arguments.input, arguments.backend)
    with tempfile.TemporaryDirectory(prefix="video-contact-sheet-") as temporary:
        temporary_dir = Path(temporary)
        if arguments.stage == "analyze":
            video = resolve_local_input(arguments.input)
            attempts = elapsed = None
        else:
            video, attempts, elapsed = _download_input(arguments, temporary_dir)
        started = time.perf_counter()
        phase_started = time.perf_counter()
        metadata = _probe_video(video, arguments.backend)
        probe_ms = round((time.perf_counter() - phase_started) * 1000)
        sheet_count = estimate_sheet_count(metadata.duration_ms, config.fps, config.slots_per_sheet)
        if sheet_count > 100:
            print(f"warning: this video will produce about {sheet_count} contact sheets", flush=True)
        frame_count = math.ceil(metadata.duration_ms * config.fps / 1000)
        timestamps = sampling_timestamps_ms(frame_count, config.fps)
        phase_started = time.perf_counter()
        frames = _extract_frames(video, timestamps, temporary_dir / "frames", arguments.backend)
        extract_ms = round((time.perf_counter() - phase_started) * 1000)
        video_id = _video_id(arguments.input)
        phase_started = time.perf_counter()
        sheets = render_contact_sheets(frames, timestamps, config, video_id=video_id)
        render_ms = round((time.perf_counter() - phase_started) * 1000)
        timings = {"download_ms": elapsed, "download_attempts": attempts, "probe_ms": probe_ms, "extract_ms": extract_ms, "render_ms": render_ms}
        phase_started = time.perf_counter()
        package = write_reference_package(
            arguments.output / video_id,
            video,
            video_id,
            config,
            arguments.parameter_source,
            sheets,
            duration_ms=metadata.duration_ms,
            width=metadata.width,
            height=metadata.height,
            timings={**timings, "write_ms": None},
            overwrite=arguments.overwrite,
        )
        timings["write_ms"] = round((time.perf_counter() - phase_started) * 1000)
        manifest_path = package / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["timings"] = {**timings, "analysis_ms": round((time.perf_counter() - started) * 1000)}
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    if arguments.timing:
        print(json.dumps(manifest["timings"], indent=2))
    print(package)
    return 0


def estimate_sheet_count(duration_ms: int, fps: int, slots_per_sheet: int) -> int:
    return math.ceil(duration_ms * fps / (1000 * slots_per_sheet))


def _require_tools(value: str, backend: str, download_only: bool = False) -> None:
    if not download_only:
        require_backend(backend)
    if is_url(value):
        require_executable("yt-dlp")


def _resolve_input(value: str, temporary_dir: Path) -> Path:
    if is_url(value):
        return download_video(value, temporary_dir / "download")
    return resolve_local_input(value)


def _download_input(arguments: argparse.Namespace, temporary_dir: Path | None = None) -> tuple[Path, int, int]:
    destination = arguments.download_dir / _video_id(arguments.input) if temporary_dir is None else temporary_dir / "download"
    if is_url(arguments.input):
        return download_video(arguments.input, destination, arguments.retry_preset, arguments.format_profile)
    return resolve_local_input(arguments.input), 0, 0


def _probe_video(video: Path, backend: str):
    return probe_video_opencv(video) if backend == "opencv" else probe_video(video)


def _extract_frames(video: Path, timestamps: list[int], frames_dir: Path, backend: str) -> list[Image.Image]:
    frames = []
    for index, timestamp_ms in enumerate(timestamps):
        frame_path = frames_dir / f"frame-{index:08d}.png"
        if backend == "opencv":
            extract_frame_opencv(video, timestamp_ms, frame_path)
        else:
            extract_frame(video, timestamp_ms, frame_path)
        with Image.open(frame_path) as image:
            frames.append(image.copy())
    return frames


def _video_id(value: str) -> str:
    if is_url(value):
        parsed = urlparse(value)
        value = Path(parsed.path).stem or parsed.netloc
        value = f"{value}-{hashlib.sha256(parsed.geturl().encode()).hexdigest()[:10]}"
    else:
        value = Path(value).stem
    identifier = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip(".-")
    return identifier or "video"


if __name__ == "__main__":
    raise SystemExit(main())
