"""
Tests for version management functionality.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
import subprocess

from version import VersionManager


class TestVersionManager:
    @pytest.fixture
    def temp_project(self):
        """Create a temporary project directory for testing."""
        temp_dir = tempfile.mkdtemp()
        project_dir = Path(temp_dir) / "test_project"
        project_dir.mkdir()
        
        # Create a test pyproject.toml
        pyproject_content = '''[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "test-project"
version = "1.2.3"
description = "Test project"
'''
        (project_dir / "pyproject.toml").write_text(pyproject_content)
        
        yield project_dir
        
        shutil.rmtree(temp_dir)
    
    def test_get_current_version(self, temp_project):
        """Test getting current version from pyproject.toml."""
        with patch('version.Path') as mock_path:
            mock_path.return_value.parent = temp_project
            manager = VersionManager()
            version = manager.get_current_version()
            assert version == (1, 2, 3)
    
    def test_set_version(self, temp_project):
        """Test setting version in pyproject.toml."""
        with patch('version.Path') as mock_path:
            mock_path.return_value.parent = temp_project
            manager = VersionManager()
            manager.set_version(2, 0, 0)
            
            # Check that the version was updated
            content = (temp_project / "pyproject.toml").read_text()
            assert 'version = "2.0.0"' in content
    
    def test_bump_version_patch(self, temp_project):
        """Test patch version bump."""
        with patch('version.Path') as mock_path:
            mock_path.return_value.parent = temp_project
            manager = VersionManager()
            major, minor, patch = manager.bump_version("patch")
            assert (major, minor, patch) == (1, 2, 4)
    
    def test_bump_version_minor(self, temp_project):
        """Test minor version bump."""
        with patch('version.Path') as mock_path:
            mock_path.return_value.parent = temp_project
            manager = VersionManager()
            major, minor, patch = manager.bump_version("minor")
            assert (major, minor, patch) == (1, 3, 0)
    
    def test_bump_version_major(self, temp_project):
        """Test major version bump."""
        with patch('version.Path') as mock_path:
            mock_path.return_value.parent = temp_project
            manager = VersionManager()
            major, minor, patch = manager.bump_version("major")
            assert (major, minor, patch) == (2, 0, 0)
    
    def test_bump_version_invalid(self, temp_project):
        """Test invalid bump type raises error."""
        with patch('version.Path') as mock_path:
            mock_path.return_value.parent = temp_project
            manager = VersionManager()
            with pytest.raises(ValueError, match="Invalid bump type"):
                manager.bump_version("invalid")
    
    @patch('subprocess.run')
    def test_get_git_changes(self, mock_run, temp_project):
        """Test getting git changes."""
        with patch('version.Path') as mock_path:
            mock_path.return_value.parent = temp_project
            manager = VersionManager()
            
            # Mock git log output
            mock_run.return_value.stdout = "abc123 feat: new feature\n"
            mock_run.return_value.returncode = 0
            
            commits = manager.get_git_changes()
            assert commits == ["abc123 feat: new feature"]
    
    def test_categorize_commits(self, temp_project):
        """Test commit categorization."""
        with patch('version.Path') as mock_path:
            mock_path.return_value.parent = temp_project
            manager = VersionManager()
            
            commits = [
                "abc123 feat: add new feature",
                "def456 fix: resolve bug",
                "ghi789 docs: update README",
                "jkl012 refactor: improve code",
                "mno345 chore: update dependencies"
            ]
            
            categories = manager.categorize_commits(commits)
            
            assert len(categories["Features"]) == 1
            assert len(categories["Bug Fixes"]) == 1
            assert len(categories["Documentation"]) == 1
            assert len(categories["Refactoring"]) == 1
            assert len(categories["Other"]) == 1
    
    def test_generate_changelog_entry(self, temp_project):
        """Test changelog entry generation."""
        with patch('version.Path') as mock_path:
            mock_path.return_value.parent = temp_project
            manager = VersionManager()
            
            commits = [
                "abc123 feat: add new feature",
                "def456 fix: resolve bug"
            ]
            
            entry = manager.generate_changelog_entry("1.2.3", commits)
            
            assert "## [1.2.3]" in entry
            assert "### Features" in entry
            assert "### Bug Fixes" in entry
            assert "add new feature" in entry
            assert "resolve bug" in entry
    
    def test_update_changelog_new_file(self, temp_project):
        """Test creating new changelog file."""
        with patch('version.Path') as mock_path:
            mock_path.return_value.parent = temp_project
            manager = VersionManager()
            
            commits = ["abc123 feat: initial release"]
            manager.update_changelog("1.0.0", commits)
            
            changelog_file = temp_project / "CHANGELOG.md"
            assert changelog_file.exists()
            
            content = changelog_file.read_text()
            assert "# Changelog" in content
            assert "## [1.0.0]" in content
    
    def test_update_changelog_existing_file(self, temp_project):
        """Test updating existing changelog file."""
        with patch('version.Path') as mock_path:
            mock_path.return_value.parent = temp_project
            manager = VersionManager()
            
            # Create existing changelog
            changelog_content = """# Changelog

## [1.0.0] - 2023-01-01

### Features
- Initial release
"""
            changelog_file = temp_project / "CHANGELOG.md"
            changelog_file.write_text(changelog_content)
            
            commits = ["abc123 feat: new feature"]
            manager.update_changelog("1.1.0", commits)
            
            content = changelog_file.read_text()
            assert "## [1.1.0]" in content
            assert "## [1.0.0]" in content  # Old entry should still be there