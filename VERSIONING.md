# Versioning System Overview

This document provides an overview of the versioning system implemented for the Unofficial Retro Patch project.

## What Was Implemented

### 1. **Modern Python Packaging** (`pyproject.toml`)
- Standardized project metadata
- Dependency management
- Build configuration
- Development tools configuration

### 2. **Version Management Script** (`version.py`)
- Semantic versioning support
- Automatic version bumping (major/minor/patch)
- Git commit analysis
- Changelog generation from conventional commits
- GitHub release automation

### 3. **GitHub Actions CI/CD**
- **CI Pipeline** (`.github/workflows/ci.yml`):
  - Runs on every push and pull request
  - Multi-Python version testing (3.8-3.11)
  - Linting with flake8, black, mypy
  - Test coverage reporting
  - Build verification

- **Release Pipeline** (`.github/workflows/release.yml`):
  - Triggers on version tags (v*)
  - Automatic GitHub release creation
  - PyPI package upload
  - Distribution file attachment

### 4. **Development Tools**
- **Makefile**: Common development tasks
- **Pre-commit hooks**: Code quality enforcement
- **Test suite**: Comprehensive testing framework
- **Setup script**: Easy environment setup

### 5. **Documentation**
- **CHANGELOG.md**: Automatic changelog generation
- **RELEASE.md**: Detailed release guide
- **Updated README.md**: Development workflow documentation

## Key Features

### Automated Release Process
```bash
# Quick release (patch)
make release-patch

# Manual control
python version.py release --type patch --create-release
```

### Conventional Commits Support
- `feat:` → Features section
- `fix:` → Bug Fixes section  
- `docs:` → Documentation section
- `refactor:` → Refactoring section
- `test:` → Other section
- `chore:` → Other section

### GitHub Integration
- Automatic release creation from tags
- Changelog generation from git history
- PyPI package upload
- Distribution file management

### Development Workflow
```bash
# Setup
./scripts/setup.sh

# Development
make install
make test
make lint
make format

# Release
make release-patch
git push origin v1.2.3
```

## File Structure

```
├── pyproject.toml          # Project configuration
├── version.py              # Version management script
├── CHANGELOG.md           # Generated changelog
├── RELEASE.md             # Release guide
├── Makefile               # Development tasks
├── .pre-commit-config.yaml # Code quality hooks
├── scripts/
│   └── setup.sh          # Setup script
├── tests/
│   ├── __init__.py
│   └── test_version.py   # Version management tests
└── .github/workflows/
    ├── ci.yml            # CI pipeline
    └── release.yml       # Release pipeline
```

## Usage Examples

### For Users
1. Clone repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure `.env` file
4. Run: `python main.py`

### For Developers
1. Setup: `./scripts/setup.sh`
2. Development: `make help`
3. Testing: `make test`
4. Release: `make release-patch`

### For Maintainers
1. Follow conventional commits
2. Use semantic versioning
3. Test before release: `make check`
4. Create releases: `python version.py release --type patch`

## Benefits

1. **Automation**: Reduces manual release work
2. **Consistency**: Standardized release process
3. **Quality**: Automated testing and linting
4. **Documentation**: Automatic changelog generation
5. **Distribution**: PyPI and GitHub releases
6. **Collaboration**: Clear development workflow

## Next Steps

1. **Configure PyPI**: Set up PyPI API token
2. **GitHub Secrets**: Add required secrets to repository
3. **Test Workflow**: Create test release
4. **Documentation**: Update project documentation
5. **Community**: Share release process with contributors

## Troubleshooting

### Common Issues
- **Version conflicts**: Edit `pyproject.toml` manually
- **Changelog issues**: Check commit message format
- **GitHub release fails**: Verify permissions and tokens
- **Build fails**: Check Python version compatibility

### Getting Help
- Check `RELEASE.md` for detailed instructions
- Review GitHub Actions logs for CI/CD issues
- Use `make help` for available commands
- Check test output for debugging information