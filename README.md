# FrameAtlas

[English documentation](README.en.md)

FrameAtlas 将本地视频或 `yt-dlp` 支持的 HTTP(S) URL 转换为带帧号和毫秒时间戳的 PNG 联系表，供 AI 进行视觉分析、定位场景和复用视频内容。

## 功能

- 默认使用 OpenCV 抽帧，FFmpeg 作为显式备用后端。
- 联系表严格按从左到右、从上到下排列；最后空格显示 `END`，不复制末帧。
- 始终保持原视频画面比例，以留白适配单元格，绝不拉伸、压扁或裁切画面。
- 默认仅下载和保存视觉分析所需的视频轨；使用 `--media-mode complete` 才下载音视频轨并保留完整媒体。
- 保存已选媒体文件、`frames.json`、`manifest.json` 和 `reference.md`。
- 图片保存在 `contact-sheets/YYYYMMDD/NNNN/`；日期和四位批次号便于归档。
- 支持让 AI 自动安装或更新 OpenCV、Pillow 和 URL 所需的 `yt-dlp`。

## 安装

```powershell
python -m pip install -e .
```

AI 可阅读 [AGENTS.md](AGENTS.md) 并执行对应部署步骤，将本 Skill 安装到 Trae、OpenCode 或 Claude Code。Windows 用户也可运行：

```powershell
.\tools\install-skill.ps1 -TargetHost all
```

其中 `-TargetHost trae` 将 Skill 安装至当前克隆仓库的 `.trae/skills/video-contact-sheet/`；`traeglobal` 安装至 Trae 的 Windows 个人目录；`traecli` 安装至当前仓库的 TraeCode CLI 项目目录；`claude` 与 `opencode` 安装到个人目录。

仅使用当前 Python 环境；如需镜像，请让用户确认可信镜像后仅用于该次安装，不修改全局 pip 配置。

### 交给 AI 安装

将下列提示词直接发送给 Trae、OpenCode 或 Claude Code。应使用 GitHub Raw 文件地址，而不是 `github.io` 地址：

```text
请读取并严格按照此文件安装 FrameAtlas Skill：
https://raw.githubusercontent.com/zzx124Z/FrameAtlas/main/AGENTS.md

要求：
1. 先克隆仓库并阅读 AGENTS.md。
2. 仅按 AGENTS.md 的当前宿主对应目录安装 Skill。
3. 使用当前 Python 环境安装项目依赖。
4. 不要使用任何内置浏览器或 Computer Use。
5. 安装完成后验证 video-contact-sheet --help，并报告实际安装目录。
```

若后续更改默认分支或仓库名，请同步修改链接。

## 使用

```powershell
video-contact-sheet "C:\media\demo.mp4" --fps 1 --rows 5 --columns 5 --output "video-reference" --parameter-source explicit
video-contact-sheet "https://example.com/video" --fps 1 --rows 5 --columns 5 --output "video-reference" --parameter-source explicit
```

默认参数是 `1 fps`、`5x5`。图片数量：`ceil(视频秒数 × 每秒帧数 ÷ (行数 × 列数))`。例如 10 分钟视频：`ceil(600 × 1 ÷ 25) = 24` 张联系表。优先使用能回答问题的最低抽帧密度，并只打开目标时间范围的联系表。

### 不稳定网络的两阶段模式

对 Bilibili 等分轨下载或 CDN 不稳定的来源，建议先下载、后分析，避免重复下载。默认 `visual-only` 只选视频轨，不下载对联系表无用的音频，也不需要 FFmpeg 合并：

```powershell
video-contact-sheet "https://example.com/video" --stage download --download-dir video-downloads --retry-preset balanced --media-mode visual-only
video-contact-sheet "video-downloads/<video-id>/original.mp4" --stage analyze --output video-reference
```

`--media-mode complete` 才会选择视频轨加音频轨，可能需要 FFmpeg 合并，适用于需要声音或完整归档的场景。`--retry-preset` 支持 `fast-fail`、`balanced`（默认）和 `reliable`；`--format-profile small` 优先选择不高于 720p 的视频格式。下载阶段会显示尝试信息，分析产物的 `manifest.json` 会记录阶段耗时。默认的 `--stage all` 仍可一条命令完成。

### 长视频效率与故障处理

- OpenCV 会一次打开视频并按时间顺序解码所有目标帧；不要为每个时间戳重新打开视频或随机跳转，否则某些 H.264 文件会显著变慢。
- 完整视频分析应按时间顺序读取全部联系表，但每轮只加载少量图片；如果模型出现临时请求失败（例如 `4054`），保留已生成的本地联系表，从下一批继续读取，不必重新下载或生成。
- `1 fps`、`5x5` 每张图覆盖 25 秒，约 16 分钟视频会产生约 39 张联系表；字幕或角落文字看不清时，改用 `3x3` 或 `2x2`，不要凭模糊图像猜测。

## Bilibili HTTP 412

先比对 `where.exe yt-dlp`、`yt-dlp --version`、`python -m pip show yt-dlp` 和 `python -m yt_dlp --version`。常见根因是 PATH 中的旧 `yt-dlp.exe` 与另一 Python 环境中新安装的版本不一致；对齐后再重试一次。禁止使用 BrowserUse、内置浏览器、Computer Use、Cookie、伪造请求头或代理轮换绕过平台控制。

## 内容权利

只处理你有权下载、保存和分析的内容。本项目不绕过登录、付费墙、DRM 或其他访问控制，也不会收集凭据、Cookie 或访问令牌。
