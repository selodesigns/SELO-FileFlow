# SELO FileFlow

A professional file management solution from SELOdev that automatically organizes files downloaded from web browsers into appropriate directories based on file types.

## Features

- Monitors your downloads folder for new files
- Automatically categorizes files into:
  - Images
  - Documents
  - Videos
  - Software
  - Other
- Runs in the background as a system service
- Configurable paths and file type mappings
- Modern UI with custom application icon

## Requirements

### For Development
- Python 3.13+
- watchdog
- pyyaml
- PyQt5

### For End Users
- Windows 10/11 (for installer version)
- No Python installation required for the standalone executable

## Installation

### Development Version
1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Configure the application in `config/settings.yaml`

### Standalone Executable (Windows)
1. Download the latest installer (`SELO-FileFlow-Setup-x.x.x.exe`) from the releases page
2. Run the installer and follow the on-screen instructions
3. Launch SELO FileFlow from your Start menu or desktop shortcut
4. The application will automatically create a default configuration on first run

## Usage

Run the application with:

```
python -m src.main
```

To run as a background service, use the provided service scripts in the `scripts` directory.

## Configuration

Edit `config/settings.yaml` to customize:
- Source directory (downloads folder)
- Destination directories
- File type mappings
- Logging settings

## License

MIT
