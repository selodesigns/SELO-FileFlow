# FileFlow Installation Guide

## Overview
FileFlow is an enhanced media content classification and organization system with advanced NSFW/SFW detection capabilities. This guide will help you install all dependencies for optimal performance.

## Quick Start
```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Install system dependencies (Ubuntu/Debian)
sudo apt install libimage-exiftool-perl ffmpeg

# 3. Run FileFlow
python3 -m fileflow.main --ui
```

## Detailed Installation

### 1. Python Dependencies
Install the core Python packages:
```bash
pip install -r requirements.txt
```

This installs:
- **PyYAML**: Configuration file handling
- **Watchdog**: File system monitoring
- **PyQt5**: Graphical user interface
- **OpenCV**: Advanced visual content analysis
- **Pillow**: Image processing and basic EXIF extraction
- **NumPy**: Numerical computing for image analysis
- **pytest**: Testing framework

### 2. System-Level Dependencies

#### EXIF Metadata Analysis (Highly Recommended)
For comprehensive EXIF data extraction and enhanced content classification:

**Ubuntu/Debian:**
```bash
sudo apt install libimage-exiftool-perl
```

**macOS:**
```bash
brew install exiftool
```

**Windows:**
- Download ExifTool from https://exiftool.org/
- Extract and add to your system PATH

#### Video Analysis (Recommended)
For video metadata extraction and analysis:

**Ubuntu/Debian:**
```bash
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
- Download FFmpeg from https://ffmpeg.org/
- Extract and add to your system PATH

### 3. Verification
Test your installation:
```bash
# Test basic functionality
python3 -m fileflow.main --help

# Test enhanced features
python3 test_enhanced_exif.py

# Launch the UI
python3 -m fileflow.main --ui
```

## Feature Availability

### Core Features (Always Available)
- ✅ Filename-based content classification
- ✅ File properties analysis
- ✅ Basic file organization
- ✅ Graphical user interface

### Enhanced Features (Dependency-Based)

#### With Pillow + OpenCV
- ✅ Visual content analysis (skin detection, face detection)
- ✅ Image property analysis
- ✅ Advanced color analysis
- ✅ High-resolution image handling

#### With ExifTool
- ✅ Comprehensive EXIF metadata extraction
- ✅ Camera equipment detection
- ✅ Photo editing software identification
- ✅ GPS/location data analysis
- ✅ Timestamp pattern analysis
- ✅ Content keyword detection in metadata

#### With FFmpeg
- ✅ Video metadata analysis
- ✅ Duration and bitrate analysis
- ✅ Video format detection
- ✅ Frame sampling for visual analysis

## Performance Optimization

### Optional Enhancements
For better performance, consider:

1. **SIMD-Accelerated Pillow** (optional replacement):
   ```bash
   pip uninstall Pillow
   pip install pillow-simd
   ```

2. **GPU Acceleration** for OpenCV (if you have NVIDIA GPU):
   ```bash
   pip uninstall opencv-python
   pip install opencv-contrib-python
   ```

### System Resources
- **RAM**: Minimum 4GB, recommended 8GB+ for large media collections
- **Storage**: SSD recommended for faster file operations
- **CPU**: Multi-core processor recommended for parallel analysis

## Troubleshooting

### Common Issues

#### "ExifTool not found"
- Ensure ExifTool is installed and in your system PATH
- Test with: `exiftool -ver`

#### "FFmpeg not found"
- Ensure FFmpeg is installed and in your system PATH  
- Test with: `ffmpeg -version`

#### "OpenCV import error"
- Try reinstalling: `pip uninstall opencv-python && pip install opencv-python`
- For Ubuntu: `sudo apt install python3-opencv`

#### "PyQt5 display issues"
- For headless systems: `export QT_QPA_PLATFORM=offscreen`
- For X11 forwarding: `export DISPLAY=:0`

#### "Permission denied" errors
- Ensure write permissions to destination directories
- Check file ownership and permissions

### Graceful Degradation
FileFlow is designed to work even with missing optional dependencies:
- Without ExifTool: Falls back to Pillow for basic EXIF extraction
- Without OpenCV: Uses only filename and file property analysis
- Without FFmpeg: Skips video metadata analysis

## Development Setup

For development and testing:
```bash
# Install development dependencies
pip install pytest-cov black flake8

# Run tests
pytest

# Format code
black fileflow/

# Lint code
flake8 fileflow/
```

## Docker Installation (Alternative)

If you prefer containerized deployment:
```bash
# Build Docker image (Dockerfile not included, but can be created)
docker build -t fileflow .

# Run with volume mounts
docker run -v /path/to/media:/media -v /path/to/config:/config fileflow
```

## Next Steps

After installation:
1. **Configure** your source and destination directories in the UI
2. **Test** classification on a small sample of files
3. **Adjust** thresholds and settings as needed
4. **Run** full organization on your media collection

For more information, see the main README.md file.
