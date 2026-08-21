# FrameAtlas Agent Setup

Read this file when installing FrameAtlas from a cloned repository. Install dependencies with `python -m pip install --upgrade -e .` in the current Python environment. Do not use BrowserUse, TRAE-browseruse, any built-in browser, or Computer Use while using this project.

Install the skill document by copying `.trae/skills/video-contact-sheet` to the host-specific skill directory:

- Trae project: `.trae/skills/video-contact-sheet`
- Claude Code project: `.claude/skills/video-contact-sheet`
- Claude Code personal: `~/.claude/skills/video-contact-sheet`
- OpenCode project: `.opencode/skills/video-contact-sheet`
- OpenCode personal: `~/.config/opencode/skills/video-contact-sheet`

For this repository itself, the Trae project location already exists. On Windows, run `./tools/install-skill.ps1 -TargetHost claude`, `-TargetHost opencode`, or `-TargetHost all` from the repository root to copy the skill document to personal locations. Restart the host after installation.
