# 视频拼图参考 Skill 实现计划

> **对于代理工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。

**目标：** 构建一个下载或读取视频、按时间顺序渲染带标注联系表并输出可供多模态代理引用索引的 Python CLI 和 Skill。

**架构：** Python 包负责验证参数、调用本机媒体工具、渲染网格并写出索引。Skill 只在用户请求将视频转为图片参考材料时触发，询问缺少的采样参数后调用 CLI。

**技术栈：** Python 3.11+、Pillow、pytest、ffmpeg、ffprobe、可选 yt-dlp。

---

## 任务 1：创建包、配置与采样模型

**文件：** `pyproject.toml`、`src/video_contact_sheet/__init__.py`、`src/video_contact_sheet/models.py`、`tests/test_sampling.py`

1. 编写覆盖默认参数、非法参数和 `fps=2` 时间戳的失败测试。
2. 运行 `python -m pytest tests/test_sampling.py`，确认测试因包不存在而失败。
3. 定义不可变配置和帧记录模型；实现输入验证、按 `index / fps` 生成毫秒时间戳。
4. 再次运行该测试，确认通过。

## 任务 2：实现联系表渲染

**文件：** `src/video_contact_sheet/render.py`、`tests/test_render.py`

1. 编写 3×3 行优先布局、每帧标注、最后一页 `END` 槽的失败测试。
2. 运行 `python -m pytest tests/test_render.py`，确认失败。
3. 使用 Pillow 实现带顶部标题和格子边距的 PNG 联系表渲染；网格中 `slot = row * columns + column`。
4. 再次运行该测试，确认通过。

## 任务 3：实现输入和媒体工具封装

**文件：** `src/video_contact_sheet/input_source.py`、`src/video_contact_sheet/media.py`、`tests/test_media.py`

1. 编写本地输入、URL 下载器命令构造、缺少可执行程序和 ffprobe 元数据解析的失败测试。
2. 运行 `python -m pytest tests/test_media.py`，确认失败。
3. 实现命令检查、`yt-dlp` 下载、`ffprobe` 元数据读取和 `ffmpeg` 单帧提取；使用参数数组执行，不经 shell 拼接用户输入。
4. 再次运行该测试，确认通过。

## 任务 4：写出参考包和 CLI

**文件：** `src/video_contact_sheet/output.py`、`src/video_contact_sheet/cli.py`、`tests/test_output.py`、`README.md`

1. 编写索引 JSON、Markdown 参考说明、存在目录拒绝覆盖和 `--overwrite` 的失败测试。
2. 运行 `python -m pytest tests/test_output.py`，确认失败。
3. 实现输出目录、JSON 清单、Markdown、参数解析和完整编排；CLI 输出产物目录。
4. 再次运行 `python -m pytest`，确认全套测试通过。

## 任务 5：创建可发布 Skill

**文件：** `skills/video-contact-sheet/SKILL.md`

1. 写出压力场景：用户没有提供参数、用户提供高密度参数、宿主不支持提问工具。
2. 编写 Skill，要求提问、默认降级、估算输出数量、合规提示和正确 CLI 调用。
3. 人工检查 YAML 前置元数据、禁止范围和行优先要求是否完整。

## 任务 6：端到端验证与发布准备

**文件：** `.gitignore`、`LICENSE`、`tests/`

1. 用 ffmpeg 创建一个短的本地测试视频。
2. 运行 CLI，以 `1 fps`、`3×3` 生成联系表。
3. 检查生成图片、`frames.json`、`manifest.json` 和 `reference.md` 是否存在，且帧总数和最后一页空槽正确。
4. 运行 `python -m pytest` 并检查工作区变更。
5. 创建 GitHub 仓库说明所需的发布清单，不自动推送或创建远程仓库。
