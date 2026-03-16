<#
   Setup-GitHub-Project.ps1 - Windows PowerShell
   Purpose: Auto setup Git + GitHub and create PR
   Repository: claude-bridge-local
   User: luckys4900
#>

# Project configuration
$repoOwner = "luckys4900"
$repoName  = "claude-bridge-local"
$repoPath  = "$repoName"

# 1. Check Git installation
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "[INFO] Git not found. Installing via winget..."
    winget install -e --id Git.Git
    Write-Host "[INFO] Git installed. Please restart PowerShell and run again."
    exit
}
else {
    Write-Host "[OK] Git installed: $(git --version)"
}

# 2. Check GitHub CLI installation
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Host "[INFO] GitHub CLI not found. Installing via winget..."
    winget install -e --id GitHub.cli
    Write-Host "[INFO] GitHub CLI installed. Please restart PowerShell and run again."
    exit
}
else {
    Write-Host "[OK] GitHub CLI installed"
}

# 3. Check Git config
$gitName  = git config --global user.name
$gitEmail = git config --global user.email

if (-not $gitName -or -not $gitEmail) {
    Write-Host "[WARN] Git user.name or user.email not set."
    $gitName  = Read-Host "Enter Git username"
    $gitEmail = Read-Host "Enter Git email"
    git config --global user.name  "$gitName"
    git config --global user.email "$gitEmail"
    Write-Host "[OK] Git config set: $gitName <$gitEmail>"
}
else {
    Write-Host "[OK] Git config: $gitName <$gitEmail>"
}

# 4. Check GitHub CLI login
Write-Host "`n--- Check GitHub CLI Login ---"
$ghAuthStatus = gh auth status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARN] GitHub CLI not logged in."
    Write-Host "Please run: gh auth login"
    Write-Host "Then run this script again."
    exit
}
else {
    Write-Host "[OK] GitHub CLI authenticated"
}

# 5. Check if repository exists on GitHub
Write-Host "`n--- Check GitHub Repository ---"
$repoCheck = gh repo view $repoOwner/$repoName --json name -q ".name" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARN] Repository $repoOwner/$repoName not found."
    $createRepo = Read-Host "Create repository? (y/n)"
    if ($createRepo -eq "y") {
        gh repo create $repoOwner/$repoName --public --description "Claude Code proxy for OpenRouter / Ollama / GLM"
        Write-Host "[OK] Repository created"
    }
    else {
        Write-Host "[INFO] Repository creation cancelled."
        exit
    }
}
else {
    Write-Host "[OK] Repository exists: $repoOwner/$repoName"
}

# 6. Set up remote URL
$remoteUrl = "https://github.com/$repoOwner/$repoName.git"

if (Test-Path .git) {
    Write-Host "`n[INFO] Current directory is a Git repository"
    git remote -v
    $remoteExists = git remote get-url origin 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[INFO] Adding remote origin..."
        git remote add origin $remoteUrl
    }
    else {
        Write-Host "[INFO] Updating remote URL..."
        git remote set-url origin $remoteUrl
    }
}
else {
    Write-Host "[WARN] Current directory is not a Git repository"
    Write-Host "Location: $(Get-Location)"
    $initRepo = Read-Host "Initialize Git repository? (y/n)"
    if ($initRepo -eq "y") {
        git init
        git remote add origin $remoteUrl
        Write-Host "[OK] Git repository initialized"
    }
    else {
        exit
    }
}

git remote -v
Write-Host "[OK] Remote origin set: $remoteUrl"

# 7. Check for changes and commit
Write-Host "`n--- Check File Status ---"
git status

$hasChanges = git status --porcelain
if ($hasChanges) {
    Write-Host "[INFO] There are changed files"
    
    $branch = "setup/initial-$(Get-Date -Format 'yyyyMMddHHmmss')"
    
    Write-Host "[INFO] Creating branch: $branch"
    git checkout -b $branch

    Write-Host "[INFO] Staging files..."
    git add .

    $commitMessage = "chore: initial project setup with GitHub integration"
    Write-Host "[INFO] Committing: $commitMessage"
    git commit -m $commitMessage

    Write-Host "[INFO] Pushing branch..."
    git push -u origin $branch
    Write-Host "[OK] Branch $branch pushed to remote"
}
else {
    Write-Host "[INFO] No changed files"
    
    $currentBranch = git branch --show-current
    Write-Host "[INFO] Current branch: $currentBranch"
    
    $pushMain = Read-Host "Push current branch? (y/n)"
    if ($pushMain -eq "y") {
        git push -u origin $currentBranch
        Write-Host "[OK] Branch $currentBranch pushed"
    }
}

# 8. Create Pull Request (if not on main/master)
$currentBranch = git branch --show-current
if ($currentBranch -ne "main" -and $currentBranch -ne "master") {
    Write-Host "`n--- Create Pull Request ---"
    $createPR = Read-Host "Create Pull Request? (y/n)"
    if ($createPR -eq "y") {
        $mainBranch = "main"
        $prTitle = "chore: initial project setup"
        $prBody = "Initial project setup completed.`n`n- Git repository initialized`n- GitHub remote configured`n- Initial files added"
        
        gh pr create `
            --title $prTitle `
            --body $prBody `
            --base $mainBranch `
            --head $currentBranch
        Write-Host "[OK] Pull Request created"
    }
}

# 9. Completion message
Write-Host "`n=== Setup Complete ==="
Write-Host "Git version      : $(git --version)"
Write-Host "User             : $(git config --global user.name) <$(git config --global user.email)>"
Write-Host "Repository       : https://github.com/$repoOwner/$repoName"
Write-Host "Current branch   : $(git branch --show-current)"
Write-Host "`nNext steps:"
Write-Host "1. Review and merge PR on GitHub (if created)"
Write-Host "2. Switch to main: git checkout main"
Write-Host "3. Pull latest: git pull origin main"
