# FileFlow Quick Start Guide

## 🚀 Installation (3 Simple Steps)

### 1. Clone or Download

```bash
git clone https://github.com/selodesigns/SELO-FileFlow.git
cd SELO-FileFlow/selo-fileflow
```

Or download and extract the ZIP file, then navigate to the `selo-fileflow` directory.

### 2. Run the Installer

```bash
chmod +x install.sh
./install.sh
```

The installer will:
- ✅ Detect your operating system
- ✅ Check for Python 3.8+ and Node.js 18+
- ✅ Install all system dependencies (ExifTool, FFmpeg)
- ✅ Install Python packages (FastAPI, OpenCV, PyQt5, etc.)
- ✅ Install Node.js packages for web UI (React, Vite, etc.)
- ✅ Create launcher scripts
- ✅ Set up desktop integration

**Total time**: ~2-5 minutes depending on your internet speed.

### 3. Launch FileFlow

After installation, you'll be prompted to choose:

**Option 1: Web UI** (Recommended)
```bash
./launch-web.sh
```
Then open your browser to: **http://localhost:5173**

**Option 2: Desktop UI**
```bash
./launch-desktop.sh
```
A native desktop window will appear.

**Option 3: Command Line**
```bash
./fileflow --help
```

---

## 📱 Using FileFlow

### Web Interface (Easiest)

1. **Launch**: `./launch-web.sh`
2. **Open browser**: http://localhost:5173
3. **Configure**:
   - Add source directories (e.g., Downloads folder)
   - Set destination directories (e.g., Pictures, Videos, Documents)
   - Enable NSFW classification if needed
4. **Click "Start Organization"** in the Actions tab
5. **Done!** Files are organized automatically

### Desktop Interface

1. **Launch**: `./launch-desktop.sh`
2. **Configure** folders in the UI
3. **Click "Organize"**
4. **Done!**

### Command Line

```bash
# Organize files once
./fileflow --organize-once

# Start automatic file watcher
./fileflow --watch

# Reorganize with NSFW classification
./fileflow --reorganize

# Launch web interface
./fileflow --web

# Launch desktop UI
./fileflow --ui
```

---

## 🎯 Common Workflows

### First-Time Setup

1. Run `./launch-web.sh`
2. Go to **Configuration** tab
3. Add your Downloads folder as a source
4. Add destination folders (Pictures, Videos, etc.)
5. Go to **File Types** tab to customize extensions
6. Go to **Actions** tab and click "Start Organization"

### Enable Auto-Organization

1. Go to **Watcher** tab in web UI
2. Click "Start Watcher"
3. FileFlow now automatically organizes new files in real-time!

### NSFW Content Classification

1. Go to **Classification** tab
2. Toggle "Enable Content Classification"
3. Adjust sensitivity slider
4. Click "Save Classification Settings"
5. Use "Reorganize" in Actions tab to classify existing files

---

## 📂 Directory Structure

After installation:

```
SELO-FileFlow/selo-fileflow/
├── launch-web.sh          # ← Launch web UI
├── launch-desktop.sh      # ← Launch desktop UI  
├── fileflow              # ← CLI helper
├── install.sh            # Installer script
├── fileflow/             # Python backend
├── web/                  # React frontend
└── config.yaml           # Your configuration
```

Your configuration is also saved at:
```
~/.config/fileflow/config.yaml
```

---

## 🔧 Troubleshooting

### Installation Failed

**Python not found:**
```bash
# Ubuntu/Debian
sudo apt install python3 python3-pip

# macOS
brew install python3
```

**Node.js not found** (for web UI):
```bash
# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# macOS
brew install node
```

### Web UI Won't Start

1. Check if port 9001 is in use:
   ```bash
   lsof -i :9001
   ```

2. Use a different port:
   ```bash
   python3 -m fileflow.main --web --port 9002
   ```

3. Update Vite proxy in `web/vite.config.ts` to match

### Desktop UI Won't Start

Install PyQt5:
```bash
pip install --user PyQt5
```

### Services Not Stopping

Press `Ctrl+C` in the terminal, or:
```bash
pkill -f "fileflow.main"
pkill -f "vite"
```

---

## 💡 Tips

- **Web UI** is best for remote access and modern browsers
- **Desktop UI** is best for local use and system integration
- **CLI** is best for automation and scripting
- Config file is at `~/.config/fileflow/config.yaml`
- Logs are at `~/.cache/fileflow/logs/`
- API documentation: http://localhost:9001/docs

---

## 📚 More Help

- **Web UI Guide**: [WEB_UI_GUIDE.md](WEB_UI_GUIDE.md)
- **Configuration**: Edit `~/.config/fileflow/config.yaml`
- **Issues**: GitHub Issues page
- **Updates**: `git pull` in the project directory

---

## ⚡ Quick Commands Reference

| Command | Description |
|---------|-------------|
| `./install.sh` | Install FileFlow |
| `./launch-web.sh` | Start web interface |
| `./launch-desktop.sh` | Start desktop interface |
| `./fileflow --help` | Show all CLI options |
| `./fileflow --organize-once` | Organize files once |
| `./fileflow --watch` | Start auto-watcher |
| `./fileflow --reorganize` | Apply NSFW classification |

---

**That's it!** FileFlow is ready to organize your files. Enjoy! 🎉
