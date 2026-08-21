from PIL import Image

from video_contact_sheet.models import SamplingConfig
from video_contact_sheet.render import format_timestamp, render_contact_sheets


def make_frame(color):
    return Image.new("RGB", (360, 360), color)


def test_formats_timestamps_with_millisecond_precision():
    assert format_timestamp(3_723_004) == "01:02:03.004"


def test_places_frames_in_strict_row_major_order():
    config = SamplingConfig(rows=3, columns=3)
    frames = [make_frame((index, 0, 0)) for index in range(9)]

    sheets = render_contact_sheets(
        frames,
        [index * 1_000 for index in range(9)],
        config,
        video_id="demo",
    )

    assert len(sheets) == 1
    assert [(placement.index, placement.row, placement.column) for placement in sheets[0].placements] == [
        (index, index // 3, index % 3) for index in range(9)
    ]
    for placement in sheets[0].placements:
        x = placement.column * 368 + 4 + 180
        y = 48 + placement.row * 368 + 4 + 180
        assert sheets[0].image.getpixel((x, y)) == (placement.index, 0, 0)


def test_marks_only_final_page_empty_slots_as_end_without_repeating_last_frame():
    config = SamplingConfig(rows=3, columns=3)
    frames = [make_frame((index, 0, 0)) for index in range(10)]

    sheets = render_contact_sheets(
        frames,
        [index * 1_000 for index in range(10)],
        config,
        video_id="demo",
    )

    final_sheet = sheets[1]
    assert [(placement.index, placement.row, placement.column) for placement in final_sheet.placements] == [
        (9, 0, 0)
    ]
    assert final_sheet.end_slots == [(row, column) for row in range(3) for column in range(3)][1:]
    assert final_sheet.image.getpixel((552, 232)) == (255, 255, 255)
    assert final_sheet.image.getpixel((184, 232)) == (9, 0, 0)


def test_preserves_wide_frame_aspect_ratio_with_letterboxing():
    config = SamplingConfig(rows=1, columns=1)
    frame = Image.new("RGB", (720, 360), (0, 0, 255))

    sheet = render_contact_sheets([frame], [0], config, video_id="wide")[0].image

    assert sheet.getpixel((184, 232)) == (0, 0, 255)
    assert sheet.getpixel((184, 80)) == (255, 255, 255)
    assert sheet.getpixel((184, 385)) == (255, 255, 255)
