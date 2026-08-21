from dataclasses import dataclass
from typing import Sequence

from PIL import Image, ImageDraw, ImageFont

from .models import SamplingConfig

CELL_SIZE = 360
GUTTER = 4
HEADER_HEIGHT = 48


@dataclass(frozen=True)
class FramePlacement:
    index: int
    timestamp_ms: int
    row: int
    column: int


@dataclass
class RenderedSheet:
    image: Image.Image
    placements: list[FramePlacement]
    end_slots: list[tuple[int, int]]


def format_timestamp(timestamp_ms: int) -> str:
    if not isinstance(timestamp_ms, int) or isinstance(timestamp_ms, bool) or timestamp_ms < 0:
        raise ValueError("timestamp_ms must be a non-negative integer")
    hours, remainder = divmod(timestamp_ms, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    seconds, milliseconds = divmod(remainder, 1_000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"


def render_contact_sheets(
    frames: Sequence[Image.Image],
    timestamps_ms: Sequence[int],
    config: SamplingConfig,
    *,
    video_id: str,
) -> list[RenderedSheet]:
    if len(frames) != len(timestamps_ms):
        raise ValueError("frames and timestamps_ms must have the same length")
    if not isinstance(video_id, str) or not video_id:
        raise ValueError("video_id must be a non-empty string")
    if not frames:
        return []

    slots_per_sheet = config.slots_per_sheet
    return [
        _render_sheet(
            frames[start : start + slots_per_sheet],
            timestamps_ms[start : start + slots_per_sheet],
            config,
            video_id,
            sheet_index=start // slots_per_sheet + 1,
            frame_offset=start,
        )
        for start in range(0, len(frames), slots_per_sheet)
    ]


def _render_sheet(
    frames: Sequence[Image.Image],
    timestamps_ms: Sequence[int],
    config: SamplingConfig,
    video_id: str,
    *,
    sheet_index: int,
    frame_offset: int,
) -> RenderedSheet:
    width = config.columns * (CELL_SIZE + 2 * GUTTER)
    height = HEADER_HEIGHT + config.rows * (CELL_SIZE + 2 * GUTTER)
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    start_time = format_timestamp(timestamps_ms[0])
    end_time = format_timestamp(timestamps_ms[-1])
    draw.text(
        (GUTTER, GUTTER),
        f"{video_id} | Sheet {sheet_index} | {start_time} to {end_time} | {config.fps} fps | {config.rows}x{config.columns}",
        fill="black",
        font=font,
    )

    placements = []
    end_slots = []
    for slot in range(config.slots_per_sheet):
        row, column = divmod(slot, config.columns)
        x = column * (CELL_SIZE + 2 * GUTTER) + GUTTER
        y = HEADER_HEIGHT + row * (CELL_SIZE + 2 * GUTTER) + GUTTER
        draw.rectangle((x - 1, y - 1, x + CELL_SIZE, y + CELL_SIZE), outline="black")
        if slot < len(frames):
            frame = _fit_frame(frames[slot])
            image.paste(frame, (x, y))
            timestamp_ms = timestamps_ms[slot]
            placement = FramePlacement(frame_offset + slot, timestamp_ms, row, column)
            placements.append(placement)
            draw.text(
                (x + GUTTER, y + GUTTER),
                f"#{placement.index} {format_timestamp(timestamp_ms)}",
                fill="white",
                stroke_width=1,
                stroke_fill="black",
                font=font,
            )
        else:
            end_slots.append((row, column))
            _draw_centered_text(draw, (x, y, x + CELL_SIZE, y + CELL_SIZE), "END", font)

    return RenderedSheet(image=image, placements=placements, end_slots=end_slots)


def _fit_frame(frame: Image.Image) -> Image.Image:
    source = frame.convert("RGB")
    scale = min(CELL_SIZE / source.width, CELL_SIZE / source.height)
    size = (max(1, round(source.width * scale)), max(1, round(source.height * scale)))
    resized = source.resize(size)
    canvas = Image.new("RGB", (CELL_SIZE, CELL_SIZE), "white")
    canvas.paste(resized, ((CELL_SIZE - resized.width) // 2, (CELL_SIZE - resized.height) // 2))
    return canvas


def _draw_centered_text(
    draw: ImageDraw.ImageDraw,
    bounds: tuple[int, int, int, int],
    text: str,
    font: ImageFont.ImageFont,
) -> None:
    left, top, right, bottom = bounds
    text_bounds = draw.textbbox((0, 0), text, font=font)
    text_width = text_bounds[2] - text_bounds[0]
    text_height = text_bounds[3] - text_bounds[1]
    draw.text(
        (left + (right - left - text_width) // 2, top + (bottom - top - text_height) // 2),
        text,
        fill="black",
        font=font,
    )
