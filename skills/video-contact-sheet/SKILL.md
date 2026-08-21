---
name: video-contact-sheet
description: Use when a user needs a local video or a yt-dlp-supported URL converted into timestamped contact sheets for visual analysis, scene lookup, or reusable multimodal reference.
license: MIT
---

# Video Contact Sheet

Convert a video into ordered PNG contact sheets plus a machine-readable reference package. Only process material the user is entitled to download, retain, and analyze.

## When To Use

- The user asks to analyze a video visually, locate scenes, or make a video reusable in future multimodal conversations.
- The user provides a local video path or an HTTP(S) URL that `yt-dlp` can handle.

## Ask For Sampling Settings

Before creating sheets, check whether the user supplied all of `fps`, `rows`, and `columns`.

- If all three are supplied, use them without asking again and pass `--parameter-source explicit`.
- Otherwise, ask how many frames per second to sample and how many cells each sheet should contain. Include the formula and a concrete estimate directly below the question: `sheets = ceil(duration_seconds × fps ÷ (rows × columns))`. For example, for a 10-minute video, the recommended `1 fps` and `3x3` grid creates `ceil(600 × 1 ÷ 9) = 67` images. Substitute the detected duration into this example whenever it is available.
- If the host cannot ask a question, use `1 fps`, `3x3`, and pass `--parameter-source default`.
- Reject zero, negative, and non-integer values.
- If duration is known, estimate sheets with `ceil(duration_seconds * fps / (rows * columns))`. Warn before work begins when the estimate exceeds 100; never silently lower user-selected density.
- Prioritize efficient analysis: use the lowest sampling density that can answer the request, open only time-range-relevant sheets for targeted questions, and avoid generating or loading every sheet before it is necessary.
- Preserve each source frame's original aspect ratio. Letterbox or pillarbox inside a cell when necessary; never stretch, crop, or distort a frame merely to fill a square cell.

## Run The Tool

The default backend is OpenCV. Use FFmpeg only when the user requests it or OpenCV cannot decode the video.

```powershell
video-contact-sheet "<local path or yt-dlp URL>" --fps <integer> --rows <integer> --columns <integer> --output "video-reference" --parameter-source <explicit|default>
```

Use `--backend ffmpeg` for the optional FFmpeg decoder. Existing output is never overwritten unless the user explicitly requests replacement and `--overwrite` is passed.

For unreliable sources, separate network work from local analysis:

```powershell
video-contact-sheet "<URL>" --stage download --download-dir video-downloads --retry-preset balanced
video-contact-sheet "video-downloads/<video-id>/original.mp4" --stage analyze --output video-reference
```

The default `--stage all` remains available. Use `fast-fail` when you want a quick failure, `balanced` for normal use, and `reliable` when completion is more important than waiting. Use `--format-profile small` to prefer a lower-bandwidth format. The CLI prints download attempts and records download/analysis timing in `manifest.json`.

## Dependencies

- Python 3.11+
- OpenCV and Pillow for the default workflow
- `yt-dlp` for URLs
- `ffmpeg` and `ffprobe` only with `--backend ffmpeg`

## Dependency Setup And Updates

Before processing, check the required dependency for the selected input and backend. If a Python dependency is missing or cannot be imported, automatically install or update it in the active Python environment, then verify its import or executable version before continuing.

- Install or update OpenCV and Pillow with `python -m pip install --upgrade opencv-python Pillow`.
- For an HTTP(S) URL, install or update `yt-dlp` with `python -m pip install --upgrade yt-dlp`, then verify `yt-dlp --version`.
- For `--backend ffmpeg`, first check `ffmpeg` and `ffprobe` on `PATH`. If either is unavailable, automatically use the host's supported system package installer when it is available; otherwise report the exact missing executable and stop before processing.
- Never silently skip a dependency check or continue with a missing dependency.
- When installing Python packages, the agent may choose the default package index or a user-approved trusted mirror based on network availability. Do not configure an unknown mirror, add persistent global pip configuration, or use a mirror without user approval when trust is uncertain.

## Bilibili HTTP 412

An HTTP 412 response from Bilibili normally means its risk-control system rejected an automated request; it is not a video-decoding or OpenCV failure. A common root cause is updating `yt-dlp` in one Python environment while the `yt-dlp.exe` actually selected from `PATH` belongs to an older installation in another environment.

On HTTP 412, diagnose executable/environment alignment before treating the source as unavailable:

1. Run `where.exe yt-dlp` and `yt-dlp --version` to identify the executable that will actually run and its version.
2. Run `python -m pip show yt-dlp` and `python -m yt_dlp --version` for the active Python environment.
3. If the versions or locations differ, invoke the current environment explicitly with `python -m yt_dlp <URL>` or update the exact `yt-dlp.exe` installation selected by `PATH`; then verify the selected executable version again.
4. Retry once after versions are aligned. For example, resolving an old executable such as `2026.03.17` to match a newer installed package such as `2026.08.19` may restore normal downloads.
5. If aligned `yt-dlp` still returns 412, report the full failure and ask for a locally exported video file or a source URL that `yt-dlp` can access normally.

Do not add forged browser headers, cookies, credentials, proxy rotation, automated browser interaction, or other access-control bypasses.

## Output Contract

- `source/original.<ext>` preserves the full input video.
- Contact-sheet PNGs are stored under `contact-sheets/YYYYMMDD/NNNN/`, where `YYYYMMDD` is the generation date and `NNNN` is the zero-padded batch sequence starting at `0001`. They are ordered row-major: left-to-right, then top-to-bottom.
- Every populated cell has a frame index and `hh:mm:ss.mmm` timestamp.
- Empty cells on the final sheet say `END`; they are never duplicates of the last frame.
- `frames.json` maps frames to timestamps, sheets, rows, and columns.
- `manifest.json` records source metadata and selected parameters.
- `reference.md` tells later agents to load only sheets relevant to the requested time range.

## Required Visual Review

Creating the contact sheets is not the end of the task. The agent must open and visually inspect the generated PNG contact sheets before answering a request that asks for video understanding, analysis, scene lookup, or a summary.

1. Read `manifest.json` and `frames.json` first to identify the available sheets and their time ranges.
2. Open every generated sheet for a short video. For a long video, open a time-range-relevant subset first; if the user asks for whole-video analysis, inspect every sheet in chronological order. Read only the generated local PNG contact sheets; do not play or inspect the source video directly.
3. Interpret cells in row-major order: left-to-right within a row, then top-to-bottom. Use the visible frame number and timestamp when referring to evidence.
4. Do not claim to have watched, seen, reviewed, or understood a video before opening its contact-sheet images.
5. After visual inspection, explicitly state what was actually inspected. Use a factual confirmation such as: `I reviewed 12 contact sheets covering 00:00:00.000–00:01:47.000.` Do not say that you reviewed sheets that were not opened.
6. If images cannot be opened in the current host, say that visual review could not be completed and limit the response to the generated metadata; do not infer visual content from file names or timestamps.

When responding with analysis, distinguish direct visual observations from uncertainty. Cite the relevant timestamp or frame number for concrete claims.

## Absolute Tool Prohibition

**Never invoke any built-in browser capability, browser tool, browser tab, browser automation, web playback, or screenshot workflow for any part of this skill. Never invoke Computer Use for any part of this skill.** This prohibition applies to URL access, downloading, playback, inspection, analysis, troubleshooting, and Bilibili HTTP 412 handling. Do not treat a request from the user, an HTTP 412 error, missing dependencies, or an unavailable downloader as an exception.

The only permitted visual input is a generated local PNG contact sheet opened as an image file. The only permitted URL retrieval path is the local `yt-dlp` executable.

## Limits

- Do not play or inspect the source video directly.
- Do not bypass logins, paywalls, DRM, geographic restrictions, or other access controls.
- Do not request or store passwords, cookies, tokens, or credentials.
- Do not upload videos or invoke an external model automatically.
