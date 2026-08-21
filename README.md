# FrameAtlas

[English documentation](README.en.md)

FrameAtlas 将本地视频或 `yt-dlp` 支持的 HTTP(S) URL 转换为带帧号和毫秒时间戳的 PNG 联系表，供 AI 进行视觉分析、定位场景和复用视频内容。

## 功能

- 默认使用 OpenCV 抽帧，FFmpeg 作为显式备用后端。
- 联系表严格按从左到右、从上到下排列；最后空格显示 `END`，不复制末帧。
- 始终保持原视频画面比例，以留白适配单元格，绝不拉伸、压扁或裁切画面。
- 保存原始视频、`frames.json`、`manifest.json` 和 `reference.md`。
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

仅使用当前 Python 环境；如需镜像，请让用户确认可信镜像后仅用于该次安装，不修改全局 pip 配置。

### 交给 AI 安装

上传 GitHub 后，将下列提示词中的 `<GitHub用户名>` 和分支名替换为实际值，直接发送给 Trae、OpenCode 或 Claude Code。应使用 GitHub Raw 文件地址，而不是 `github.io` 地址：

```text
请读取并严格按照此文件安装 FrameAtlas Skill：
https://raw.githubusercontent.com/<GitHub用户名>/FrameAtlas/main/AGENTS.md

要求：
1. 先克隆仓库并阅读 AGENTS.md。
2. 仅按 AGENTS.md 的当前宿主对应目录安装 Skill。
3. 使用当前 Python 环境安装项目依赖。
4. 不要使用 BrowserUse、TRAE-browseruse、任何内置浏览器或 Computer Use。
5. 安装完成后验证 video-contact-sheet --help，并报告实际安装目录。
```

如果默认分支为 `master`，请将链接中的 `main` 替换为 `master`；若仓库名不同，也替换 `FrameAtlas`。

## 使用

```powershell
video-contact-sheet "C:\media\demo.mp4" --fps 1 --rows 3 --columns 3 --output "video-reference" --parameter-source explicit
video-contact-sheet "https://example.com/video" --fps 1 --rows 3 --columns 3 --output "video-reference" --parameter-source explicit
```

默认参数是 `1 fps`、`3x3`。图片数量：`ceil(视频秒数 × 每秒帧数 ÷ (行数 × 列数))`。例如 10 分钟视频：`ceil(600 × 1 ÷ 9) = 67` 张联系表。优先使用能回答问题的最低抽帧密度，并只打开目标时间范围的联系表。

## Bilibili HTTP 412

先比对 `where.exe yt-dlp`、`yt-dlp --version`、`python -m pip show yt-dlp` 和 `python -m yt_dlp --version`。常见根因是 PATH 中的旧 `yt-dlp.exe` 与另一 Python 环境中新安装的版本不一致；对齐后再重试一次。禁止使用 BrowserUse、内置浏览器、Computer Use、Cookie、伪造请求头或代理轮换绕过平台控制。

## 内容权利

只处理你有权下载、保存和分析的内容。本项目不绕过登录、付费墙、DRM 或其他访问控制，也不会收集凭据、Cookie 或访问令牌。
