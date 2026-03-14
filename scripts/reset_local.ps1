$ErrorActionPreference = "Stop"

$projectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $projectRoot

$pythonExe = Join-Path $projectRoot ".venv\Scripts\python.exe"

if (Test-Path $pythonExe) {
    & $pythonExe -m src.setup.reset_project
} else {
    Write-Host "No se encontro .venv. No se pudo eliminar la base del proyecto desde este script."
}

if (Test-Path ".venv") {
    Remove-Item ".venv" -Recurse -Force
}
