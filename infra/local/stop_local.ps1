if (-not (Get-Command docker -ErrorAction SilentlyContinue)) { Write-Error "docker not found"; exit 1 }
Push-Location $PSScriptRoot
docker compose down -v
Pop-Location
