# Release Guide

This document explains how to create releases for the Unofficial Retro Patch project.

## Overview

The project uses semantic versioning and automated release management. Releases are created by:

1. Bumping the version number
2. Generating a changelog from git commits
3. Creating a git tag
4. Building distribution packages
5. Creating a GitHub release (optional)

## Quick Release

For most releases, use the Makefile commands:

```bash
# Patch release (bug fixes)
make release-patch

# Minor release (new features)
make release-minor

# Major release (breaking changes)
make release-major
```

## Manual Release Process

### 1. Bump Version

```bash
# Bump patch version (1.2.3 -> 1.2.4)
python version.py bump --type patch

# Bump minor version (1.2.3 -> 1.3.0)
python version.py bump --type minor

# Bump major version (1.2.3 -> 2.0.0)
python version.py bump --type major
```

### 2. Create Release

```bash
# Create release with automatic changelog generation
python version.py release --type patch

# Create release with GitHub integration (requires GITHUB_TOKEN)
python version.py release --type patch --create-release
```

## Commit Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/) for automatic changelog generation:

- `feat: add new feature` → Features section
- `fix: resolve bug` → Bug Fixes section
- `docs: update README` → Documentation section
- `refactor: improve code` → Refactoring section
- `test: add tests` → Other section
- `chore: update dependencies` → Other section

## GitHub Integration

### Prerequisites

1. Install GitHub CLI:
   ```bash
   # macOS
   brew install gh

   # Ubuntu/Debian
   sudo apt install gh

   # Windows
   winget install GitHub.cli
   ```

2. Authenticate with GitHub:
   ```bash
   gh auth login
   ```

3. Set up GitHub token (optional, for automated releases):
   ```bash
   export GITHUB_TOKEN=your_token_here
   ```

### Automated Release

```bash
python version.py release --type patch --create-release
```

This will:
- Bump version
- Generate changelog
- Create git tag
- Build packages
- Create GitHub release draft

## Manual GitHub Release

1. Push the tag:
   ```bash
   git push origin v1.2.3
   ```

2. Go to GitHub releases page:
   https://github.com/BALOTIAS/urp/releases/new

3. Create release with:
   - Tag: `v1.2.3`
   - Title: `Release v1.2.3`
   - Description: Copy from CHANGELOG.md
   - Upload built packages from `dist/` folder

## CI/CD Pipeline

The GitHub Actions workflow automatically:

- Runs tests on every push
- Builds packages on tag push
- Creates GitHub release on tag push
- Uploads to PyPI (if configured)

## Troubleshooting

### Version Conflicts

If you need to reset version:

```bash
# Edit pyproject.toml manually
# Then commit changes
git add pyproject.toml
git commit -m "fix: reset version to 1.0.0"
```

### Changelog Issues

If changelog is not generated correctly:

1. Check commit messages follow conventional format
2. Ensure git history is available
3. Manually edit CHANGELOG.md if needed

### GitHub Release Issues

1. Check GitHub CLI is installed and authenticated
2. Verify GITHUB_TOKEN is set (if using automated releases)
3. Check repository permissions
4. Create release manually if needed

## Best Practices

1. **Always test before release:**
   ```bash
   make check
   ```

2. **Use conventional commits:**
   ```bash
   git commit -m "feat: add new pixelation algorithm"
   ```

3. **Review changes before release:**
   ```bash
   git log --oneline v1.2.2..HEAD
   ```

4. **Test the release locally:**
   ```bash
   python version.py release --type patch
   # Review changes, then push tag
   ```

5. **Keep releases focused:**
   - One feature/fix per release
   - Clear commit messages
   - Comprehensive changelog

## Version Strategy

- **Patch (0.0.X):** Bug fixes, minor improvements
- **Minor (0.X.0):** New features, backward compatible
- **Major (X.0.0):** Breaking changes, major rewrites

For this project:
- **0.1.x:** Initial development, API may change
- **1.0.0:** First stable release
- **1.x.x:** Stable releases with new features
- **2.0.0:** Breaking changes (if needed)