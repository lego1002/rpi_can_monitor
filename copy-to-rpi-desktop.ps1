#!/usr/bin/env pwsh

# Copy files from rpi_can_monitor to RPI_Desktop with correct directory structure
# PowerShell version for Windows

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Copying CAN Logger files to RPI_Desktop" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Define paths
$ScriptDir = Get-Location
$RpiDesktopDir = Join-Path $env:USERPROFILE "Desktop\RPI_Desktop"

# Check if RPI_Desktop exists
if (-not (Test-Path $RpiDesktopDir)) {
    Write-Host "✗ Error: RPI_Desktop directory not found at $RpiDesktopDir" -ForegroundColor Red
    exit 1
}

Write-Host "Source directory: $ScriptDir" -ForegroundColor Yellow
Write-Host "Destination directory: $RpiDesktopDir" -ForegroundColor Yellow
Write-Host ""

# Create necessary directories
Write-Host "[1/5] Creating directory structure..." -ForegroundColor Green
New-Item -ItemType Directory -Path "$RpiDesktopDir\scripts" -Force | Out-Null
New-Item -ItemType Directory -Path "$RpiDesktopDir\services" -Force | Out-Null
New-Item -ItemType Directory -Path "$RpiDesktopDir\LOGS" -Force | Out-Null
Write-Host "✓ Directories created" -ForegroundColor Green
Write-Host ""

# Copy main Python scripts
Write-Host "[2/5] Copying Python scripts to scripts/" -ForegroundColor Green
$pythonFiles = @(
    "canlogging-v4_lego.py",
    "wheel-speed-api.py"
)

foreach ($file in $pythonFiles) {
    $source = Join-Path $ScriptDir $file
    $dest = Join-Path $RpiDesktopDir "scripts\$file"
    if (Test-Path $source) {
        Copy-Item -Path $source -Destination $dest -Force
        Write-Host "✓ $file" -ForegroundColor Green
    }
}
Write-Host ""

# Copy setup script
Write-Host "[3/5] Copying setup script to scripts/" -ForegroundColor Green
$source = Join-Path $ScriptDir "setup-service.sh"
$dest = Join-Path $RpiDesktopDir "scripts\setup-service.sh"
if (Test-Path $source) {
    Copy-Item -Path $source -Destination $dest -Force
    Write-Host "✓ setup-service.sh" -ForegroundColor Green
}
Write-Host ""

# Copy service files
Write-Host "[4/5] Copying systemd service files to services/" -ForegroundColor Green
$serviceFiles = @(
    "canlogging-lego.service",
    "wheel-speed-api.service"
)

foreach ($file in $serviceFiles) {
    $source = Join-Path $ScriptDir $file
    $dest = Join-Path $RpiDesktopDir "services\$file"
    if (Test-Path $source) {
        Copy-Item -Path $source -Destination $dest -Force
        Write-Host "✓ $file" -ForegroundColor Green
    }
}
Write-Host ""

# Copy documentation
Write-Host "[5/5] Copying documentation" -ForegroundColor Green
$source = Join-Path $ScriptDir "SERVICE_SETUP.md"
$dest = Join-Path $RpiDesktopDir "SERVICE_SETUP.md"
if (Test-Path $source) {
    Copy-Item -Path $source -Destination $dest -Force
    Write-Host "✓ SERVICE_SETUP.md" -ForegroundColor Green
}
Write-Host ""

# Display summary
Write-Host "================================================" -ForegroundColor Green
Write-Host "✓ Copy completed successfully!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "File structure:" -ForegroundColor Cyan
Write-Host "$RpiDesktopDir/" -ForegroundColor Cyan
Write-Host "├── scripts/" -ForegroundColor Cyan
Write-Host "│   ├── canlogging-v4_lego.py" -ForegroundColor Cyan
Write-Host "│   ├── wheel-speed-api.py" -ForegroundColor Cyan
Write-Host "│   └── setup-service.sh" -ForegroundColor Cyan
Write-Host "├── services/" -ForegroundColor Cyan
Write-Host "│   ├── canlogging-lego.service" -ForegroundColor Cyan
Write-Host "│   └── wheel-speed-api.service" -ForegroundColor Cyan
Write-Host "├── SERVICE_SETUP.md" -ForegroundColor Cyan
Write-Host "└── LOGS/" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. On RPi, navigate to: cd ~/Desktop/RPI_Desktop" -ForegroundColor Yellow
Write-Host "2. Run: sudo bash scripts/setup-service.sh setup-all" -ForegroundColor Yellow
Write-Host "3. Check status: sudo systemctl status canlogging-lego.service" -ForegroundColor Yellow
Write-Host ""
