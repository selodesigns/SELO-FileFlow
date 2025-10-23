# FileFlow Scripts

This directory contains utility scripts for building, releasing, and managing FileFlow.

## 📦 Release & Build Scripts

### `build-release.sh` (Linux/macOS)
Creates distribution archives for direct download.

**Usage:**
```bash
# Build all platforms
./scripts/build-release.sh v1.0.0 all

# Build specific platform
./scripts/build-release.sh v1.0.0 linux
./scripts/build-release.sh v1.0.0 windows
./scripts/build-release.sh v1.0.0 macos
```

**Output:**
- `dist/fileflow-v1.0.0-linux.tar.gz`
- `dist/fileflow-v1.0.0-windows.zip`
- `dist/fileflow-v1.0.0-macos.tar.gz`
- `dist/fileflow-v1.0.0-source.tar.gz`
- `dist/checksums.txt`

**Features:**
- ✅ Builds production web UI
- ✅ Creates platform-specific archives
- ✅ Includes all necessary files
- ✅ Generates SHA256 checksums
- ✅ Removes development files

---

### `build-release.ps1` (Windows)
Windows PowerShell version of the build script.

**Usage:**
```powershell
# Build Windows archive
.\scripts\build-release.ps1 -Version "v1.0.0" -Platform "windows"
```

---

### `create-release.sh` (Linux/macOS)
Interactive helper for creating new releases with version management.

**Usage:**
```bash
# Interactive mode (recommended)
./scripts/create-release.sh

# Quick mode
./scripts/create-release.sh --quick 1.0.0
```

**Features:**
- ✅ Interactive release checklist
- ✅ Version validation and updates
- ✅ Automatic git tagging
- ✅ CHANGELOG.md reminders
- ✅ Safe with uncommitted changes check

**Process:**
1. Prompts for new version
2. Updates `web/package.json`
3. Commits version bump
4. Creates git tag
5. Pushes to trigger GitHub Actions

---

## 🚀 Launcher Scripts

These scripts are copied into release archives for easy launching.

### Web UI Launchers
- `launch-web.sh` (Linux/macOS)
- `launch-web.bat` (Windows)

### Desktop UI Launchers
- `launch-desktop.sh` (Linux/macOS)
- `launch-desktop.bat` (Windows)

### CLI Wrappers
- `fileflow` (Linux/macOS)
- `fileflow.bat` (Windows)

---

## 🌐 Website Integration

### `website-download-example.html`
Example download page template for your website.

**Features:**
- ✅ Modern, responsive design
- ✅ Auto-fetches latest release from GitHub API
- ✅ Platform detection buttons
- ✅ Installation instructions
- ✅ Checksum verification info

**Customize:**
1. Update `GITHUB_REPO` variable
2. Adjust styling to match your website
3. Add analytics/tracking if desired

**JavaScript API Integration:**
```javascript
// Fetch latest release
const response = await fetch('https://api.github.com/repos/selodesigns/SELO-FileFlow/releases/latest');
const data = await response.json();

// Get version
const version = data.tag_name;

// Build download URLs
const linuxUrl = `https://github.com/selodesigns/SELO-FileFlow/releases/download/${version}/fileflow-${version}-linux.tar.gz`;
```

---

## 🔄 Automated Releases

GitHub Actions workflow (`.github/workflows/release.yml`) automatically:
1. Triggers on git tag push (`v*.*.*`)
2. Builds all platform archives
3. Creates GitHub release
4. Uploads archives
5. Generates checksums

**Trigger a release:**
```bash
# Option 1: Using create-release.sh (recommended)
./scripts/create-release.sh

# Option 2: Manual tagging
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

---

## 📋 Release Checklist

Before creating a release:

- [ ] Test on all platforms (Linux, Windows, macOS)
- [ ] Update version in `web/package.json`
- [ ] Update `CHANGELOG.md` with release notes
- [ ] Update documentation if needed
- [ ] Run tests: `pytest tests/`
- [ ] Build and test archives locally
- [ ] Review changes: `git diff`
- [ ] Commit all changes
- [ ] Run `./scripts/create-release.sh`
- [ ] Monitor GitHub Actions workflow
- [ ] Verify release on GitHub
- [ ] Test download links
- [ ] Update website download page

---

## 📂 Archive Structure

Each release archive contains:

```
fileflow-v1.0.0-linux/
├── fileflow/              # Python source code
│   ├── __init__.py
│   ├── cli.py
│   ├── config.py
│   ├── organizer.py
│   ├── watcher.py
│   └── ...
├── web/                   # Pre-built React app
│   └── dist/
│       ├── index.html
│       ├── assets/
│       └── ...
├── scripts/               # Launch and utility scripts
│   ├── launch-web.sh
│   ├── launch-desktop.sh
│   └── ...
├── requirements.txt       # Python dependencies
├── install.sh            # Installation script
├── launch-web.sh         # Web UI launcher
├── launch-desktop.sh     # Desktop UI launcher
├── fileflow              # CLI wrapper
├── INSTALL.txt           # Quick installation guide
├── README.md             # Full documentation
├── QUICKSTART.md         # Quick start guide
├── USER_GUIDE.md         # User guide
├── WEB_UI_GUIDE.md       # Web UI guide
└── LICENSE               # License file
```

---

## 🛠️ Development

### Testing Build Scripts Locally

```bash
# Test build (without pushing)
./scripts/build-release.sh dev all

# Check output
ls -lh dist/

# Extract and test
mkdir test-build
cd test-build
tar -xzf ../dist/fileflow-dev-linux.tar.gz
cd fileflow-dev-linux
./install.sh
./launch-web.sh
```

### Adding New Platforms

To add support for a new platform:

1. Add platform case in `build-release.sh`
2. Create platform-specific launcher scripts
3. Update documentation
4. Test thoroughly on target platform

---

## 🔐 Security

### Checksums
All releases include `checksums.txt` with SHA256 hashes.

**Verify:**
```bash
# Linux/macOS
sha256sum -c checksums.txt

# Windows
certutil -hashfile filename.zip SHA256
```

### Code Signing (Future)
Consider signing releases for production:
- **macOS**: Apple Developer certificate
- **Windows**: Authenticode certificate
- **Linux**: GPG signing

---

## 📞 Support

For issues with scripts or releases:
- GitHub Issues: https://github.com/selodesigns/SELO-FileFlow/issues
- Documentation: See `DISTRIBUTION.md` for detailed info

---

## 📄 License

These scripts are part of FileFlow and are covered by the MIT License.
