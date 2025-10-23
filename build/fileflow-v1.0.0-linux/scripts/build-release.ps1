# FileFlow Release Builder for Windows
# Creates distribution archives for direct download

param(
    [string]$Version = "dev",
    [string]$Platform = "all"
)

$ErrorActionPreference = "Stop"

# Configuration
$ProjectName = "fileflow"
$BuildDir = "build"
$DistDir = "dist"
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSCommandPath)

Write-Host "╔════════════════════════════════════════╗" -ForegroundColor Blue
Write-Host "║   FileFlow Release Builder             ║" -ForegroundColor Blue
Write-Host "╚════════════════════════════════════════╝" -ForegroundColor Blue
Write-Host ""
Write-Host "Version: $Version" -ForegroundColor Green
Write-Host "Platform: $Platform" -ForegroundColor Green
Write-Host ""

# Validate version format
if ($Version -ne "dev" -and $Version -notmatch '^v\d+\.\d+\.\d+$') {
    Write-Host "Error: Version must be in format vX.Y.Z (e.g., v1.0.0)" -ForegroundColor Red
    exit 1
}

# Clean previous builds
function Clean-Build {
    Write-Host "→ Cleaning previous builds..." -ForegroundColor Yellow
    Set-Location $ProjectRoot
    
    if (Test-Path $BuildDir) {
        Remove-Item -Recurse -Force $BuildDir
    }
    if (Test-Path $DistDir) {
        Remove-Item -Recurse -Force $DistDir
    }
    
    New-Item -ItemType Directory -Path $BuildDir -Force | Out-Null
    New-Item -ItemType Directory -Path $DistDir -Force | Out-Null
}

# Build web UI
function Build-Web {
    Write-Host "→ Building web UI (production)..." -ForegroundColor Yellow
    Set-Location "$ProjectRoot\web"
    
    # Check if node_modules exists
    if (-not (Test-Path "node_modules")) {
        Write-Host "  Installing Node.js dependencies..." -ForegroundColor Yellow
        npm install
    }
    
    # Build production bundle
    Write-Host "  Building production bundle..." -ForegroundColor Yellow
    npm run build
    
    Write-Host "✓ Web UI built successfully" -ForegroundColor Green
}

# Create Windows archive
function Create-WindowsArchive {
    $ArchiveName = "$ProjectName-$Version-windows"
    $BuildPath = "$ProjectRoot\$BuildDir\$ArchiveName"
    
    Write-Host "→ Creating Windows archive..." -ForegroundColor Yellow
    
    # Create build directory structure
    New-Item -ItemType Directory -Path $BuildPath -Force | Out-Null
    
    # Copy core files
    Write-Host "  Copying core files..." -ForegroundColor Yellow
    Copy-Item -Recurse "$ProjectRoot\fileflow" "$BuildPath\fileflow"
    Copy-Item -Recurse "$ProjectRoot\web\dist" "$BuildPath\web"
    Copy-Item -Recurse "$ProjectRoot\scripts" "$BuildPath\scripts"
    Copy-Item "$ProjectRoot\requirements.txt" "$BuildPath\"
    Copy-Item "$ProjectRoot\README.md" "$BuildPath\"
    Copy-Item "$ProjectRoot\QUICKSTART.md" "$BuildPath\"
    Copy-Item "$ProjectRoot\USER_GUIDE.md" "$BuildPath\"
    Copy-Item "$ProjectRoot\WEB_UI_GUIDE.md" "$BuildPath\"
    Copy-Item "$ProjectRoot\WINDOWS.md" "$BuildPath\"
    Copy-Item "$ProjectRoot\install.bat" "$BuildPath\"
    Copy-Item "$ProjectRoot\install.ps1" "$BuildPath\"
    
    if (Test-Path "$ProjectRoot\LICENSE") {
        Copy-Item "$ProjectRoot\LICENSE" "$BuildPath\"
    }
    
    # Create launcher scripts
    @'
@echo off
cd /d "%~dp0"
call venv\Scripts\activate.bat 2>nul
call scripts\launch-web.bat
'@ | Out-File -FilePath "$BuildPath\launch-web.bat" -Encoding ASCII
    
    @'
@echo off
cd /d "%~dp0"
call venv\Scripts\activate.bat 2>nul
python -m fileflow.gui.main
'@ | Out-File -FilePath "$BuildPath\launch-desktop.bat" -Encoding ASCII
    
    @'
@echo off
cd /d "%~dp0"
call venv\Scripts\activate.bat 2>nul
python -m fileflow.cli %*
'@ | Out-File -FilePath "$BuildPath\fileflow.bat" -Encoding ASCII
    
    # Create INSTALL.txt
    @"
FileFlow $Version - Installation Instructions

1. INSTALL DEPENDENCIES:
   
   > install.bat
   OR
   > powershell -ExecutionPolicy Bypass -File install.ps1

2. LAUNCH:
   
   Web UI (Recommended):
   > launch-web.bat
   Then open: http://localhost:5173
   
   Desktop UI:
   > launch-desktop.bat
   
   CLI:
   > fileflow.bat --help

For detailed instructions, see:
- QUICKSTART.md - Quick start guide
- README.md - Full documentation
- WINDOWS.md - Windows-specific guide

Support: https://github.com/selodesigns/SELO-FileFlow/issues
"@ | Out-File -FilePath "$BuildPath\INSTALL.txt" -Encoding UTF8
    
    # Remove development files
    Get-ChildItem -Path $BuildPath -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force
    Get-ChildItem -Path $BuildPath -Recurse -Directory -Filter ".pytest_cache" | Remove-Item -Recurse -Force
    Get-ChildItem -Path $BuildPath -Recurse -File -Filter "*.pyc" | Remove-Item -Force
    
    # Create ZIP archive
    Write-Host "  Creating ZIP archive..." -ForegroundColor Yellow
    Set-Location "$ProjectRoot\$BuildDir"
    Compress-Archive -Path $ArchiveName -DestinationPath "..\$DistDir\$ArchiveName.zip" -Force
    
    Write-Host "✓ Created: $ArchiveName.zip" -ForegroundColor Green
}

# Generate checksums
function Generate-Checksums {
    Write-Host "→ Generating checksums..." -ForegroundColor Yellow
    
    Set-Location "$ProjectRoot\$DistDir"
    
    $ChecksumFile = "checksums.txt"
    "# SHA256 checksums for FileFlow $Version" | Out-File $ChecksumFile -Encoding UTF8
    "# Generated on $(Get-Date)" | Out-File $ChecksumFile -Append -Encoding UTF8
    "" | Out-File $ChecksumFile -Append -Encoding UTF8
    
    Get-ChildItem -File | Where-Object { $_.Name -ne "checksums.txt" } | ForEach-Object {
        $hash = (Get-FileHash -Algorithm SHA256 $_.FullName).Hash.ToLower()
        "$hash  $($_.Name)" | Out-File $ChecksumFile -Append -Encoding UTF8
    }
    
    Write-Host "✓ Checksums generated" -ForegroundColor Green
}

# Main build process
function Main {
    Clean-Build
    Build-Web
    
    switch ($Platform) {
        "windows" {
            Create-WindowsArchive
        }
        "all" {
            Create-WindowsArchive
            Write-Host ""
            Write-Host "Note: For Linux and macOS archives, run build-release.sh on those platforms" -ForegroundColor Cyan
        }
        default {
            Write-Host "Error: On Windows, only 'windows' and 'all' platforms are supported" -ForegroundColor Red
            exit 1
        }
    }
    
    Generate-Checksums
    
    # Summary
    Write-Host ""
    Write-Host "╔════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║   Build Complete!                      ║" -ForegroundColor Green
    Write-Host "╚════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
    Write-Host "Release archives:" -ForegroundColor Green
    Set-Location $ProjectRoot
    Get-ChildItem "$DistDir" | Format-Table Name, Length
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Green
    Write-Host "1. Test archive on Windows"
    Write-Host "2. Create GitHub release: https://github.com/selodesigns/SELO-FileFlow/releases/new"
    Write-Host "3. Upload archives from: $DistDir\"
    Write-Host "4. Update website download links"
    Write-Host ""
}

# Run main function
Main
