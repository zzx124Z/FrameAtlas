# 视频拼图参考 Skill 设计

## 目标

将公开视频链接或本地视频转换为完整原视频归档和按时间顺序拼接的联系表（contact sheet），使多模态代理能够通过图片理解视频内容，并能精确引用画面时间点。

## 范围

首版支持本地视频和公开链接。链接下载使用用户本机已安装的 `yt-dlp`，不实现绕过登录、付费墙、DRM 或平台访问控制的逻辑。输入视频始终保留完整原文件。

首版生成联系表、`frames.json`、`manifest.json` 和 `reference.md`。不包含语音转写、OCR、上传、云端服务或模型调用。

## 用户交互

当用户没有同时指定采样频率和网格尺寸时，Skill 必须在生成前请求用户选择：

- 每秒抽取帧数（fps）
- 联系表网格的行数与列数

推荐默认值为 `1 fps` 和 `3×3`。若宿主环境不支持提问工具，使用该默认值，并在 `manifest.json` 中记录 `parameter_source` 为 `default`。用户已明确提供参数时直接执行，不重复询问。

若预估联系表数量过大，Skill 在执行前提示：`ceil(视频时长 × fps / (rows × columns))`。默认警告阈值为 100 张联系表。

## 处理管线

1. 验证输入是存在的本地文件或可下载的公开 URL。
2. 对 URL 调用 `yt-dlp` 下载原视频；本地输入复制或在清单中引用原文件。
3. 用 `ffprobe` 获取视频时长和尺寸。
4. 依据 `fps` 生成严格递增的采样时间戳；时间点定义为 `index / fps`，从零开始，不使用逐步累加。
5. 用 `ffmpeg` 逐个提取对应时间点的帧，保持原始顺序。
6. 在每个小图绘制连续帧编号和 `hh:mm:ss.mmm` 时间戳。
7. 按行优先顺序拼接：从左至右填充第一行，再填充下一行。
8. 最后一个联系表的空槽保留为空白并标记 `END`；不得复制末帧补满。
9. 写入索引文件和可供代理阅读的使用说明。

## 输出布局

```text
video-reference/<video-id>/
├─ source/original.<ext>
├─ contact-sheets/sheet-0001_00-00-00.000_to_00-00-08.000.png
├─ frames.json
├─ manifest.json
└─ reference.md
```

每张联系表顶部显示视频标识、联系表序号、起止时间、fps 和网格尺寸。格子之间使用边距和边框，图片为 PNG。小图短边默认不得低于 360 像素；画布尺寸会随网格扩大。

## 数据契约

`frames.json` 按联系表记录每一帧的 `index`、`timestamp_ms`、`row`、`column` 和图片文件名。`manifest.json` 记录输入、原视频路径、处理参数、参数来源、生成时间、视频元数据和产物列表。`reference.md` 指引代理先读清单，再按时间范围按需读取联系表，避免一次加载全部图片。

## 代码结构

```text
.trae/skills/video-contact-sheet/SKILL.md
src/video_contact_sheet/
├─ __init__.py
├─ cli.py
├─ models.py
├─ input_source.py
├─ media.py
├─ render.py
└─ output.py
tests/
├─ test_sampling.py
├─ test_render.py
└─ test_output.py
pyproject.toml
README.md
```

Python CLI 处理确定性媒体工作；Skill 只处理触发条件、权限边界、参数提问和 CLI 调用说明。依赖为 Python 3.11+、Pillow，外部可执行程序为 `ffmpeg`、`ffprobe`，URL 下载另需 `yt-dlp`。

## 失败处理

- 缺少 `ffmpeg` 或 `ffprobe`：在开始处理前报出明确安装要求。
- URL 下载失败：保留下载器错误摘要，不创建不完整索引。
- 帧提取失败：停止处理、返回出错时间点，并保留可安全复用的原视频。
- 非法 `fps`、行数或列数：拒绝零、负数和非整数值。
- 输出目录已存在：默认拒绝覆盖；用户显式传入覆盖参数时才清理并重建。

## 测试标准

- 采样时间戳严格递增且与 fps 对应。
- 9 帧在 3×3 网格中按行优先落在预期坐标。
- 10 帧生成两张联系表，第二张仅有第一格帧和其余 `END` 槽。
- JSON 索引中的时间戳、序号和网格坐标与渲染顺序一致。
- 无交互参数时清单记录默认参数来源。
- 非法参数和已存在目录返回可读错误。

## 合规与安全

仅处理用户有权下载、保存和分析的内容；项目不要求或保存账号密码、Cookie、访问令牌，也不提供绕过任何访问限制的能力。
