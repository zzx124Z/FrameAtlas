import json
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path


class MediaToolError(RuntimeError):
    pass


@dataclass(frozen=True)
class VideoMetadata:
    duration_ms: int
    width: int
    height: int


@dataclass(frozen=True)
class RetrySettings:
    retries: int
    fragment_retries: int
    socket_timeout: int


RETRY_PRESETS = {
    "fast-fail": RetrySettings(1, 1, 10),
    "balanced": RetrySettings(3, 5, 20),
    "reliable": RetrySettings(5, 20, 30),
}


def build_download_command(url: str, destination: Path, settings: RetrySettings | None = None, format_profile: str = "balanced") -> list[str]:
    settings = settings or RETRY_PRESETS["balanced"]
    command = [
        "yt-dlp", "--no-playlist", "--output", str(destination / "original.%(ext)s"),
        "--retries", str(settings.retries), "--fragment-retries", str(settings.fragment_retries),
        "--socket-timeout", str(settings.socket_timeout),
    ]
    if format_profile == "small":
        command.extend(["--format", "bv*[height<=720]+ba/b[height<=720]/b"])
    elif format_profile != "balanced":
        raise ValueError(f"unsupported format profile: {format_profile}")
    command.append(url)
    return command


def require_executable(name: str) -> None:
    if shutil.which(name) is None:
        raise MediaToolError(f"required executable is not available on PATH: {name}")


def require_backend(backend: str) -> None:
    if backend == "opencv":
        try:
            import cv2
        except ImportError as error:
            raise MediaToolError("OpenCV is required for the opencv backend; install the project dependencies") from error
        return
    if backend == "ffmpeg":
        require_executable("ffprobe")
        require_executable("ffmpeg")
        return
    raise MediaToolError(f"unsupported media backend: {backend}")


def download_video(url: str, destination: Path, retry_preset: str = "balanced", format_profile: str = "balanced") -> tuple[Path, int, int]:
    require_executable("yt-dlp")
    if retry_preset not in RETRY_PRESETS:
        raise ValueError(f"unsupported retry preset: {retry_preset}")
    destination.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    settings = RETRY_PRESETS[retry_preset]
    errors = []
    for attempt in range(1, 4):
        for partial in destination.glob("original.*"):
            partial.unlink()
        print(f"download: attempt {attempt}/3, profile={format_profile}, retries={settings.retries}, fragment-retries={settings.fragment_retries}", flush=True)
        completed = subprocess.run(build_download_command(url, destination, settings, format_profile), capture_output=True, text=True)
        files = sorted(destination.glob("original.*"))
        if completed.returncode == 0 and len(files) == 1:
            elapsed_ms = round((time.perf_counter() - started) * 1000)
            (destination / "download-manifest.json").write_text(
                json.dumps({"input": url, "video": files[0].name, "attempts": attempt, "elapsed_ms": elapsed_ms, "retry_preset": retry_preset, "format_profile": format_profile}, indent=2),
                encoding="utf-8",
            )
            return files[0], attempt, elapsed_ms
        errors.append(completed.stderr.strip() or "yt-dlp did not produce exactly one original video")
    raise MediaToolError(f"yt-dlp failed after 3 attempts: {errors[-1]}")


def parse_probe_metadata(raw_metadata: str) -> VideoMetadata:
    try:
        payload = json.loads(raw_metadata)
        video_stream = next(stream for stream in payload["streams"] if stream.get("codec_type") == "video")
        duration_ms = round(float(payload["format"]["duration"]) * 1000)
        width = int(video_stream["width"])
        height = int(video_stream["height"])
    except (KeyError, StopIteration, TypeError, ValueError, json.JSONDecodeError) as error:
        raise MediaToolError("ffprobe output does not contain valid video metadata") from error
    if duration_ms <= 0 or width <= 0 or height <= 0:
        raise MediaToolError("ffprobe output contains non-positive video metadata")
    return VideoMetadata(duration_ms=duration_ms, width=width, height=height)


def probe_video(video: Path) -> VideoMetadata:
    require_executable("ffprobe")
    command = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration:stream=codec_type,width,height",
        "-of",
        "json",
        str(video),
    ]
    completed = subprocess.run(command, capture_output=True, text=True)
    if completed.returncode != 0:
        raise MediaToolError(completed.stderr.strip() or "ffprobe failed")
    return parse_probe_metadata(completed.stdout)


def probe_video_opencv(video: Path) -> VideoMetadata:
    require_backend("opencv")
    import cv2

    capture = cv2.VideoCapture(str(video))
    try:
        if not capture.isOpened():
            raise MediaToolError(f"OpenCV cannot open video: {video}")
        fps = capture.get(cv2.CAP_PROP_FPS)
        frame_count = capture.get(cv2.CAP_PROP_FRAME_COUNT)
        width = round(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = round(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    finally:
        capture.release()
    if fps <= 0 or frame_count <= 0 or width <= 0 or height <= 0:
        raise MediaToolError("OpenCV could not read valid video metadata")
    return VideoMetadata(duration_ms=round(frame_count * 1000 / fps), width=width, height=height)


def extract_frame(video: Path, timestamp_ms: int, destination: Path) -> None:
    require_executable("ffmpeg")
    if timestamp_ms < 0:
        raise ValueError("timestamp_ms must not be negative")
    destination.parent.mkdir(parents=True, exist_ok=True)
    timestamp_seconds = f"{timestamp_ms / 1000:.3f}"
    command = ["ffmpeg", "-y", "-ss", timestamp_seconds, "-i", str(video), "-frames:v", "1", str(destination)]
    completed = subprocess.run(command, capture_output=True, text=True)
    if completed.returncode != 0 or not destination.is_file():
        raise MediaToolError(completed.stderr.strip() or f"ffmpeg failed at {timestamp_seconds}s")


def extract_frame_opencv(video: Path, timestamp_ms: int, destination: Path) -> None:
    require_backend("opencv")
    if timestamp_ms < 0:
        raise ValueError("timestamp_ms must not be negative")
    import cv2

    destination.parent.mkdir(parents=True, exist_ok=True)
    capture = cv2.VideoCapture(str(video))
    try:
        if not capture.isOpened():
            raise MediaToolError(f"OpenCV cannot open video: {video}")
        capture.set(cv2.CAP_PROP_POS_MSEC, timestamp_ms)
        success, frame = capture.read()
    finally:
        capture.release()
    if not success or frame is None or not cv2.imwrite(str(destination), frame):
        raise MediaToolError(f"OpenCV failed at {timestamp_ms}ms")
