# FrameAtlas

[中文文档](README.md)

FrameAtlas converts a local video or an HTTP(S) URL supported by `yt-dlp` into timestamped PNG contact sheets for efficient AI visual analysis, scene lookup, and reusable video references.

## Features

- Uses OpenCV for frame extraction by default, with FFmpeg as an explicit fallback.
- Orders frames strictly left-to-right, then top-to-bottom; final unused cells show `END`.
- Preserves each source frame's aspect ratio with letterboxing or pillarboxing; it never stretches, squashes, or crops a frame to fill a cell.
- Downloads and archives only the video stream needed for visual analysis by default; use `--media-mode complete` for audio plus video.
- Creates `frames.json`, `manifest.json`, and `reference.md` beside the selected media file.
- Stores sheets in `contact-sheets/YYYYMMDD/NNNN/` for date- and batch-based organization.
- Lets an AI install or update OpenCV, Pillow, and URL-required `yt-dlp` in the active environment.

## Install

```powershell
python -m pip install -e .
```

An AI can read [AGENTS.md](AGENTS.md) and follow its host-specific setup instructions for Trae, OpenCode, or Claude Code. On Windows:

```powershell
.\tools\install-skill.ps1 -TargetHost all
```

`-TargetHost trae` installs the Skill into `.trae/skills/video-contact-sheet/` in the current cloned repository; `traeglobal` installs into Trae's Windows personal directory; `traecli` installs into the current repository's TraeCode CLI project directory; `claude` and `opencode` install to personal directories.

Use only the active Python environment. A trusted package mirror requires user approval and applies only to the current installation command.

### Ask An AI To Install It

Send this prompt directly to Trae, OpenCode, or Claude Code. Use a GitHub Raw URL, not a `github.io` URL:

```text
Read this file and install the FrameAtlas Skill exactly as instructed:
https://raw.githubusercontent.com/zzx124Z/FrameAtlas/main/AGENTS.md

Requirements:
1. Clone the repository and read AGENTS.md first.
2. Install the Skill only in the current host's directory specified by AGENTS.md.
3. Install project dependencies in the active Python environment.
4. Do not use any built-in browser or Computer Use.
5. After installation, verify video-contact-sheet --help and report the installed path.
```

Update the URL if the default branch or repository name changes later.

## Usage

```powershell
video-contact-sheet "C:\media\demo.mp4" --fps 1 --rows 5 --columns 5 --output "video-reference" --parameter-source explicit
video-contact-sheet "https://example.com/video" --fps 1 --rows 5 --columns 5 --output "video-reference" --parameter-source explicit
```

The defaults are `1 fps` and `5x5`. Sheet count is `ceil(duration_seconds × fps ÷ (rows × columns))`. A 10-minute video at defaults produces `ceil(600 × 1 ÷ 25) = 24` sheets. Use the lowest density that can answer the question and open only time-range-relevant sheets.

### Two-Stage Mode For Unreliable Networks

For sources with separate audio/video streams or unstable CDN connections, download first and analyze locally to avoid repeating network work. The default `visual-only` mode selects just the video stream, so it skips audio that contact-sheet analysis cannot use and avoids FFmpeg merging:

```powershell
video-contact-sheet "https://example.com/video" --stage download --download-dir video-downloads --retry-preset balanced --media-mode visual-only
video-contact-sheet "video-downloads/<video-id>/original.mp4" --stage analyze --output video-reference
```

`--media-mode complete` selects audio plus video and can require FFmpeg to merge the streams; use it only when sound or a complete archive is needed. `--retry-preset` supports `fast-fail`, `balanced` (default), and `reliable`; `--format-profile small` prefers a video format at or below 720p. The download stage prints attempt information, and the analysis `manifest.json` records stage timings. The default `--stage all` remains available.

### Long-Video Efficiency And Recovery

- OpenCV opens the video once and decodes every target frame in chronological order. Do not reopen the video or seek randomly for each timestamp: some H.264 files become dramatically slower that way.
- For a whole-video review, inspect all sheets chronologically, but load only a small batch per model request. If a temporary model-request failure occurs (such as `4054`), keep the generated local sheets and resume from the next batch instead of downloading or generating again.
- At `1 fps` and `5x5`, each sheet covers 25 seconds; a roughly 16-minute video produces about 39 sheets. Use a `3x3` or `2x2` grid for subtitles or corner text rather than guessing from unreadable cells.

## Bilibili HTTP 412

Compare `where.exe yt-dlp`, `yt-dlp --version`, `python -m pip show yt-dlp`, and `python -m yt_dlp --version`. A common cause is an outdated `yt-dlp.exe` on `PATH` while the newer package was installed into another Python environment; align versions and retry once. Never use BrowserUse, a built-in browser, Computer Use, cookies, forged headers, or proxy rotation to bypass platform controls.

## Content Rights

Process only material you are entitled to download, retain, and analyze. This project does not bypass logins, paywalls, DRM, or other access controls, and does not collect credentials, cookies, or access tokens.
