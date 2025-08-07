@echo off
REM Build batch file for YouTube Automation Application
REM ===================================================

echo YouTube Automation Build Script
echo ==============================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.x and add it to your PATH
    pause
    exit /b 1
)

REM Check if we should use verbose mode
set VERBOSE_FLAG=
if "%1"=="verbose" set VERBOSE_FLAG=--verbose
if "%1"=="--verbose" set VERBOSE_FLAG=--verbose

REM Check if we should skip UPX
set UPX_FLAG=
if "%2"=="--no-upx" set UPX_FLAG=--no-upx
if "%1"=="--no-upx" set UPX_FLAG=--no-upx

REM Check if this is clean-only
if "%1"=="clean" (
    echo Running clean only...
    python build.py --clean-only
    pause
    exit /b
)

REM Run the build script
echo Starting build process...
echo.

python build.py %VERBOSE_FLAG% %UPX_FLAG%

if errorlevel 1 (
    echo.
    echo BUILD FAILED!
    echo Check the error messages above.
) else (
    echo.
    echo BUILD SUCCESSFUL!
    echo Check the dist folder for the packaged application.
)

echo.
pause
