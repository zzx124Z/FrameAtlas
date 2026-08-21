import json
import re
from pathlib import Path

import pytest
from PIL import Image

from video_contact_sheet.models import SamplingConfig
from video_contact_sheet.output import OutputExistsError, write_reference_package
from video_contact_sheet.render import render_contact_sheets


def test_writes_machine_and_agent_readable_reference_package(tmp_path: Path):
    source = tmp_path / "input.mp4"
    source.write_bytes(b"video")
    config = SamplingConfig(fps=1, rows=3, columns=3)
    sheets = render_contact_sheets(
        [Image.new("RGB", (360, 360), (0, 0, 0))], [0], config, video_id="demo"
    )

    package = write_reference_package(
        tmp_path / "output",
        source,
        "demo",
        config,
        "default",
        sheets,
        duration_ms=1_000,
        width=360,
        height=360,
    )

    frames = json.loads((package / "frames.json").read_text(encoding="utf-8"))
    manifest = json.loads((package / "manifest.json").read_text(encoding="utf-8"))
    assert (package / "source" / "original.mp4").exists()
    image_folder = package / "contact-sheets"
    assert image_folder.exists()
    image_paths = list(image_folder.glob("*/*/sheet-*.png"))
    assert len(image_paths) == 1
    assert re.fullmatch(r"\d{8}", image_paths[0].parent.parent.name)
    assert image_paths[0].parent.name == "0001"
    assert frames["sheets"][0]["frames"][0] == {"index": 0, "timestamp_ms": 0, "row": 0, "column": 0}
    assert frames["sheets"][0]["file"] == str(image_paths[0].relative_to(package)).replace("\\", "/")
    assert manifest["parameter_source"] == "default"
    assert "contact-sheets" in (package / "reference.md").read_text(encoding="utf-8")


def test_refuses_existing_output_unless_overwrite_is_requested(tmp_path: Path):
    package = tmp_path / "output"
    package.mkdir()

    with pytest.raises(OutputExistsError):
        write_reference_package(
            package,
            tmp_path / "input.mp4",
            "demo",
            SamplingConfig(),
            "explicit",
            [],
            duration_ms=0,
            width=0,
            height=0,
        )
