# FileFlow User Guide

## Table of Contents
1. [Getting Started](#getting-started)
2. [Understanding Content Classification](#understanding-content-classification)
3. [Using the Graphical Interface](#using-the-graphical-interface)
4. [Command Line Usage](#command-line-usage)
5. [Configuration and Settings](#configuration-and-settings)
6. [Advanced Features](#advanced-features)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

---

## Getting Started

### First Launch
After installation, launch FileFlow with:
```bash
python3 -m fileflow.main --ui
```

### Quick Setup Workflow
1. **Configure Folders**: Set up source and destination directories
2. **Test Classification**: Try the classification system on a small sample
3. **Adjust Settings**: Fine-tune thresholds and options
4. **Organize Files**: Run full organization on your media collection

---

## Understanding Content Classification

FileFlow uses a sophisticated **multi-layered analysis system** to classify media files as SFW (Safe for Work) or NSFW (Not Safe for Work).

### Classification Methods

#### 1. **Filename Analysis** (Always Active)
- Scans filenames for NSFW/SFW keywords
- Recognizes common adult content patterns
- Applies SFW override patterns (family, wedding, etc.)

**Examples:**
- `IMG_1234.jpg` → Neutral (requires deeper analysis)
- `vacation_beach.jpg` → SFW (family keyword)
- `adult_content.mp4` → NSFW (explicit keyword)

#### 2. **Visual Content Analysis** (OpenCV Required)
- **Skin Detection**: Analyzes skin tone percentages
- **Face Detection**: Counts and analyzes faces
- **Color Analysis**: Examines color distributions
- **Composition Analysis**: Studies image layout

**What it detects:**
- High skin exposure ratios
- Multiple faces in intimate settings
- Specific color patterns associated with adult content
- Unusual aspect ratios or compositions

#### 3. **EXIF Metadata Analysis** (ExifTool/Pillow)
- **Camera Equipment**: Professional vs smartphone detection
- **Editing Software**: Photoshop, GIMP usage indicators
- **Timestamp Patterns**: Late-night photography
- **GPS Data**: Location-based context
- **Content Keywords**: Metadata descriptions and tags

**Professional indicators:**
- High-end camera equipment (Canon 5D, Nikon D850, etc.)
- Wide aperture settings (f/1.4, f/2.8)
- High ISO settings in low light
- Professional editing software signatures

#### 4. **File Properties Analysis**
- **File Size**: Unusually large media files
- **Duration**: Long video content
- **Bitrate**: High-quality encoding patterns
- **Format**: Specific file types and containers

### Classification Scoring

FileFlow combines all analysis methods into a **confidence score**:
- **0.0 - 0.3**: Likely SFW
- **0.3 - 0.7**: Uncertain (manual review recommended)
- **0.7 - 1.0**: Likely NSFW

---

## Using the Graphical Interface

### Main Window Overview

The FileFlow UI has five main tabs:

#### 1. **Folders Tab**
Configure your media organization:

**Source Directories:**
- Add folders containing mixed media files
- Support for multiple source locations
- Real-time monitoring available

**Destination Directories:**
- Set up organized folder structure
- Categories: Images, Videos, Documents, etc.
- Automatic SFW/NSFW subdirectory creation

**Quick Actions:**
- `Add Source Folder`: Browse and add new source
- `Remove Selected`: Remove unwanted sources
- `Add Destination`: Configure output folders

#### 2. **File Types Tab**
Customize file type handling:

**Supported Formats:**
- **Images**: JPG, PNG, GIF, BMP, WEBP, TIFF
- **Videos**: MP4, AVI, MOV, MKV, WMV
- **Documents**: PDF, DOC, TXT (basic classification)

**Custom Extensions:**
- Add new file types
- Assign to specific categories
- Override default behavior

#### 3. **Custom Mappings Tab**
Create specific file handling rules:

**Pattern Matching:**
- Filename patterns → Destination folders
- Regular expressions supported
- Priority-based rule application

**Examples:**
- `*_family_*` → `Images/SFW/Family`
- `*_vacation_*` → `Images/SFW/Travel`
- `*_private_*` → `Images/NSFW/Private`

#### 4. **Content Classification Tab** ⭐ **NEW**
Control advanced classification features:

**System Status:**
- ✅ **Pillow**: Basic image analysis
- ✅ **OpenCV**: Advanced visual analysis
- ✅ **ExifTool**: Comprehensive metadata extraction

**Classification Settings:**
- ☑️ **Enable Content Classification**: Master toggle
- ☑️ **Enable Visual Analysis**: OpenCV features
- ☑️ **Enable Filename Analysis**: Keyword detection
- ☑️ **Media Files Only**: Skip documents
- ☑️ **NSFW Move Notifications**: Privacy alerts

**Visual Analysis Threshold:**
- Slider: 0.1 (Conservative) → 1.0 (Aggressive)
- Lower values: Fewer false positives
- Higher values: Catches more subtle content

**Actions:**
- `Save Settings`: Store configuration
- `Test Classification`: Try on sample files
- `Reorganize Existing Files`: Apply to current collection

#### 5. **Settings Tab**
General application preferences:

**Monitoring Options:**
- Real-time file watching
- Batch processing intervals
- Performance settings

**Logging:**
- Debug level selection
- Log file locations
- Error reporting

### Using Content Classification

#### Step 1: Configure Sources and Destinations
1. Go to **Folders Tab**
2. Click `Add Source Folder` and select your mixed media directory
3. Add destinations for each category (Images, Videos, etc.)

#### Step 2: Set Up Classification
1. Go to **Content Classification Tab**
2. Verify system status (green checkmarks)
3. Enable desired analysis methods:
   - ✅ **Content Classification**: Always recommended
   - ✅ **Visual Analysis**: For image content analysis
   - ✅ **Filename Analysis**: For keyword detection
4. Adjust **Visual Analysis Threshold** (start with 0.5)

#### Step 3: Test on Sample Files
1. Click `Test Classification` button
2. Select a few sample files from your collection
3. Review results and accuracy
4. Adjust threshold if needed

#### Step 4: Run Full Organization
1. Click `Reorganize Existing Files` for current files
2. Or use file watching for new files
3. Monitor progress in the status bar
4. Review results in destination folders

---

## Command Line Usage

### Basic Commands

#### Organize Files Once
```bash
python3 -m fileflow.main --organize-once
```
Processes all files in source directories once.

#### Watch for New Files
```bash
python3 -m fileflow.main --watch
```
Continuously monitors source directories for new files.

#### Reorganize Existing Files
```bash
python3 -m fileflow.main --reorganize
```
Applies content classification to existing organized files.

#### Launch GUI
```bash
python3 -m fileflow.main --ui
```
Opens the graphical user interface.

### Advanced Command Line Options

#### Custom Configuration
```bash
python3 -m fileflow.main --config /path/to/custom/config.yaml --organize-once
```

#### Verbose Output
```bash
python3 -m fileflow.main --verbose --watch
```

#### Dry Run (Preview Only)
```bash
python3 -m fileflow.main --dry-run --reorganize
```

---

## Configuration and Settings

### Configuration File Location
- **Linux**: `~/.config/selo-fileflow/config.yaml`
- **macOS**: `~/Library/Application Support/selo-fileflow/config.yaml`
- **Windows**: `%APPDATA%/selo-fileflow/config.yaml`

### Sample Configuration
```yaml
# Source directories to monitor
source_directories:
  - "/home/user/Downloads"
  - "/home/user/Pictures/Mixed"

# Destination directories by category
destination_directories:
  Images: "/home/user/Pictures/Organized"
  Videos: "/home/user/Videos/Organized"
  Documents: "/home/user/Documents/Organized"

# Content classification settings
content_classification:
  enabled: true
  visual_analysis: true
  filename_analysis: true
  media_only: true
  visual_threshold: 0.5
  nsfw_notifications: false

# File type mappings
file_types:
  Images: [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]
  Videos: [".mp4", ".avi", ".mov", ".mkv", ".wmv"]
  Documents: [".pdf", ".doc", ".docx", ".txt"]

# Custom filename mappings
custom_mappings:
  "*family*": "Images/SFW/Family"
  "*vacation*": "Images/SFW/Travel"
  "*work*": "Images/SFW/Professional"
```

### Editing Configuration
1. **Via GUI**: Use the Settings tab
2. **Direct Edit**: Open config file in text editor
3. **Command Line**: Use `--config` parameter

---

## Advanced Features

### Batch Processing
For large media collections:

```bash
# Process in smaller batches
python3 -m fileflow.main --batch-size 100 --organize-once

# Parallel processing
python3 -m fileflow.main --workers 4 --reorganize
```

### Custom Classification Rules

#### Creating Custom Patterns
```yaml
custom_nsfw_keywords:
  - "private"
  - "personal" 
  - "intimate"

custom_sfw_overrides:
  - "family_private"  # Family photos marked private
  - "work_personal"   # Personal work photos
```

#### EXIF-Based Rules
```yaml
exif_rules:
  camera_brands:
    professional: ["Canon", "Nikon", "Sony"]
    smartphone: ["iPhone", "Samsung", "Pixel"]
  
  suspicious_software:
    - "Photoshop"
    - "GIMP" 
    - "Lightroom"
```

### Performance Optimization

#### For Large Collections
1. **Enable Caching**: Speeds up repeated analysis
2. **Adjust Batch Size**: Balance memory vs speed
3. **Use SSD Storage**: Faster file operations
4. **Increase RAM**: Better for parallel processing

#### Memory Management
```yaml
performance:
  cache_enabled: true
  cache_size_mb: 512
  batch_size: 50
  parallel_workers: 2
```

### Integration with Other Tools

#### Export Results
```bash
# Export classification results to CSV
python3 -m fileflow.main --export-results results.csv

# Generate classification report
python3 -m fileflow.main --generate-report report.html
```

#### API Usage
```python
from fileflow.robust_content_classifier import RobustContentClassifier

classifier = RobustContentClassifier()
result = classifier.classify_media_file(Path("image.jpg"))
print(f"NSFW Score: {result['nsfw_score']}")
```

---

## Troubleshooting

### Common Issues

#### "No files being processed"
**Symptoms**: FileFlow runs but no files are moved
**Solutions**:
1. Check source directory paths in configuration
2. Verify file permissions (read/write access)
3. Ensure file types are in supported extensions
4. Check if files are already organized

#### "Classification seems inaccurate"
**Symptoms**: Wrong SFW/NSFW classifications
**Solutions**:
1. Adjust visual analysis threshold (try 0.3-0.7 range)
2. Enable/disable specific analysis methods
3. Add custom keywords to override patterns
4. Review and update filename patterns

#### "Performance is slow"
**Symptoms**: Long processing times
**Solutions**:
1. Reduce batch size for memory-constrained systems
2. Disable visual analysis for faster processing
3. Enable caching for repeated operations
4. Use SSD storage for better I/O performance

#### "EXIF analysis not working"
**Symptoms**: Missing metadata in classification
**Solutions**:
1. Install ExifTool: `sudo apt install libimage-exiftool-perl`
2. Verify installation: `exiftool -ver`
3. Check file permissions
4. Try with different image formats

#### "Visual analysis disabled"
**Symptoms**: OpenCV features not available
**Solutions**:
1. Install OpenCV: `pip install opencv-python`
2. Check system dependencies
3. Verify camera/webcam access (if needed)
4. Try reinstalling with: `pip uninstall opencv-python && pip install opencv-python`

### Debug Mode
Enable detailed logging:
```bash
python3 -m fileflow.main --debug --organize-once
```

Check log files:
- **Linux**: `~/.cache/selo-fileflow/logs/`
- **macOS**: `~/Library/Logs/selo-fileflow/`
- **Windows**: `%TEMP%/selo-fileflow/logs/`

### Getting Help
1. **Check logs**: Look for error messages
2. **Run verification**: `python3 verify_installation.py`
3. **Test components**: Use individual test scripts
4. **Report issues**: Include logs and system information

---

## Best Practices

### Initial Setup
1. **Start Small**: Test with a small sample of files first
2. **Backup Important Files**: Always keep originals safe
3. **Review Classifications**: Manually check first few results
4. **Adjust Gradually**: Fine-tune settings based on results

### Ongoing Usage
1. **Regular Reviews**: Periodically check classification accuracy
2. **Update Keywords**: Add new patterns as needed
3. **Monitor Performance**: Watch for slowdowns or errors
4. **Backup Configuration**: Save your settings

### Privacy and Security
1. **Local Processing**: All analysis happens on your machine
2. **No Cloud Upload**: Files never leave your system
3. **Secure Storage**: Use encrypted drives for sensitive content
4. **Access Control**: Set appropriate file permissions

### Organization Strategy
1. **Consistent Naming**: Use clear, descriptive folder names
2. **Logical Hierarchy**: Create intuitive directory structures
3. **Regular Cleanup**: Remove duplicates and unwanted files
4. **Documentation**: Keep notes on your organization system

### Performance Tips
1. **SSD Storage**: Use solid-state drives for better performance
2. **Adequate RAM**: 8GB+ recommended for large collections
3. **Batch Processing**: Process files in manageable chunks
4. **Regular Maintenance**: Clear caches and temporary files

---

## Example Workflows

### Workflow 1: New User Setup
1. Install FileFlow and dependencies
2. Run `python3 verify_installation.py`
3. Launch GUI: `python3 -m fileflow.main --ui`
4. Configure one source folder with mixed content
5. Set up basic destination structure
6. Enable content classification with default settings
7. Test on 10-20 sample files
8. Adjust threshold based on results
9. Run full organization

### Workflow 2: Large Collection Migration
1. Create backup of original files
2. Set up FileFlow with optimized settings
3. Process in batches of 500-1000 files
4. Review results after each batch
5. Fine-tune settings based on accuracy
6. Complete full migration
7. Verify organization structure

### Workflow 3: Ongoing Maintenance
1. Set up file watching for new downloads
2. Weekly review of classifications
3. Monthly adjustment of keywords/patterns
4. Quarterly performance optimization
5. Annual backup and cleanup

---

This comprehensive guide covers all aspects of using FileFlow effectively. For additional help, refer to the technical documentation or run the built-in verification tools.
