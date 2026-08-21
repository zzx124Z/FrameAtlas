# FrameAtlas

[中文文档](README.md)

FrameAtlas converts a local video or an HTTP(S) URL supported by `yt-dlp` into timestamped PNG contact sheets for efficient AI visual analysis, scene lookup, and reusable video references.

## Features

- Uses OpenCV for frame extraction by default, with FFmpeg as an explicit fallback.
- Orders frames strictly left-to-right, then top-to-bottom; final unused cells show `END`.
- Preserves each source frame's aspect ratio with letterboxing or pillarboxing; it never stretches, squashes, or crops a frame to fill a cell.
- Archives the source video and creates `frames.json`, `manifest.json`, and `reference.md`.
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

Use only the active Python environment. A trusted package mirror requires user approval and applies only to the current installation command.

### Ask An AI To Install It

After publishing to GitHub, replace `<GitHub-username>` and the branch name below, then send this prompt to Trae, OpenCode, or Claude Code. Use a GitHub Raw URL, not a `github.io` URL:

```text
Read this file and install the FrameAtlas Skill exactly as instructed:
https://raw.githubusercontent.com/<GitHub-username>/FrameAtlas/main/AGENTS.md

Requirements:
1. Clone the repository and read AGENTS.md first.
2. Install the Skill only in the current host's directory specified by AGENTS.md.
3. Install project dependencies in the active Python environment.
4. Do not use BrowserUse, TRAE-browseruse, any built-in browser, or Computer Use.
5. After installation, verify video-contact-sheet --help and report the installed path.
```

Replace `main` with `master` when applicable, and replace `FrameAtlas` if you publish under a different repository name.

## Usage

```powershell
video-contact-sheet "C:\media\demo.mp4" --fps 1 --rows 3 --columns 3 --output "video-reference" --parameter-source explicit
video-contact-sheet "https://example.com/video" --fps 1 --rows 3 --columns 3 --output "video-reference" --parameter-source explicit
```

The defaults are `1 fps` and `3x3`. Sheet count is `ceil(duration_seconds × fps ÷ (rows × columns))`. A 10-minute video at defaults produces `ceil(600 × 1 ÷ 9) = 67` sheets. Use the lowest density that can answer the question and open only time-range-relevant sheets.

## Bilibili HTTP 412

Compare `where.exe yt-dlp`, `yt-dlp --version`, `python -m pip show yt-dlp`, and `python -m yt_dlp --version`. A common cause is an outdated `yt-dlp.exe` on `PATH` while the newer package was installed into another Python environment; align versions and retry once. Never use BrowserUse, a built-in browser, Computer Use, cookies, forged headers, or proxy rotation to bypass platform controls.

## Content Rights

Process only material you are entitled to download, retain, and analyze. This project does not bypass logins, paywalls, DRM, or other access controls, and does not collect credentials, cookies, or access tokens.
