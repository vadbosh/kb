<#
Install the kb toolkit — Windows.  Linux / macOS: use install.sh

The CLI is installed INSIDE the skill (skills\kb\scripts\kb) together with a
kb.cmd launcher, so nothing depends on PATH. Windows has no ~/.local/bin and
does not act on a shebang line — hence the launcher.

  .\install.ps1                 install the skill into every assistant found + docs
  .\install.ps1 -DryRun         print what would happen, change nothing
  .\install.ps1 -WithPath       also place a launcher on PATH for manual use
  .\install.ps1 -SkillsDir D    install into D instead of auto-detecting

Idempotent: re-running replaces only what changed and backs up what it
overwrites as <file>.bak.<timestamp>. Nothing outside the user profile is
touched. If execution policy blocks this file:

  powershell -ExecutionPolicy Bypass -File .\install.ps1
#>
[CmdletBinding()]
param(
    [switch]$DryRun,
    [switch]$WithPath,
    [string]$SkillsDir
)

$ErrorActionPreference = 'Stop'

$Src     = Split-Path -Parent $MyInvocation.MyCommand.Path
$DocDir  = if ($env:KB_DOC_DIR) { $env:KB_DOC_DIR } else { Join-Path $HOME '.kb-docs' }
$PathDir = if ($env:KB_BIN_DIR) { $env:KB_BIN_DIR } else { Join-Path $env:LOCALAPPDATA 'kb\bin' }
$Stamp   = Get-Date -Format 'yyyyMMdd-HHmmss'

function Say  ([string]$T) { Write-Host $T }
function Ok   ([string]$T) { Write-Host $T -ForegroundColor Green }
function Warn ([string]$T) { Write-Host $T -ForegroundColor Yellow }
function Bad  ([string]$T) { Write-Host $T -ForegroundColor Red }

function Short([string]$Path) {
    if ($Path.StartsWith($HOME)) { return '~' + $Path.Substring($HOME.Length) }
    return $Path
}

# Copy with a timestamped backup. Returns early when the content already
# matches, so a re-run is a genuine no-op instead of a pile of identical .bak.
function Install-KbFile([string]$From, [string]$To) {
    if ((Test-Path -LiteralPath $To) -and
        ((Get-FileHash -LiteralPath $From).Hash -eq (Get-FileHash -LiteralPath $To).Hash)) {
        Say "    = $(Short $To)"
        return
    }
    if ($DryRun) { Say "    would write $(Short $To)"; return }

    $parent = Split-Path -Parent $To
    if (-not (Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }
    if (Test-Path -LiteralPath $To) {
        Copy-Item -LiteralPath $To -Destination "$To.bak.$Stamp"
        Say "    ~ $(Short $To)  (backup .bak.$Stamp)"
    } else {
        Say "    + $(Short $To)"
    }
    Copy-Item -LiteralPath $From -Destination $To -Force
}

# ── Python ──────────────────────────────────────────────────────────────────
# Deliberately shallow: try the usual three names, keep the first that actually
# runs code and reports 3.10+. A Microsoft Store stub of python.exe fails that
# probe on its own, so it needs no special handling. Anything else — missing
# install, or installed but never added to PATH — ends up here as "not found",
# which is the same fix either way.
$probeCode = 'import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)'
$launch = $null
foreach ($cand in @(
    @{ Exe = 'py';      Pre = @('-3') },
    @{ Exe = 'python3'; Pre = @()     },
    @{ Exe = 'python';  Pre = @()     }
)) {
    if (-not (Get-Command $cand.Exe -ErrorAction SilentlyContinue)) { continue }
    & $cand.Exe @($cand.Pre + @('-c', $probeCode)) 2>$null
    if ($LASTEXITCODE -eq 0) {
        $launch = (@($cand.Exe) + $cand.Pre) -join ' '
        break
    }
}

if (-not $launch) {
    Write-Host ''
    Bad  '  Python 3.10+ not found.'
    Write-Host ''
    Warn '  Either it is not installed, or it is installed but not on PATH'
    Warn '  (a common outcome when "Add python.exe to PATH" was left unticked).'
    Write-Host ''
    Say  '    winget install Python.Python.3.12'
    Say  '    or https://www.python.org/downloads/windows/'
    Write-Host ''
    Warn '  Then reopen the terminal and run this installer again.'
    Write-Host ''
    exit 1
}
Ok "python: $launch"

# ── skill ───────────────────────────────────────────────────────────────────
Say '-- skill --'

$dirs = if ($SkillsDir) { @($SkillsDir) } else {
    @(
        (Join-Path $HOME '.claude\skills'),
        (Join-Path $env:APPDATA 'opencode\skills'),
        (Join-Path $HOME '.config\opencode\skills'),
        (Join-Path $HOME '.codex\skills')
    ) | Where-Object { Test-Path -LiteralPath (Split-Path -Parent $_) }
}

if (-not $dirs -or $dirs.Count -eq 0) {
    Bad  '  No assistant directory found.'
    Warn '  Looked for ~\.claude, %APPDATA%\opencode, ~\.config\opencode, ~\.codex'
    Warn '  Pass -SkillsDir <path> to install anyway.'
    exit 1
}

# %~dp0 is the directory of the .cmd itself, so the launcher and the script stay
# movable as a pair.
$cmdShim = @"
@echo off
$launch "%~dp0kb" %*
"@

foreach ($dir in $dirs) {
    Say "  $(Short $dir)"
    Install-KbFile (Join-Path $Src 'skills\kb\SKILL.md') (Join-Path $dir 'kb\SKILL.md')

    foreach ($ref in Get-ChildItem -LiteralPath (Join-Path $Src 'skills\kb\references') -Filter '*.md') {
        Install-KbFile $ref.FullName (Join-Path $dir "kb\references\$($ref.Name)")
    }

    Install-KbFile (Join-Path $Src 'skills\kb\scripts\kb') (Join-Path $dir 'kb\scripts\kb')

    $shim = Join-Path $dir 'kb\scripts\kb.cmd'
    if ($DryRun) {
        Say "    would write $(Short $shim)"
    } else {
        Set-Content -LiteralPath $shim -Value $cmdShim -Encoding ASCII
        Say "    + $(Short $shim)"
    }
}

# ── docs ────────────────────────────────────────────────────────────────────
Say '-- docs --'
Install-KbFile (Join-Path $Src 'docs\kb.en.md') (Join-Path $DocDir 'kb.en.md')
Install-KbFile (Join-Path $Src 'docs\kb.ru.md') (Join-Path $DocDir 'kb.ru.md')

# ── optional: a launcher on PATH, for running kb by hand ────────────────────
if ($WithPath) {
    Say '-- PATH copy --'
    Install-KbFile (Join-Path $Src 'skills\kb\scripts\kb') (Join-Path $PathDir 'kb')
    if (-not $DryRun) {
        Set-Content -LiteralPath (Join-Path $PathDir 'kb.cmd') -Value $cmdShim -Encoding ASCII
        Say "    + $(Short (Join-Path $PathDir 'kb.cmd'))"
        if ([Environment]::GetEnvironmentVariable('Path', 'User') -notlike "*$PathDir*") {
            Warn "    $(Short $PathDir) is not on PATH — add it for this user:"
            Say  "      [Environment]::SetEnvironmentVariable('Path',"
            Say  "        [Environment]::GetEnvironmentVariable('Path','User') + ';$PathDir', 'User')"
            Warn '      then reopen the terminal.'
        }
    }
}

# ── verify ──────────────────────────────────────────────────────────────────
Say '-- verify --'
if ($DryRun) { Warn '  dry run - nothing was installed'; exit 0 }

$probe = Join-Path $dirs[0] 'kb\scripts\kb.cmd'
& $probe --help > $null 2>&1
if ($LASTEXITCODE -eq 0) {
    Ok "  ok - $(Short $probe)"
    Write-Host ''
    Say "  In your assistant: say 'kbrestore' to load a project's notes,"
    Say "  'kbsave' to write down what you learned."
    Say "  By hand: & '$probe' list"
} else {
    Bad "  Installed, but $(Short $probe) did not run (exit $LASTEXITCODE)."
    Warn '  Check that Python is still on PATH in this terminal.'
    exit 1
}
