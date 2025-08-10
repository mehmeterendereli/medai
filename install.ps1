[CmdletBinding()]
param(
  [string]$Model = "openai/gpt-oss-20b",
  [string]$BaseUrl = "http://localhost:8000/v1",
  [switch]$UseYarn = $false,
  [switch]$SkipPlaywright = $false,
  [switch]$InstallTorch = $true,
  [string]$TorchIndexUrl = "https://download.pytorch.org/whl/cu121"
)

function Write-Info($msg) { Write-Host "[+] $msg" -ForegroundColor Cyan }
function Write-Warn($msg) { Write-Host "[!] $msg" -ForegroundColor Yellow }
function Write-Err($msg)  { Write-Host "[-] $msg" -ForegroundColor Red }
function Test-Command($name) { $null -ne (Get-Command $name -ErrorAction SilentlyContinue) }

$ErrorActionPreference = 'Stop'

Push-Location $PSScriptRoot
try {
  Write-Info "Ön gereksinimler kontrol ediliyor (winget, git, python, node, tesseract)..."
  $hasWinget = Test-Command winget
  if (-not (Test-Command git)) {
    if ($hasWinget) { Write-Info "Git yok, yüklenecek"; winget install -e --id Git.Git -h } else { Write-Warn "Git bulunamadı. Lütfen kurun." }
  }
  if (-not (Test-Command python)) {
    if ($hasWinget) { Write-Info "Python 3.11 yok, yüklenecek"; winget install -e --id Python.Python.3.11 -h } else { Write-Warn "Python 3.11 bulunamadı. Lütfen kurun." }
  }
  if (-not (Test-Command node)) {
    if ($hasWinget) { Write-Info "Node.js 20 yok, yüklenecek"; winget install -e --id OpenJS.NodeJS.LTS -h } else { Write-Warn "Node.js bulunamadı. Lütfen kurun." }
  }
  if (-not (Test-Command tesseract)) {
    if ($hasWinget) { Write-Info "Tesseract OCR yok, yüklenecek"; winget install -e --id UB-Mannheim.TesseractOCR -h } else { Write-Warn "Tesseract bulunamadı. GUI installer ile kurun." }
  }

  Write-Info "Python sanal ortam oluşturuluyor (.venv)"
  if (-not (Test-Path .venv)) { python -m venv .venv }
  $py = Join-Path $PWD ".venv/Scripts/python.exe"
  & $py -m pip install --upgrade pip wheel setuptools

  if ($InstallTorch) {
    Write-Info "CUDA için torch kuruluyor ($TorchIndexUrl)"
    & $py -m pip install torch --index-url $TorchIndexUrl
  } else {
    Write-Warn "Torch kurulumu atlandı (-InstallTorch:$false)."}

  Write-Info "Python bağımlılıkları yükleniyor (requirements.txt)"
  & $py -m pip install -r requirements.txt

  if (-not $SkipPlaywright) {
    Write-Info "Playwright Chromium kuruluyor"
    & $py -m playwright install chromium
  }

  Write-Info "Konfigürasyon hazırlanıyor"
  if (-not (Test-Path ./configs/config.toml)) {
    Copy-Item ./configs/config.example.toml ./configs/config.toml -Force
  }
  # Python paket modülleri için __init__.py ekle
  foreach($d in @('.','core','tools')){
    $p = Join-Path $PWD "jarvis/$d/__init__.py"
    if (-not (Test-Path $p)) { New-Item -ItemType File -Path $p | Out-Null }
  }

  Write-Info "Electron HUD bağımlılıkları kuruluyor"
  Push-Location ./overlay-ui
  if ($UseYarn) {
    & corepack enable | Out-Null
    & corepack prepare yarn@stable --activate | Out-Null
    try { yarn install } catch { Write-Warn "Yarn ile kurulum başarısız, npm ile denenecek"; npm install }
  } else {
    npm install
  }
  Pop-Location

  Write-Info "data/ ve logs/ klasörleri oluşturuluyor"
  New-Item -ItemType Directory -Force -Path ./data/chroma | Out-Null
  New-Item -ItemType Directory -Force -Path ./data/cache | Out-Null
  New-Item -ItemType Directory -Force -Path ./logs | Out-Null

  Write-Info "Model ayarı configs/config.toml içine yazılıyor"
  (Get-Content ./configs/config.toml) -replace 'model\s*=\s*".*"', "model = \"$Model\"" | Set-Content ./configs/config.toml
  (Get-Content ./configs/config.toml) -replace 'base_url\s*=\s*".*"', "base_url = \"$BaseUrl\"" | Set-Content ./configs/config.toml

  Write-Info "Kurulum tamamlandı. Çalıştırmak için:"
  Write-Host "  ./startup/start_agent.ps1 -Model '$Model'" -ForegroundColor Green
}
catch {
  Write-Err $_
  exit 1
}
finally { Pop-Location }
