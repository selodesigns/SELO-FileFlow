# Changelog

All notable changes to FileFlow will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial changelog setup
- Release automation with GitHub Actions
- Distribution packaging system

## How to Update This File

When making changes, add them under the [Unreleased] section using these categories:

- **Added** - New features
- **Changed** - Changes in existing functionality
- **Deprecated** - Soon-to-be removed features
- **Removed** - Removed features
- **Fixed** - Bug fixes
- **Security** - Security improvements

When creating a new release:
1. Change [Unreleased] to [Version] - YYYY-MM-DD
2. Add a new [Unreleased] section at the top
3. Update version numbers in:
   - web/package.json
   - Documentation files

## Example Format

```markdown
## [1.0.0] - 2024-10-23

### Added
- Modern web UI with React and TypeScript
- FastAPI REST API backend
- PyQt5 desktop application
- Multi-layered AI content classification
- Cross-platform support (Linux, Windows, macOS)
- Automated file organization with watcher
- Real-time file processing
- Web-based configuration interface

### Changed
- Migrated from CLI-first to Web-first approach
- Improved performance with parallel processing
- Enhanced EXIF metadata extraction

### Fixed
- File permission handling on Windows
- Unicode filename support
- Memory optimization for large file sets

### Security
- Local-only processing (no cloud dependencies)
- Secure file path handling
- Input validation improvements
```

---

## Release Process

1. Update CHANGELOG.md with version details
2. Update version in web/package.json
3. Commit changes: `git commit -am "Release vX.Y.Z"`
4. Create and push tag: `git tag -a vX.Y.Z -m "Release vX.Y.Z" && git push origin vX.Y.Z`
5. GitHub Actions automatically creates release with archives
6. Update website download links
7. Announce release
