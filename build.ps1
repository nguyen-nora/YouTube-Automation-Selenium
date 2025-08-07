# Build PowerShell script for YouTube Automation Application
# ==========================================================

param(
    [switch]$Verbose,
    [switch]$NoUpx,
    [switch]$CleanOnly,
    [string]$SpecFile = "youtube_automation.spec"
)

Write-Host "YouTube Automation Build Script" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.x and add it to your PATH" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Build command arguments
$arguments = @()

if ($Verbose) {
    $arguments += "--verbose"
}

if ($NoUpx) {
    $arguments += "--no-upx"
}

if ($CleanOnly) {
    $arguments += "--clean-only"
}

if ($SpecFile -ne "youtube_automation.spec") {
    $arguments += "--spec-file"
    $arguments += $SpecFile
}

# Run the build script
Write-Host "Starting build process..." -ForegroundColor Yellow
Write-Host ""

$process = Start-Process -FilePath "python" -ArgumentList (@("build.py") + $arguments) -NoNewWindow -PassThru -Wait

if ($process.ExitCode -eq 0) {
    Write-Host ""
    Write-Host "BUILD SUCCESSFUL!" -ForegroundColor Green
    Write-Host "Check the dist folder for the packaged application." -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "BUILD FAILED!" -ForegroundColor Red
    Write-Host "Check the error messages above." -ForegroundColor Red
}

Write-Host ""
Read-Host "Press Enter to continue"
