#!/usr/bin/env python3
"""
Build Script for YouTube Automation Application
==============================================

This script automates the packaging process:
1. Cleans previous build artifacts
2. Copies the chrome-win64 directory to the build location
3. Runs PyInstaller with the custom spec file
4. Verifies all required files are included in the output
5. Compresses the final executable using UPX (optional)

Usage:
    python build.py [options]
    
Options:
    --no-upx        Skip UPX compression
    --clean-only    Only clean build artifacts, don't build
    --verbose       Show detailed output
    --spec-file     Specify custom spec file (default: youtube_automation.spec)
"""

import os
import sys
import shutil
import subprocess
import json
import argparse
import time
from pathlib import Path
from typing import List, Dict, Tuple


class BuildAutomation:
    """Handles the automated build process for the YouTube automation application."""
    
    def __init__(self, verbose: bool = False, use_upx: bool = True, spec_file: str = "youtube_automation.spec"):
        self.verbose = verbose
        self.use_upx = use_upx
        self.spec_file = spec_file
        self.base_path = Path.cwd()
        self.build_path = self.base_path / "build"
        self.dist_path = self.base_path / "dist"
        self.chrome_source = self.base_path / "chrome-win64"
        self.chromedriver_source = self.base_path / "chromedriver.exe"
        
        # Required files that must be present in the final build
        self.required_files = [
            "youtube_automation.exe",
            "chromedriver.exe",
            "config.json",
            "accounts.json",
            "chrome-win64/chrome.exe",
            "chrome-win64/chrome_proxy.exe",
            "chrome-win64/libEGL.dll",
            "chrome-win64/libGLESv2.dll",
        ]
        
        # Required directories
        self.required_dirs = [
            "chrome-win64",
            "src",
        ]
    
    def log(self, message: str, level: str = "INFO"):
        """Log a message with timestamp."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
    
    def run_command(self, command: List[str], cwd: Path = None) -> Tuple[int, str, str]:
        """Run a command and return exit code, stdout, and stderr."""
        if self.verbose:
            self.log(f"Running command: {' '.join(command)}", "DEBUG")
        
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=cwd or self.base_path
            )
            stdout, stderr = process.communicate()
            
            if self.verbose and stdout:
                self.log(f"STDOUT: {stdout}", "DEBUG")
            if stderr and process.returncode != 0:
                self.log(f"STDERR: {stderr}", "ERROR")
            
            return process.returncode, stdout, stderr
        except Exception as e:
            self.log(f"Command failed: {e}", "ERROR")
            return 1, "", str(e)
    
    def clean_build_artifacts(self):
        """Clean previous build artifacts."""
        self.log("Cleaning previous build artifacts...")
        
        # Directories to clean
        dirs_to_clean = [self.build_path, self.dist_path]
        
        for dir_path in dirs_to_clean:
            if dir_path.exists():
                self.log(f"Removing directory: {dir_path}")
                try:
                    shutil.rmtree(dir_path)
                    self.log(f"Successfully removed: {dir_path}")
                except Exception as e:
                    self.log(f"Failed to remove {dir_path}: {e}", "WARNING")
        
        # Clean any .spec backup files
        for spec_backup in self.base_path.glob("*.spec.bak"):
            self.log(f"Removing backup file: {spec_backup}")
            spec_backup.unlink()
        
        self.log("Build artifacts cleaned successfully")
    
    def verify_prerequisites(self):
        """Verify all prerequisites are met before building."""
        self.log("Verifying prerequisites...")
        
        errors = []
        
        # Check if spec file exists
        if not (self.base_path / self.spec_file).exists():
            errors.append(f"Spec file not found: {self.spec_file}")
        
        # Check if Chrome directory exists
        if not self.chrome_source.exists():
            errors.append("Chrome directory not found: chrome-win64")
        else:
            # Check for critical Chrome files
            chrome_exe = self.chrome_source / "chrome.exe"
            if not chrome_exe.exists():
                errors.append("Chrome executable not found: chrome-win64/chrome.exe")
        
        # Check if ChromeDriver exists
        if not self.chromedriver_source.exists():
            errors.append("ChromeDriver not found: chromedriver.exe")
        
        # Check if PyInstaller is installed
        exit_code, stdout, stderr = self.run_command([sys.executable, "-m", "pip", "show", "pyinstaller"])
        if exit_code != 0:
            errors.append("PyInstaller not installed. Run: pip install pyinstaller")
        
        # Check if UPX is available (if requested)
        if self.use_upx:
            exit_code, stdout, stderr = self.run_command(["where", "upx"])
            if exit_code != 0:
                self.log("UPX not found in PATH. UPX compression will be skipped.", "WARNING")
                self.use_upx = False
        
        # Check for main.py
        if not (self.base_path / "main.py").exists():
            errors.append("Main entry point not found: main.py")
        
        # Check for config files
        if not (self.base_path / "config.json").exists():
            self.log("config.json not found. It will be created with defaults.", "WARNING")
        
        if not (self.base_path / "accounts.json").exists():
            self.log("accounts.json not found. It will be created with defaults.", "WARNING")
        
        if errors:
            self.log("Prerequisites check failed:", "ERROR")
            for error in errors:
                self.log(f"  - {error}", "ERROR")
            return False
        
        self.log("All prerequisites verified successfully")
        return True
    
    def run_pyinstaller(self):
        """Run PyInstaller with the spec file."""
        self.log(f"Running PyInstaller with spec file: {self.spec_file}")
        
        command = [sys.executable, "-m", "PyInstaller", "--clean", "--noconfirm"]
        
        if self.verbose:
            command.append("--log-level=DEBUG")
        
        command.append(self.spec_file)
        
        exit_code, stdout, stderr = self.run_command(command)
        
        if exit_code != 0:
            self.log("PyInstaller build failed", "ERROR")
            return False
        
        self.log("PyInstaller build completed successfully")
        return True
    
    def verify_build_output(self):
        """Verify all required files are present in the build output."""
        self.log("Verifying build output...")
        
        # Determine output directory based on spec file
        if "youtube_automation_dir" in self.spec_file:
            output_dir = self.dist_path / "youtube_automation"
        else:
            output_dir = self.dist_path
        
        if not output_dir.exists():
            self.log(f"Output directory not found: {output_dir}", "ERROR")
            return False
        
        missing_files = []
        missing_dirs = []
        
        # Check required files
        for req_file in self.required_files:
            file_path = output_dir / req_file
            if not file_path.exists():
                missing_files.append(req_file)
        
        # Check required directories
        for req_dir in self.required_dirs:
            dir_path = output_dir / req_dir
            if not dir_path.exists():
                missing_dirs.append(req_dir)
        
        # Report findings
        if missing_files or missing_dirs:
            self.log("Build verification failed:", "ERROR")
            for f in missing_files:
                self.log(f"  - Missing file: {f}", "ERROR")
            for d in missing_dirs:
                self.log(f"  - Missing directory: {d}", "ERROR")
            return False
        
        # Check file sizes
        exe_path = output_dir / "youtube_automation.exe"
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            self.log(f"Executable size: {size_mb:.2f} MB")
        
        # Count total files
        total_files = sum(1 for _ in output_dir.rglob("*") if _.is_file())
        self.log(f"Total files in distribution: {total_files}")
        
        self.log("Build verification passed - all required files present")
        return True
    
    def compress_with_upx(self):
        """Compress the executable with UPX."""
        if not self.use_upx:
            self.log("UPX compression skipped")
            return True
        
        self.log("Compressing executable with UPX...")
        
        # Find the executable
        if "youtube_automation_dir" in self.spec_file:
            exe_path = self.dist_path / "youtube_automation" / "youtube_automation.exe"
        else:
            exe_path = self.dist_path / "youtube_automation.exe"
        
        if not exe_path.exists():
            self.log(f"Executable not found: {exe_path}", "ERROR")
            return False
        
        # Get original size
        original_size = exe_path.stat().st_size / (1024 * 1024)
        
        # Run UPX
        command = ["upx", "--best", "--lzma", str(exe_path)]
        exit_code, stdout, stderr = self.run_command(command)
        
        if exit_code != 0:
            self.log("UPX compression failed", "WARNING")
            return False
        
        # Get compressed size
        compressed_size = exe_path.stat().st_size / (1024 * 1024)
        reduction = ((original_size - compressed_size) / original_size) * 100
        
        self.log(f"UPX compression successful:")
        self.log(f"  - Original size: {original_size:.2f} MB")
        self.log(f"  - Compressed size: {compressed_size:.2f} MB")
        self.log(f"  - Size reduction: {reduction:.1f}%")
        
        return True
    
    def create_default_configs(self):
        """Create default configuration files if they don't exist."""
        output_dir = self.dist_path / "youtube_automation" if "youtube_automation_dir" in self.spec_file else self.dist_path
        
        # Default config.json
        config_path = output_dir / "config.json"
        if not config_path.exists():
            self.log("Creating default config.json")
            default_config = {
                "browser": {
                    "chrome_binary_path": "./chrome-win64/chrome.exe",
                    "chromedriver_path": "./chromedriver.exe",
                    "headless": False,
                    "window_size": "1920,1080",
                    "user_agent": None,
                    "disable_gpu": True,
                    "no_sandbox": True,
                    "disable_dev_shm_usage": True
                },
                "automation": {
                    "loop_count": 10,
                    "min_watch_duration": 30,
                    "max_watch_duration": 120,
                    "between_loops_delay": [5, 15],
                    "human_simulation": True
                },
                "paths": {
                    "profile_directory": "./browser_profiles",
                    "downloads_directory": "./downloads",
                    "logs_directory": "./logs"
                }
            }
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=4)
        
        # Default accounts.json
        accounts_path = output_dir / "accounts.json"
        if not accounts_path.exists():
            self.log("Creating default accounts.json")
            default_accounts = {
                "accounts": [
                    {
                        "email": "example@gmail.com",
                        "password": "your_password_here",
                        "recovery_email": "recovery@example.com",
                        "phone": "+1234567890"
                    }
                ],
                "settings": {
                    "retry_failed_logins": True,
                    "max_login_attempts": 3,
                    "session_timeout": 3600
                }
            }
            with open(accounts_path, 'w') as f:
                json.dump(default_accounts, f, indent=4)
    
    def create_readme(self):
        """Create a README file for the distribution."""
        output_dir = self.dist_path / "youtube_automation" if "youtube_automation_dir" in self.spec_file else self.dist_path
        readme_path = output_dir / "README_DISTRIBUTION.txt"
        
        readme_content = """YouTube Automation Application
==============================

This is a packaged distribution of the YouTube Automation application.

IMPORTANT: This application includes a portable Chrome browser and ChromeDriver.

Quick Start:
-----------
1. Edit accounts.json with your Google account credentials
2. Review and adjust config.json settings if needed
3. Run youtube_automation.exe

Directory Structure:
------------------
- youtube_automation.exe    : Main application executable
- chromedriver.exe         : Chrome WebDriver for automation
- chrome-win64/            : Portable Chrome browser
- src/                     : Application source modules
- config.json              : Application configuration
- accounts.json            : Account credentials (edit this!)
- browser_profiles/        : Browser profile storage (created on first run)
- logs/                    : Application logs (created on first run)

Configuration:
-------------
- config.json: Contains browser settings, automation parameters, and paths
- accounts.json: Contains Google account credentials for login

Troubleshooting:
---------------
1. If Chrome fails to start:
   - Ensure chrome-win64/chrome.exe exists
   - Check that paths in config.json are correct
   
2. If login fails:
   - Verify credentials in accounts.json
   - Check logs/ directory for detailed error messages
   
3. Windows Defender issues:
   - The executable may trigger false positives
   - Add an exception for youtube_automation.exe

Notes:
------
- First run may take longer as browser profiles are created
- Keep the chrome-win64 directory with the executable
- Do not move files independently - keep the directory structure intact

For more information, check the logs directory after running the application.
"""
        
        self.log("Creating distribution README")
        with open(readme_path, 'w') as f:
            f.write(readme_content)
    
    def build(self):
        """Execute the complete build process."""
        self.log("Starting build process...")
        start_time = time.time()
        
        # Step 1: Verify prerequisites
        if not self.verify_prerequisites():
            return False
        
        # Step 2: Clean build artifacts
        self.clean_build_artifacts()
        
        # Step 3: Run PyInstaller
        if not self.run_pyinstaller():
            return False
        
        # Step 4: Verify build output
        if not self.verify_build_output():
            return False
        
        # Step 5: Create default configs
        self.create_default_configs()
        
        # Step 6: Compress with UPX (optional)
        if self.use_upx:
            self.compress_with_upx()
        
        # Step 7: Create README
        self.create_readme()
        
        # Calculate build time
        build_time = time.time() - start_time
        self.log(f"Build completed successfully in {build_time:.2f} seconds")
        
        # Final summary
        output_dir = self.dist_path / "youtube_automation" if "youtube_automation_dir" in self.spec_file else self.dist_path
        self.log("=" * 60)
        self.log("BUILD SUMMARY")
        self.log("=" * 60)
        self.log(f"Output directory: {output_dir}")
        self.log(f"Executable: {output_dir / 'youtube_automation.exe'}")
        self.log("Next steps:")
        self.log("  1. Navigate to the output directory")
        self.log("  2. Edit accounts.json with your credentials")
        self.log("  3. Run youtube_automation.exe")
        self.log("=" * 60)
        
        return True


def main():
    """Main entry point for the build script."""
    parser = argparse.ArgumentParser(
        description="Build script for YouTube Automation application",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--no-upx",
        action="store_true",
        help="Skip UPX compression"
    )
    
    parser.add_argument(
        "--clean-only",
        action="store_true",
        help="Only clean build artifacts, don't build"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed output"
    )
    
    parser.add_argument(
        "--spec-file",
        default="youtube_automation.spec",
        help="Specify custom spec file (default: youtube_automation.spec)"
    )
    
    args = parser.parse_args()
    
    # Create builder instance
    builder = BuildAutomation(
        verbose=args.verbose,
        use_upx=not args.no_upx,
        spec_file=args.spec_file
    )
    
    # Execute requested action
    if args.clean_only:
        builder.clean_build_artifacts()
        builder.log("Clean completed")
    else:
        success = builder.build()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
