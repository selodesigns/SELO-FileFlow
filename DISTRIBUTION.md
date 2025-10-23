# FileFlow Distribution Guide

This guide explains how to package FileFlow for direct download distribution on your website.

## 📦 Distribution Options

### 1. **GitHub Releases** (Recommended)
Use GitHub's built-in release system for automatic hosting and version management.

### 2. **Source Code Archives**
Pre-built ZIP/TAR.GZ files with all dependencies included.

### 3. **Standalone Executables** (Future)
PyInstaller-based executables with no dependencies required.

---

## 🚀 Quick Start - Creating a Release

### Method 1: Using Build Scripts (Automated)

```bash
# Create release archives for all platforms
./scripts/build-release.sh v1.0.0

# Or platform-specific
./scripts/build-release.sh v1.0.0 linux
./scripts/build-release.sh v1.0.0 windows
./scripts/build-release.sh v1.0.0 macos
```

This will create:
- `fileflow-v1.0.0-linux.tar.gz`
- `fileflow-v1.0.0-windows.zip`
- `fileflow-v1.0.0-macos.tar.gz`
- `fileflow-v1.0.0-source.tar.gz`

### Method 2: Manual GitHub Release

1. **Prepare Release Archives:**
   ```bash
   ./scripts/build-release.sh v1.0.0
   ```

2. **Create GitHub Release:**
   - Go to: https://github.com/selodesigns/SELO-FileFlow/releases/new
   - Tag: `v1.0.0`
   - Title: `FileFlow v1.0.0 - Release Name`
   - Upload the generated archives
   - Publish release

3. **Download Links:**
   ```
   https://github.com/selodesigns/SELO-FileFlow/releases/download/v1.0.0/fileflow-v1.0.0-linux.tar.gz
   https://github.com/selodesigns/SELO-FileFlow/releases/download/v1.0.0/fileflow-v1.0.0-windows.zip
   https://github.com/selodesigns/SELO-FileFlow/releases/download/v1.0.0/fileflow-v1.0.0-macos.tar.gz
   ```

---

## 🔄 Automated Releases with GitHub Actions

The included `.github/workflows/release.yml` workflow automatically:
- ✅ Triggers on git tag push (`git push origin v1.0.0`)
- ✅ Builds release archives for all platforms
- ✅ Creates GitHub release with archives attached
- ✅ Generates checksums (SHA256)
- ✅ Updates latest release link

**Usage:**
```bash
# Tag a new version
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# GitHub Actions automatically creates the release
```

---

## 📋 Release Checklist

Before creating a release:

- [ ] Update version in `web/package.json`
- [ ] Update version in documentation
- [ ] Test installation on all platforms (Linux, Windows, macOS)
- [ ] Update CHANGELOG.md with release notes
- [ ] Commit all changes
- [ ] Create and push git tag
- [ ] Verify GitHub Actions workflow completes
- [ ] Test download links
- [ ] Update website download links

---

## 🌐 Website Integration

### HTML Download Buttons

```html
<!-- Latest Release -->
<a href="https://github.com/selodesigns/SELO-FileFlow/releases/latest/download/fileflow-latest-linux.tar.gz">
  Download for Linux
</a>

<a href="https://github.com/selodesigns/SELO-FileFlow/releases/latest/download/fileflow-latest-windows.zip">
  Download for Windows
</a>

<a href="https://github.com/selodesigns/SELO-FileFlow/releases/latest/download/fileflow-latest-macos.tar.gz">
  Download for macOS
</a>

<!-- Specific Version -->
<a href="https://github.com/selodesigns/SELO-FileFlow/releases/download/v1.0.0/fileflow-v1.0.0-linux.tar.gz">
  Download FileFlow v1.0.0 (Linux)
</a>
```

### JavaScript Dynamic Version Detection

```javascript
// Fetch latest release info from GitHub API
fetch('https://api.github.com/repos/selodesigns/SELO-FileFlow/releases/latest')
  .then(response => response.json())
  .then(data => {
    document.getElementById('version').textContent = data.tag_name;
    
    // Update download links
    const baseUrl = `https://github.com/selodesigns/SELO-FileFlow/releases/download/${data.tag_name}`;
    document.getElementById('linux-download').href = `${baseUrl}/fileflow-${data.tag_name}-linux.tar.gz`;
    document.getElementById('windows-download').href = `${baseUrl}/fileflow-${data.tag_name}-windows.zip`;
    document.getElementById('macos-download').href = `${baseUrl}/fileflow-${data.tag_name}-macos.tar.gz`;
  });
```

---

## 📦 Archive Contents

Each release archive includes:

```
fileflow-v1.0.0-linux/
├── fileflow/              # Python source code
├── web/                   # Pre-built React app (production)
├── scripts/               # Launch and utility scripts
├── requirements.txt       # Python dependencies
├── install.sh            # Installation script
├── launch-web.sh         # Web UI launcher
├── launch-desktop.sh     # Desktop UI launcher
├── fileflow              # CLI wrapper
├── README.md             # Installation guide
├── QUICKSTART.md         # Quick start guide
└── LICENSE               # License file
```

**Pre-built Web Assets:**
- The `web/dist/` folder contains production-built React app
- No Node.js required for users (already compiled)
- Only Python dependencies need installation

---

## 🔧 Advanced: Standalone Executables

For future consideration, create completely standalone executables with no Python installation required:

### Using PyInstaller

```bash
# Install PyInstaller
pip install pyinstaller

# Create standalone executable (future implementation)
pyinstaller --name fileflow \
  --onefile \
  --add-data "web/dist:web/dist" \
  --add-data "fileflow:fileflow" \
  fileflow/__main__.py
```

**Benefits:**
- ✅ No Python installation required
- ✅ Single executable file
- ✅ Easier for non-technical users

**Considerations:**
- ⚠️ Larger file size (50-100MB+)
- ⚠️ Separate builds needed for each platform
- ⚠️ May trigger antivirus false positives

---

## 🎯 Distribution Strategy

### Tier 1: GitHub Releases (Free, Automated)
- **Best for**: All users
- **Pros**: Free hosting, version management, checksums
- **Hosting**: Automatic via GitHub
- **Bandwidth**: Unlimited

### Tier 2: Direct Website Downloads
- **Best for**: Professional image, branding
- **Pros**: Your domain, custom landing page
- **Hosting**: Host archives on your server or CDN
- **Bandwidth**: Depends on your hosting

### Tier 3: Package Managers (Future)
- **PyPI**: `pip install fileflow`
- **Homebrew**: `brew install fileflow` (macOS)
- **APT/DNF**: Platform-specific repositories (Linux)
- **Chocolatey**: `choco install fileflow` (Windows)

---

## 📊 Release Size Estimates

Approximate compressed archive sizes:

| Archive Type | Size | Contents |
|-------------|------|----------|
| Source (all platforms) | ~500 KB | Python + React source |
| Linux build | ~1.5 MB | Python + pre-built React |
| Windows build | ~1.5 MB | Python + pre-built React |
| macOS build | ~1.5 MB | Python + pre-built React |
| Standalone executable | ~80-120 MB | Bundled Python + all deps |

---

## 🔐 Security & Integrity

### Checksums (SHA256)

All releases include `checksums.txt`:

```
# SHA256 checksums for FileFlow v1.0.0
a1b2c3d4... fileflow-v1.0.0-linux.tar.gz
e5f6g7h8... fileflow-v1.0.0-windows.zip
i9j0k1l2... fileflow-v1.0.0-macos.tar.gz
```

**Verify downloads:**
```bash
# Linux/macOS
sha256sum -c checksums.txt

# Windows
certutil -hashfile fileflow-v1.0.0-windows.zip SHA256
```

### Code Signing (Future Enhancement)

For production releases, consider:
- **macOS**: Apple Developer certificate signing
- **Windows**: Authenticode certificate signing
- **Linux**: GPG signing

---

## 💡 Best Practices

1. **Semantic Versioning**: Use `vMAJOR.MINOR.PATCH` (e.g., v1.0.0)
2. **Changelog**: Maintain detailed CHANGELOG.md
3. **Testing**: Test installation on fresh systems before release
4. **Documentation**: Keep README and guides updated
5. **Backwards Compatibility**: Document breaking changes
6. **Support Policy**: Define LTS versions if applicable

---

## 🆘 Troubleshooting

### Build Fails
- Ensure Node.js 18+ is installed for web build
- Check Python 3.8+ is available
- Verify all dependencies installed

### Large Archive Size
- Exclude unnecessary files in `.gitattributes`
- Remove development dependencies
- Compress more aggressively

### Download Link Doesn't Work
- Verify GitHub release is published (not draft)
- Check tag name matches exactly
- Ensure release assets were uploaded

---

## 📞 Support

For distribution and packaging questions:
- GitHub Issues: https://github.com/selodesigns/SELO-FileFlow/issues
- Documentation: Check repository wiki

---

## 📄 License

Release archives include the MIT License. See LICENSE file for details.
