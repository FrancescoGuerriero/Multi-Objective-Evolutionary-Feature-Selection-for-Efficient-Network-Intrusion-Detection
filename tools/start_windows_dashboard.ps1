# Integrated Windows dashboard (PowerShell). Builds React and serves it through FastAPI.
$ErrorActionPreference = "Stop"
Set-Location (Resolve-Path (Join-Path $PSScriptRoot ".."))
if (-not (Get-Command python -ErrorAction SilentlyContinue)) { throw "Python 3.12 must be installed" }
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) { throw "Node.js and npm must be installed" }
Push-Location frontend
try {
    if (Test-Path package-lock.json) { npm ci } else { npm install }
    if ($LASTEXITCODE -ne 0) { throw "npm dependency installation failed" }
    npm run build
    if ($LASTEXITCODE -ne 0) { throw "React production build failed" }
} finally { Pop-Location }
Write-Host "EvoNIDS dashboard and API available at http://127.0.0.1:8000/"
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
