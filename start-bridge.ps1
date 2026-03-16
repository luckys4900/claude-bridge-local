$NPM_BIN = Join-Path $env:APPDATA "npm"
$CLAUDE_JS = Join-Path $NPM_BIN "node_modules\@anthropic-ai\claude-code\cli.js"
$OLLAMA_URL = "http://localhost:11434/v1"
$env:PATH = "$NPM_BIN;$env:PATH"
$env:ANTHROPIC_API_KEY = "sk-ant-bridge-dummy"

$LOCAL_MODELS = @{
    "1" = @{ name = "qwen3:30b";        label = "Qwen3 30B  - High quality (18GB)" }
    "2" = @{ name = "codellama:latest"; label = "CodeLlama  - Code focused (3.8GB)" }
    "3" = @{ name = "llama3.2:latest";  label = "Llama3.2   - Fast + light (2.0GB)" }
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Claude Bridge - Local GPU Mode" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

try {
    Invoke-WebRequest -Uri "http://localhost:11434/" -TimeoutSec 3 -ErrorAction Stop | Out-Null
    Write-Host "[OK] Ollama is running." -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Ollama is not running. Please start Ollama first." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Select model:" -ForegroundColor Yellow
foreach ($key in ($LOCAL_MODELS.Keys | Sort-Object)) {
    Write-Host "  $key) $($LOCAL_MODELS[$key].label)"
}
Write-Host ""

$choice = Read-Host "Enter number (1-3)"

if (-not $LOCAL_MODELS.ContainsKey($choice)) {
    Write-Host "[ERROR] Invalid choice." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

$model = $LOCAL_MODELS[$choice].name
$label = $LOCAL_MODELS[$choice].label

Write-Host ""
Write-Host "Starting: $label" -ForegroundColor Green
Write-Host "Model:    $model" -ForegroundColor Cyan
Write-Host "URL:      $OLLAMA_URL" -ForegroundColor Cyan
Write-Host ""
Write-Host "Claude will start now. Type /exit to quit." -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

$bridgePath = Join-Path $NPM_BIN "claude-bridge.cmd"
& $bridgePath openai $model --baseURL $OLLAMA_URL --claude-binary $CLAUDE_JS --apiKey dummy

Write-Host ""
Write-Host "Session ended. Press Enter to close." -ForegroundColor Gray
Read-Host
