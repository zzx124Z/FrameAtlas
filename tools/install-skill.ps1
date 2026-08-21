param(
    [ValidateSet("trae", "traeglobal", "traecli", "claude", "opencode", "all")]
    [string]$TargetHost = "all"
)

$root = Split-Path -Parent $PSScriptRoot
$source = Join-Path $root "skills\video-contact-sheet"

if (-not (Test-Path (Join-Path $source "SKILL.md"))) {
    throw "Skill source was not found: $source"
}

python -m pip install --upgrade -e $root
if ($LASTEXITCODE -ne 0) {
    throw "Python dependency installation failed."
}

$targets = @()
if ($TargetHost -in "trae", "all") {
    $targets += Join-Path $root ".trae\skills\video-contact-sheet"
}
if ($TargetHost -in "traeglobal", "all") {
    $targets += Join-Path $HOME ".trae-cn\skills\video-contact-sheet"
}
if ($TargetHost -in "traecli", "all") {
    $targets += Join-Path $root ".traecli\skills\video-contact-sheet"
}
if ($TargetHost -in "claude", "all") {
    $targets += Join-Path $HOME ".claude\skills\video-contact-sheet"
}
if ($TargetHost -in "opencode", "all") {
    $targets += Join-Path $HOME ".config\opencode\skills\video-contact-sheet"
}

foreach ($target in $targets) {
    New-Item -ItemType Directory -Force -Path $target | Out-Null
    Copy-Item -Recurse -Force (Join-Path $source "*") $target
    Write-Output "Installed FrameAtlas skill: $target"
}
