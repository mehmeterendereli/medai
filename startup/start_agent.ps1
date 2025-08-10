[CmdletBinding()]
param(
  [string]$Model = "openai/gpt-oss-20b"
)

$ErrorActionPreference = 'Stop'

function Write-Info($msg) { Write-Host "[+] $msg" -ForegroundColor Cyan }

Push-Location $PSScriptRoot\..
try {
  $py = Join-Path $PWD ".venv/Scripts/python.exe"
  if (Get-Command yarn -ErrorAction SilentlyContinue) { $nodeCmd = 'yarn' } else { $nodeCmd = 'npm' }
  $hasPython = Test-Path $py
  # Taşınabilir Node/npm (./.tools/node/node-*-win-x64) var mı kontrol et
  $portableNpm = $null
  try {
    $portableNodeDir = Get-ChildItem -Path (Join-Path $PWD ".tools/node") -Directory -Filter "node-*-win-x64" -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($portableNodeDir) { $portableNpm = Join-Path $portableNodeDir.FullName "npm.cmd" }
  } catch {}

  $cfg = (Get-Content .\configs\config.toml -Raw)
  $llmEnabled = $false
  if($cfg -match 'enabled\s*=\s*(true|false)') { $llmEnabled = [bool]::Parse($Matches[1]) }
  if ($llmEnabled) {
    Write-Info "vLLM API başlatılıyor ($Model)"
  } else {
    Write-Info "LLM devre dışı: vLLM başlatılmayacak"
  }
  $dtype = if($cfg -match 'dtype\s*=\s*"([^"]+)"'){ $Matches[1] } else { 'float16' }
  $gpuUtil = if($cfg -match 'gpu_memory_utilization\s*=\s*([0-9.]+)'){ $Matches[1] } else { '0.90' }
  $batched = if($cfg -match 'max_num_batched_tokens\s*=\s*(\d+)'){ $Matches[1] } else { '8192' }
  $tp = if($cfg -match 'tensor_parallel_size\s*=\s*(\d+)'){ $Matches[1] } else { $null }
  $maxLen = if($cfg -match 'max_model_len\s*=\s*(\d+)'){ $Matches[1] } else { $null }
  $extra = ""
  if ($tp) { $extra += " --tensor-parallel-size $tp" }
  if ($maxLen) { $extra += " --max-model-len $maxLen" }
  if ($llmEnabled) {
    $vllmArgs = "-m vllm.entrypoints.openai.api_server --model $Model --dtype $dtype --gpu-memory-utilization $gpuUtil --max-num-batched-tokens $batched$extra"
    Start-Process -FilePath $py -ArgumentList $vllmArgs -WindowStyle Hidden
    Start-Sleep -Seconds 5
  }

  Write-Info "Overlay HUD başlatılıyor"
  Push-Location .\overlay-ui
  if ($nodeCmd -eq 'yarn') {
    Start-Process -FilePath yarn -ArgumentList "start" -WindowStyle Hidden
  } else {
    if ($portableNpm -and (Test-Path $portableNpm)) {
      Write-Info "npm install (portable) çalıştırılıyor"
      Start-Process -FilePath $portableNpm -ArgumentList "install" -WindowStyle Hidden -Wait
      Write-Info "HUD başlatılıyor (npm run start)"
      Start-Process -FilePath $portableNpm -ArgumentList "run start" -WindowStyle Hidden
    } else {
      Write-Info "npm (sistem) ile HUD başlatılıyor"
      Start-Process -FilePath npm -ArgumentList "run start" -WindowStyle Hidden
    }
  }
  Pop-Location
  Start-Sleep -Seconds 2

  if ($hasPython) {
    Write-Info "Python Agent (boot) başlatılıyor"
    Start-Process -FilePath $py -ArgumentList "-m jarvis.core.boot" -WindowStyle Hidden
  } else {
    Write-Info "Python bulunamadı (.venv). Ajan başlatılmadı (LLM kapalı HUD sadece)."
  }

  Write-Info "Tüm servisler başlatıldı. Kill-switch: Ctrl+Alt+Shift+J"
}
finally { Pop-Location }
