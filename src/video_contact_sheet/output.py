import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from .models import SamplingConfig
from .render import RenderedSheet, format_timestamp


class OutputExistsError(FileExistsError):
    pass


def write_reference_package(
    package: Path,
    source: Path,
    video_id: str,
    config: SamplingConfig,
    parameter_source: str,
    sheets: list[RenderedSheet],
    *,
    duration_ms: int,
    width: int,
    height: int,
    overwrite: bool = False,
) -> Path:
    if package.exists():
        if not overwrite:
            raise OutputExistsError(f"output directory already exists: {package}")
        shutil.rmtree(package)
    source_dir = package / "source"
    sheets_dir = package / "contact-sheets" / datetime.now(timezone.utc).strftime("%Y%m%d") / "0001"
    source_dir.mkdir(parents=True)
    sheets_dir.mkdir(parents=True)
    copied_source = source_dir / f"original{source.suffix.lower()}"
    shutil.copy2(source, copied_source)

    sheet_entries = []
    for number, sheet in enumerate(sheets, start=1):
        placements = sheet.placements
        start_ms = placements[0].timestamp_ms
        end_ms = placements[-1].timestamp_ms
        file_name = f"sheet-{number:04d}_{_file_timestamp(start_ms)}_to_{_file_timestamp(end_ms)}.png"
        sheet_path = sheets_dir / file_name
        sheet.image.save(sheet_path, "PNG")
        sheet_entries.append(
            {
                "file": sheet_path.relative_to(package).as_posix(),
                "frames": [
                    {"index": item.index, "timestamp_ms": item.timestamp_ms, "row": item.row, "column": item.column}
                    for item in placements
                ],
            }
        )
    (package / "frames.json").write_text(
        json.dumps({"sampling_fps": config.fps, "grid": {"rows": config.rows, "columns": config.columns}, "sheets": sheet_entries}, indent=2),
        encoding="utf-8",
    )
    manifest = {
        "video_id": video_id,
        "source": str(source),
        "original_video": str(copied_source.relative_to(package)),
        "parameter_source": parameter_source,
        "sampling": {"fps": config.fps, "rows": config.rows, "columns": config.columns},
        "video": {"duration_ms": duration_ms, "width": width, "height": height},
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "artifacts": [entry["file"] for entry in sheet_entries],
    }
    (package / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (package / "reference.md").write_text(
        "# Video Reference\n\n"
        "Read `manifest.json` for source and sampling settings. Read `frames.json` to map frame numbers and timestamps to contact sheets. "
        "Inspect files in `contact-sheets/` only for time ranges relevant to the question; each sheet is row-major, left to right then top to bottom.\n",
        encoding="utf-8",
    )
    return package


def _file_timestamp(timestamp_ms: int) -> str:
    return format_timestamp(timestamp_ms).replace(":", "-")
