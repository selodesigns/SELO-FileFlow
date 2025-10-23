# 📦 FileFlow Packaging Quick Start

This guide shows you how to quickly create downloadable releases for your website.

## 🚀 Two Methods to Distribute FileFlow

### Method 1: Automated (Recommended) ⭐

**Uses GitHub Actions to automatically build and host releases.**

1. **Create a Release:**
   ```bash
   ./scripts/create-release.sh
   ```
   Follow the interactive prompts to create a new version.

2. **GitHub Actions Automatically:**
   - Builds archives for Linux, Windows, and macOS
   - Creates a GitHub Release
   - Generates download links

3. **Get Your Download Links:**
   ```
   https://github.com/selodesigns/SELO-FileFlow/releases/download/v1.0.0/fileflow-v1.0.0-linux.tar.gz
   https://github.com/selodesigns/SELO-FileFlow/releases/download/v1.0.0/fileflow-v1.0.0-windows.zip
   https://github.com/selodesigns/SELO-FileFlow/releases/download/v1.0.0/fileflow-v1.0.0-macos.tar.gz
   ```

4. **Add to Your Website:**
   ```html
   <a href="https://github.com/selodesigns/SELO-FileFlow/releases/latest/download/fileflow-latest-linux.tar.gz">
     Download for Linux
   </a>
   ```

**✅ That's it! GitHub hosts the files for free with unlimited bandwidth.**

---

### Method 2: Manual Build

**Build archives locally and host them yourself.**

1. **Build Release Archives:**
   ```bash
   ./scripts/build-release.sh v1.0.0 all
   ```

2. **Archives Created in `dist/`:**
   - `fileflow-v1.0.0-linux.tar.gz`
   - `fileflow-v1.0.0-windows.zip`
   - `fileflow-v1.0.0-macos.tar.gz`
   - `checksums.txt`

3. **Upload to Your Server:**
   ```bash
   scp dist/* user@yourserver.com:/var/www/downloads/
   ```

4. **Link from Your Website:**
   ```html
   <a href="https://yoursite.com/downloads/fileflow-v1.0.0-linux.tar.gz">
     Download for Linux
   </a>
   ```

---

## 🌐 Website Integration

### Option A: Use the Example HTML Page

A complete, ready-to-use download page is included:

```bash
# Copy to your website
cp scripts/website-download-example.html /path/to/your/website/download.html
```

**Features:**
- ✅ Auto-fetches latest version from GitHub
- ✅ Responsive design
- ✅ Platform detection
- ✅ Installation instructions

**Customize:**
1. Open `scripts/website-download-example.html`
2. Update `GITHUB_REPO` variable
3. Adjust styling to match your website

### Option B: Simple Download Buttons

```html
<!-- Linux -->
<a href="https://github.com/selodesigns/SELO-FileFlow/releases/latest/download/fileflow-latest-linux.tar.gz"
   class="download-btn">
  Download for Linux
</a>

<!-- Windows -->
<a href="https://github.com/selodesigns/SELO-FileFlow/releases/latest/download/fileflow-latest-windows.zip"
   class="download-btn">
  Download for Windows
</a>

<!-- macOS -->
<a href="https://github.com/selodesigns/SELO-FileFlow/releases/latest/download/fileflow-latest-macos.tar.gz"
   class="download-btn">
  Download for macOS
</a>
```

### Option C: JavaScript Dynamic Loading

```html
<div id="download-section">
  <h2>Download FileFlow <span id="version"></span></h2>
  <a href="#" id="linux-download">Linux</a>
  <a href="#" id="windows-download">Windows</a>
  <a href="#" id="macos-download">macOS</a>
</div>

<script>
fetch('https://api.github.com/repos/selodesigns/SELO-FileFlow/releases/latest')
  .then(res => res.json())
  .then(data => {
    const version = data.tag_name;
    document.getElementById('version').textContent = version;
    
    const base = `https://github.com/selodesigns/SELO-FileFlow/releases/download/${version}`;
    document.getElementById('linux-download').href = `${base}/fileflow-${version}-linux.tar.gz`;
    document.getElementById('windows-download').href = `${base}/fileflow-${version}-windows.zip`;
    document.getElementById('macos-download').href = `${base}/fileflow-${version}-macos.tar.gz`;
  });
</script>
```

---

## 📋 Complete Release Workflow

### First Time Setup (One-time)

The packaging system is already set up! You have:
- ✅ Build scripts
- ✅ Release helper
- ✅ GitHub Actions workflow
- ✅ Documentation

### Every Release (3 Steps)

1. **Prepare Release:**
   ```bash
   # Update CHANGELOG.md with release notes
   # Test on all platforms
   # Commit all changes
   ```

2. **Create Release:**
   ```bash
   ./scripts/create-release.sh
   ```
   
3. **Update Website:**
   - Download links auto-update if using GitHub URLs
   - Or manually update links if self-hosting

---

## 🎯 Quick Command Reference

### Create a New Release
```bash
# Interactive (recommended)
./scripts/create-release.sh

# Or manual steps
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

### Build Archives Locally
```bash
# All platforms
./scripts/build-release.sh v1.0.0 all

# Specific platform
./scripts/build-release.sh v1.0.0 linux
```

### Test a Build
```bash
# Build
./scripts/build-release.sh dev linux

# Extract and test
mkdir test && cd test
tar -xzf ../dist/fileflow-dev-linux.tar.gz
cd fileflow-dev-linux
./install.sh
./launch-web.sh
```

---

## 🔗 Download Link Formats

### Latest Release (Always Current)
```
https://github.com/selodesigns/SELO-FileFlow/releases/latest/download/fileflow-latest-linux.tar.gz
```

### Specific Version
```
https://github.com/selodesigns/SELO-FileFlow/releases/download/v1.0.0/fileflow-v1.0.0-linux.tar.gz
```

---

## 💡 Pro Tips

1. **Use GitHub Releases** - Free hosting, unlimited bandwidth
2. **Test Locally First** - Build and test archives before pushing
3. **Keep CHANGELOG.md Updated** - Users appreciate knowing what changed
4. **Semantic Versioning** - Use vMAJOR.MINOR.PATCH format
5. **Verify Checksums** - Include SHA256 checksums for security

---

## 📚 More Information

- **Detailed Guide**: See `DISTRIBUTION.md`
- **Scripts Documentation**: See `scripts/README.md`
- **GitHub Actions**: See `.github/workflows/release.yml`
- **Changelog**: See `CHANGELOG.md`

---

## 🆘 Troubleshooting

**Q: Build script fails?**  
A: Ensure Node.js 18+ and Python 3.8+ are installed

**Q: GitHub Actions fails?**  
A: Check workflow logs at GitHub Actions tab

**Q: Download links don't work?**  
A: Verify release is published (not draft) on GitHub

---

**Ready to create your first release?**

```bash
./scripts/create-release.sh
```
