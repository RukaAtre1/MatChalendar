$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $ProjectRoot

if (-not (Test-Path "backend\main.py")) {
    throw "backend\main.py was not found. Run this script from the MatChalendar project, or check that scripts\start_backend.ps1 is inside the project root."
}

if (Test-Path ".env.local") {
    Write-Host "Found .env.local; backend/config.py will load it."
}

Write-Host "Starting MatChalendar backend from $ProjectRoot"
Write-Host "Health:         http://127.0.0.1:8000/api/health"
Write-Host "Runtime status: http://127.0.0.1:8000/api/runtime/status"
Write-Host "Agentverse:     http://127.0.0.1:8000/api/agentverse/plan"
Write-Host ""

python backend\main.py
