# FileFlow PowerShell Installer
# Modern Windows installer with better error handling and features

param(
    [switch]$SkipNodeJs,
    [switch]$NoInteractive
)

$ErrorActionPreference = "Stop"

# Colors
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

function Write-Step($message) {
    Write-ColorOutput Blue "[STEP] $message"
}

function Write-Success($message) {
    Write-ColorOutput Green "[SUCCESS] $message"
}

function Write-Warning($message) {
    Write-ColorOutput Yellow "[WARNING] $message"
}

function Write-ErrorMsg($message) {
    Write-ColorOutput Red "[ERROR] $message"
}

# Header
Write-Host ""
Write-ColorOutput Blue "================================"
Write-ColorOutput Blue "  FileFlow Installation Script  "
Write-ColorOutput Blue "================================"
Write-Host ""

if (-not $NoInteractive) {
    $confirm = Read-Host "This script will install FileFlow and all its dependencies. Continue? (Y/n)"
    if ($confirm -eq 'n' -or $confirm -eq 'N') {
        Write-Host "Installation cancelled."
        exit 0
    }
}

# Check Python
Write-Step "Checking Python installation..."
try {
    $pythonVersion = & python --version 2>&1
    if ($LASTEXITCODE -ne 0) { throw }
    Write-Success "Python $pythonVersion detected"
} catch {
    Write-ErrorMsg "Python is not installed or not in PATH."
    Write-Host "Please install Python 3.8+ from https://www.python.org/"
    Write-Host "Make sure to check 'Add Python to PATH' during installation."
    Read-Host "Press Enter to exit"
    exit 1
}

# Check Python version
$pythonVersionNum = & python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
$versionParts = $pythonVersionNum.Split('.')
$major = [int]$versionParts[0]
$minor = [int]$versionParts[1]

if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 8)) {
    Write-ErrorMsg "Python $pythonVersionNum detected. FileFlow requires Python 3.8 or higher."
    Read-Host "Press Enter to exit"
    exit 1
}

# Check Node.js
Write-Host ""
Write-Step "Checking Node.js installation (for web UI)..."
$hasNodeJs = $false

if (-not $SkipNodeJs) {
    try {
        $nodeVersion = & node --version 2>&1
        if ($LASTEXITCODE -ne 0) { throw }
        
        $nodeVersionNum = $nodeVersion.TrimStart('v')
        $nodeMajor = [int]($nodeVersionNum.Split('.')[0])
        
        if ($nodeMajor -lt 18) {
            Write-Warning "Node.js $nodeVersion detected. Web UI requires Node.js 18+."
            Write-Warning "Please upgrade Node.js for web UI support."
            $hasNodeJs = $false
        } else {
            Write-Success "Node.js $nodeVersion detected"
            $hasNodeJs = $true
        }
    } catch {
        Write-Warning "Node.js is not installed. Web UI will not be available."
        Write-Warning "To install Node.js, visit: https://nodejs.org/"
        Write-Host "Desktop UI and CLI will still work."
        $hasNodeJs = $false
    }
}

# Upgrade pip
Write-Host ""
Write-Step "Upgrading pip..."
& python -m pip install --upgrade pip --user --quiet

# Install Python dependencies
Write-Host ""
Write-Step "Installing Python dependencies..."
if (Test-Path "requirements.txt") {
    & python -m pip install --user -r requirements.txt
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Python dependencies installed"
    } else {
        Write-ErrorMsg "Failed to install some Python dependencies"
        Write-Host "Continuing anyway..."
    }
} else {
    Write-ErrorMsg "requirements.txt not found"
    Read-Host "Press Enter to exit"
    exit 1
}

# Install Node.js dependencies
if ($hasNodeJs -and (Test-Path "web\package.json")) {
    Write-Host ""
    Write-Step "Installing Node.js dependencies for web UI..."
    
    Push-Location web
    try {
        & npm install 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Node.js dependencies installed"
        } else {
            Write-Warning "Some npm packages failed to install"
        }
    } finally {
        Pop-Location
    }
}

# Create config directory
Write-Host ""
Write-Step "Creating configuration directory..."
$configDir = Join-Path $env:USERPROFILE ".config\fileflow"
if (-not (Test-Path $configDir)) {
    New-Item -ItemType Directory -Path $configDir -Force | Out-Null
}

# Create default config
$configFile = Join-Path $configDir "config.yaml"
if (-not (Test-Path $configFile)) {
    Write-Step "Creating default configuration..."
    
    $defaultConfig = @"
# FileFlow Configuration
# Edit this file to customize your file organization

source_directories:
  - "$($env:USERPROFILE)\Downloads"

destination_directories:
  Images: "$($env:USERPROFILE)\Pictures\Organized"
  Videos: "$($env:USERPROFILE)\Videos\Organized"
  Documents: "$($env:USERPROFILE)\Documents\Organized"

# Enhanced content classification settings
content_classification:
  enabled: true
  visual_analysis: true
  filename_analysis: true
  media_only: true
  visual_threshold: 0.5
  nsfw_notifications: false

# File type mappings
file_types:
  Images: [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff"]
  Videos: [".mp4", ".avi", ".mov", ".mkv", ".wmv", ".m4v"]
  Documents: [".pdf", ".doc", ".docx", ".txt", ".rtf"]
"@
    
    $defaultConfig | Out-File -FilePath $configFile -Encoding UTF8
    Write-Success "Default configuration created"
}

# Create launchers
Write-Host ""
Write-Step "Creating launcher scripts..."

# Desktop launcher
$desktopLauncher = @'
@echo off
cd /d "%~dp0"
python -m fileflow.main --ui
if errorlevel 1 pause
'@
$desktopLauncher | Out-File -FilePath "launch-desktop.bat" -Encoding ASCII
Write-Success "Desktop launcher created: launch-desktop.bat"

# Web launcher
if ($hasNodeJs) {
    $webLauncher = @'
@echo off
cd /d "%~dp0"
echo.
echo Starting FileFlow Web UI...
echo ================================
echo.
echo Services:
echo   - API Server: http://localhost:9001
echo   - Web UI: http://localhost:5173
echo   - API Docs: http://localhost:9001/docs
echo.
echo Press Ctrl+C to stop both services
echo.

REM Start API server in background
start /b python -m fileflow.main --web --host 127.0.0.1 --port 9001

REM Wait for API to start
timeout /t 3 /nobreak >nul

REM Start frontend (this will block)
cd web
call npm run dev

REM If we get here, user stopped Vite, so kill Python too
taskkill /f /im python.exe /fi "WINDOWTITLE eq *fileflow*" >nul 2>&1
'@
    $webLauncher | Out-File -FilePath "launch-web.bat" -Encoding ASCII
    Write-Success "Web launcher created: launch-web.bat"
}

# CLI helper
$cliHelper = @'
@echo off
cd /d "%~dp0"
python -m fileflow.main %*
'@
$cliHelper | Out-File -FilePath "fileflow.bat" -Encoding ASCII
Write-Success "CLI helper created: fileflow.bat"

# Completion message
Write-Host ""
Write-ColorOutput Green "================================"
Write-ColorOutput Green "   Installation Complete!      "
Write-ColorOutput Green "================================"
Write-Host ""
Write-ColorOutput Blue "FileFlow has been successfully installed with:"
Write-Host "✅ Advanced content classification capabilities"
Write-Host "✅ Multi-layered NSFW/SFW detection"
Write-Host "✅ EXIF metadata analysis"
Write-Host "✅ Visual content analysis"
if ($hasNodeJs) {
    Write-Host "✅ Modern web interface"
}
Write-Host ""
Write-ColorOutput Blue "Quick Start:"
if ($hasNodeJs) {
    Write-ColorOutput Yellow "  • Launch Web UI: launch-web.bat"
    Write-Host "    Access at: http://localhost:5173"
    Write-Host ""
}
Write-ColorOutput Yellow "  • Launch Desktop UI: launch-desktop.bat"
Write-ColorOutput Yellow "  • CLI Usage: fileflow.bat --help"
Write-Host ""
Write-ColorOutput Blue "Command Examples:"
Write-Host "  • Organize once: fileflow.bat --organize-once"
Write-Host "  • Start watcher: fileflow.bat --watch"
Write-Host "  • Reorganize with NSFW classification: fileflow.bat --reorganize"
Write-Host ""
Write-ColorOutput Blue "Configuration:"
Write-Host "  • Config file: $configFile"
Write-Host "  • Or use the web/desktop UI to configure"
Write-Host ""

# Offer to launch
if (-not $NoInteractive) {
    Write-Host ""
    if ($hasNodeJs) {
        Write-Host "Choose interface:"
        Write-Host "1) Web UI (modern, browser-based)"
        Write-Host "2) Desktop UI (PyQt, native)"
        Write-Host "3) Skip for now"
        Write-Host ""
        $choice = Read-Host "Enter choice (1-3)"
        
        switch ($choice) {
            "1" {
                Write-Host ""
                Write-Host "Launching Web UI..."
                Start-Process "launch-web.bat"
                Start-Sleep -Seconds 5
                Start-Process "http://localhost:5173"
            }
            "2" {
                Write-Host ""
                Write-Host "Launching Desktop UI..."
                Start-Process "launch-desktop.bat"
            }
            default {
                Write-Host ""
                Write-Host "You can launch FileFlow anytime with launch-web.bat or launch-desktop.bat"
            }
        }
    } else {
        $launch = Read-Host "Would you like to launch the Desktop UI now? (Y/n)"
        if ($launch -ne 'n' -and $launch -ne 'N') {
            Write-Host ""
            Write-Host "Launching Desktop UI..."
            Start-Process "launch-desktop.bat"
        }
    }
}

Write-Host ""
Write-Host "Installation complete. Press any key to exit..."
if (-not $NoInteractive) {
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}
