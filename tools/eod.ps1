param(
  [string]$Msg = ""
)

$ErrorActionPreference = "Stop"

function Fail($m) { Write-Host "EOD FAIL: $m" -ForegroundColor Red; exit 1 }
function Info($m) { Write-Host "EOD: $m" -ForegroundColor Cyan }

# Ensure we're in a git repo
git rev-parse --is-inside-work-tree *> $null
if ($LASTEXITCODE -ne 0) { Fail "Not inside a git repository." }

# Show status
Info "Status (pre):"
git status --porcelain

# If no message provided, generate one
if ([string]::IsNullOrWhiteSpace($Msg)) {
  $ts = Get-Date -Format "yyyy-MM-dd_HHmm"
  $Msg = "EOD sync $ts"
}

# Pull first (safer than push-first)
Info "Pull (rebase):"
git pull --rebase
if ($LASTEXITCODE -ne 0) { Fail "Pull failed. Resolve conflicts, then rerun." }

# Stage everything (you can change -A to specific paths if desired)
Info "Stage:"
git add -A

# If nothing staged, exit cleanly
$staged = git diff --cached --name-only
if ([string]::IsNullOrWhiteSpace($staged)) {
  Info "No staged changes. Nothing to commit."
  exit 0
}

# Commit
Info "Commit:"
git commit -m "$Msg"
if ($LASTEXITCODE -ne 0) { Fail "Commit failed." }

# Push
Info "Push:"
git push
if ($LASTEXITCODE -ne 0) { Fail "Push failed." }

Info "Done."
Info "Status (post):"
git status --porcelain