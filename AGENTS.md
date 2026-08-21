# FrameAtlas Agent Setup

Read this file when installing FrameAtlas from a cloned repository. Install dependencies with `python -m pip install --upgrade -e .` in the current Python environment. Do not use any built-in browser or Computer Use while using this project.

Install the skill document by copying `skills/video-contact-sheet` to the host-specific skill directory:

- Trae project: `.trae/skills/video-contact-sheet`
- Trae personal on Windows: `%USERPROFILE%/.trae-cn/skills/video-contact-sheet`
- TraeCode CLI project: `.traecli/skills/video-contact-sheet`
- TraeCode CLI personal: `~/.traecli/skills/video-contact-sheet`
- Claude Code project: `.claude/skills/video-contact-sheet`
- Claude Code personal: `~/.claude/skills/video-contact-sheet`
- OpenCode project: `.opencode/skills/video-contact-sheet`
- OpenCode personal: `~/.config/opencode/skills/video-contact-sheet`

On Windows, run `./tools/install-skill.ps1 -TargetHost trae`, `-TargetHost traeglobal`, `-TargetHost traecli`, `-TargetHost claude`, `-TargetHost opencode`, or `-TargetHost all` from the repository root. The `trae` and `traecli` targets install into this cloned repository's project directories; `traeglobal`, `claude`, and `opencode` install to personal locations. Restart the host after installation.
