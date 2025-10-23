# FileFlow for Windows

Complete guide for installing and using FileFlow on Windows.

## 🚀 Quick Install

### Prerequisites

1. **Python 3.8+** - Download from [python.org](https://www.python.org/downloads/)
   - ✅ Check "Add Python to PATH" during installation
   - ✅ Choose "Install for all users" (recommended)

2. **Node.js 18+** (optional, for Web UI) - Download from [nodejs.org](https://nodejs.org/)
   - ✅ Use the LTS version
   - ✅ Default settings are fine

3. **Git** (optional) - Download from [git-scm.com](https://git-scm.com/)
   - Or download ZIP from GitHub

### Installation

#### Option 1: PowerShell (Recommended)

```powershell
# 1. Clone or download
git clone https://github.com/selodesigns/SELO-FileFlow.git
cd SELO-FileFlow\selo-fileflow

# 2. Run installer
powershell -ExecutionPolicy Bypass -File install.ps1

# 3. Launch
launch-web.bat
```

#### Option 2: Command Prompt

```cmd
# 1. Clone or download
git clone https://github.com/selodesigns/SELO-FileFlow.git
cd SELO-FileFlow\selo-fileflow

# 2. Run installer
install.bat

# 3. Launch
launch-web.bat
```

## 🎯 Usage

### Web Interface

```cmd
launch-web.bat
```

Then open http://localhost:5173 in your browser.

### Desktop Interface

```cmd
launch-desktop.bat
```

### Command Line

```cmd
REM Show help
fileflow.bat --help

REM Organize files once
fileflow.bat --organize-once

REM Start file watcher
fileflow.bat --watch

REM Reorganize with NSFW classification
fileflow.bat --reorganize
```

## 📂 File Locations

### Configuration
```
%USERPROFILE%\.config\fileflow\config.yaml
```

### Default Directories
- **Source**: `%USERPROFILE%\Downloads`
- **Images**: `%USERPROFILE%\Pictures\Organized`
- **Videos**: `%USERPROFILE%\Videos\Organized`
- **Documents**: `%USERPROFILE%\Documents\Organized`

### Launchers
- `launch-web.bat` - Web interface
- `launch-desktop.bat` - Desktop interface
- `fileflow.bat` - CLI helper

## 🔧 Windows-Specific Features

### System Integration

The installer automatically:
- ✅ Creates Start Menu shortcuts (optional)
- ✅ Adds to system PATH (optional)
- ✅ Sets up file associations (optional)

### Performance Optimization

For Windows, FileFlow uses:
- Native file system watchers
- Windows path handling
- Optimized disk I/O

### Security

FileFlow respects Windows UAC and:
- Doesn't require administrator privileges
- Runs in user space
- All analysis is local (no internet required)

## 🛠️ Troubleshooting

### Python not found

**Error**: `'python' is not recognized as an internal or external command`

**Solution**:
1. Reinstall Python from python.org
2. **Check "Add Python to PATH"** during installation
3. Restart Command Prompt/PowerShell

Verify:
```cmd
python --version
```

### Node.js not found

**Error**: `'node' is not recognized as an internal or external command`

**Solution**:
1. Install Node.js from nodejs.org
2. Use the LTS version
3. Restart Command Prompt/PowerShell

Verify:
```cmd
node --version
npm --version
```

### Port Already in Use

**Error**: Address already in use (port 9001)

**Solution**:

Check what's using the port:
```powershell
Get-NetTCPConnection -LocalPort 9001
```

Use a different port:
```cmd
python -m fileflow.main --web --port 9002
```

Then update `web\vite.config.ts` to match.

### Permission Denied

**Error**: Access denied or permission errors

**Solution**:
- Don't run in protected directories (C:\Windows, C:\Program Files)
- Install in your user folder (%USERPROFILE%)
- Run Command Prompt as Administrator if needed (not recommended)

### PyQt5 Installation Failed

**Error**: Failed building wheel for PyQt5

**Solutions**:

1. **Update pip**:
   ```cmd
   python -m pip install --upgrade pip
   ```

2. **Install Visual C++ Redistributables**:
   - Download from [Microsoft](https://aka.ms/vs/17/release/vc_redist.x64.exe)
   - Install and restart

3. **Use pre-built wheel**:
   ```cmd
   pip install --user PyQt5
   ```

### Web UI Won't Load

1. **Check API server is running**:
   ```cmd
   curl http://localhost:9001/health
   ```

2. **Check browser console** (Press F12):
   - Look for errors
   - Check network tab

3. **Disable firewall temporarily**:
   - Windows Defender may block local servers
   - Add exception for Python

4. **Try different browser**:
   - Chrome/Edge recommended
   - Clear cache

### Services Won't Stop

**PowerShell**:
```powershell
Stop-Process -Name python -Force
Stop-Process -Name node -Force
```

**Command Prompt**:
```cmd
taskkill /F /IM python.exe
taskkill /F /IM node.exe
```

## 📦 Optional Dependencies

### ExifTool (for EXIF analysis)

**Windows installer**:
1. Download from [exiftool.org](https://exiftool.org/)
2. Rename `exiftool(-k).exe` to `exiftool.exe`
3. Add to PATH or place in FileFlow directory

**Using Chocolatey**:
```powershell
choco install exiftool
```

### FFmpeg (for video analysis)

**Windows binaries**:
1. Download from [ffmpeg.org](https://ffmpeg.org/download.html)
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to PATH

**Using Chocolatey**:
```powershell
choco install ffmpeg
```

## 🎨 Windows UI Tips

### Desktop UI
- Minimize to system tray
- Right-click tray icon for menu
- Notifications appear in Action Center

### Web UI
- Pin tab in browser for quick access
- Create desktop shortcut to http://localhost:5173
- Use Edge/Chrome for best performance

## 🚀 Advanced Configuration

### Run as Windows Service

1. Install NSSM (Non-Sucking Service Manager):
   ```powershell
   choco install nssm
   ```

2. Create service:
   ```cmd
   nssm install FileFlow "C:\Path\to\python.exe" "-m fileflow.main --watch"
   ```

3. Start service:
   ```cmd
   nssm start FileFlow
   ```

### Schedule with Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (e.g., At log on)
4. Action: Start a program
5. Program: `launch-web.bat` (full path)

### Create Desktop Shortcut

**For Web UI**:
1. Right-click desktop → New → Shortcut
2. Location: `C:\Path\to\SELO-FileFlow\selo-fileflow\launch-web.bat`
3. Name: "FileFlow Web UI"

**For Desktop UI**:
1. Right-click desktop → New → Shortcut
2. Location: `C:\Path\to\SELO-FileFlow\selo-fileflow\launch-desktop.bat`
3. Name: "FileFlow"

## 📊 Performance Tips for Windows

### Optimize for Large Collections

Edit `config.yaml`:
```yaml
performance:
  batch_size: 50           # Lower for Windows
  parallel_workers: 2      # Based on CPU cores
  cache_enabled: true      # Recommended
  memory_limit_mb: 512     # Adjust based on RAM
```

### Exclude from Windows Defender

Add FileFlow directory to exclusions:
1. Windows Security → Virus & threat protection
2. Manage settings → Exclusions
3. Add folder: `SELO-FileFlow\selo-fileflow`

This improves performance during file operations.

## 🔐 Security Notes

- FileFlow runs entirely locally
- No internet connection required
- No telemetry or data collection
- Safe to use on private/sensitive files
- Respects Windows permissions

## 📱 Windows 10/11 Compatibility

| Feature | Windows 10 | Windows 11 |
|---------|------------|------------|
| Web UI | ✅ | ✅ |
| Desktop UI | ✅ | ✅ |
| CLI | ✅ | ✅ |
| File Watcher | ✅ | ✅ |
| NSFW Classification | ✅ | ✅ |
| System Tray | ✅ | ✅ |

## 🆘 Getting Help

### Check Logs

Logs are in:
```
%USERPROFILE%\.cache\fileflow\logs\
```

### Common Issues

1. **"Module not found"**: Reinstall dependencies
2. **"Port in use"**: Change port in config
3. **"Permission denied"**: Run in user directory
4. **"Cannot connect"**: Check firewall

### Report Issues

1. Check existing issues on GitHub
2. Include:
   - Windows version
   - Python version
   - Error messages
   - Log files

## 🎉 Next Steps

- Configure your directories in the web UI
- Enable NSFW classification if needed
- Start organizing your files!
- Check out the full documentation

**Enjoy using FileFlow on Windows!** 🚀
