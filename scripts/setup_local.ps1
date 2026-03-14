$ErrorActionPreference = "Stop"

$projectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $projectRoot

if (-not (Test-Path ".env") -and (Test-Path ".env.example")) {
    Copy-Item ".env.example" ".env"
}

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    python -m venv .venv
}

$pythonExe = Join-Path $projectRoot ".venv\Scripts\python.exe"

& $pythonExe -m pip install -r requirements.txt
& $pythonExe -m src.setup.bootstrap
& $pythonExe -m uvicorn src.api.app:app --host 127.0.0.1 --port 8000
