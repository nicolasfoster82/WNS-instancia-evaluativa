$ErrorActionPreference = "Stop"

$projectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $projectRoot

if (-not (Test-Path ".env") -and (Test-Path ".env.example")) {
    Copy-Item ".env.example" ".env"
}

docker compose build python api
docker compose up -d postgres
docker compose run --rm python python -m src.setup.bootstrap
docker compose --profile api up api
