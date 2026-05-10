# move_docker_data.ps1
# This script moves the Docker Desktop WSL2 data to the A: drive to free up space on C:

$TargetDir = "A:\DockerData"
$ExportPath = "A:\docker-desktop-data.tar"

Write-Host "!!! IMPORTANT !!!" -ForegroundColor Red
Write-Host "Please ensure Docker Desktop is COMPLETELY CLOSED before proceeding." -ForegroundColor Red
Write-Host "Press any key to continue once Docker is closed..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Create target directory if it doesn't exist
if (-not (Test-Path $TargetDir)) {
    Write-Host "Creating directory $TargetDir..."
    New-Item -ItemType Directory -Force -Path $TargetDir
}

Write-Host "Shutting down WSL..." -ForegroundColor Cyan
wsl --shutdown

Write-Host "Exporting Docker data to $ExportPath (This may take a few minutes)..." -ForegroundColor Cyan
wsl --export docker-desktop $ExportPath

if ($LASTEXITCODE -eq 0) {
    Write-Host "Unregistering current Docker data from C:..." -ForegroundColor Cyan
    wsl --unregister docker-desktop

    Write-Host "Importing Docker data to $TargetDir..." -ForegroundColor Cyan
    wsl --import docker-desktop $TargetDir $ExportPath --version 2

    Write-Host "Cleaning up temporary export file..." -ForegroundColor Cyan
    Remove-Item $ExportPath
    
    Write-Host "SUCCESS! Docker data has been moved to $TargetDir." -ForegroundColor Green
    Write-Host "You can now restart Docker Desktop." -ForegroundColor Green
} else {
    Write-Host "ERROR: Export failed. Please ensure you have enough space on A: and Docker is closed." -ForegroundColor Red
}
