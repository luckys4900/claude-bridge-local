<#
   Auto-Save-Git.ps1 - Git Auto-Save Script for Windows
   Purpose: Automatically commit and push changes to GitHub
   Features:
   - Monitor file changes in the repository
   - Auto-commit with timestamp
   - Auto-push to remote
   - Configurable interval
#>

param(
    [int]$IntervalMinutes = 5,
    [switch]$NoPush,
    [switch]$Silent
)

# Configuration
$RepoPath = $PSScriptRoot
$LogFile = Join-Path $RepoPath "autosave.log"
$CommitPrefixValue = "autosave"

function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] $Message"
    Add-Content -Path $LogFile -Value $logEntry
    if (-not $Silent) {
        Write-Host $logEntry
    }
}

function Write-ErrorLog {
    param([string]$Message)
    Write-Log "[ERROR] $Message"
    Write-Host $Message -ForegroundColor Red
}

function Check-GitRepo {
    if (-not (Test-Path (Join-Path $RepoPath ".git"))) {
        Write-ErrorLog "Not a Git repository: $RepoPath"
        return $false
    }
    return $true
}

function Has-Changes {
    $changes = git -C $RepoPath status --porcelain
    return $null -ne $changes -and $changes.Trim() -ne ""
}

function Auto-Commit {
    Write-Log "Checking for changes..."
    
    if (-not (Has-Changes)) {
        Write-Log "No changes detected"
        return $false
    }

    try {
        # Get list of changed files
        $changedFiles = git -C $RepoPath status --short
        Write-Log "Changes detected:"
        foreach ($file in $changedFiles) {
            Write-Log "  $file"
        }

        # Stage all changes
        Write-Log "Staging changes..."
        git -C $RepoPath add -A

        # Commit with timestamp
        $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
        $commitMessage = $CommitPrefixValue + " - " + $timestamp
        
        Write-Log "Committing with message: $commitMessage"
        $commitResult = git -C $RepoPath commit -m $commitMessage
        
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Commit successful"
            
            # Push to remote if enabled
            if (-not $NoPush) {
                Write-Log "Pushing to remote..."
                $pushResult = git -C $RepoPath push origin main
                if ($LASTEXITCODE -eq 0) {
                    Write-Log "Push successful"
                    return $true
                } else {
                    Write-ErrorLog "Push failed: $pushResult"
                    return $false
                }
            }
            return $true
        } else {
            Write-ErrorLog "Commit failed or nothing to commit"
            return $false
        }
    }
    catch {
        Write-ErrorLog "Error during auto-commit: $_"
        return $false
    }
}

# Main execution
Write-Log "========================================"
Write-Log "Git Auto-Save Started"
Write-Log "Repository: $RepoPath"
Write-Log "Interval: $IntervalMinutes minutes"
Write-Log "Push enabled: $(-not $NoPush)"
Write-Log "========================================"

# Check if we're in a Git repository
if (-not (Check-GitRepo)) {
    exit 1
}

# Initial check
Auto-Commit

# Monitor loop
$interval = New-TimeSpan -Minutes $IntervalMinutes
Write-Log "Starting auto-save loop (Press Ctrl+C to stop)..."

while ($true) {
    Start-Sleep -Seconds $interval.TotalSeconds
    
    Write-Log "--- Auto-save check at $(Get-Date -Format 'HH:mm:ss') ---"
    Auto-Commit
}
