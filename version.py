#!/usr/bin/env python3
"""
Version management script for Unofficial Retro Patch.
Handles version bumping, changelog generation, and GitHub release preparation.
"""

import os
import re
import sys
import subprocess
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple


class VersionManager:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.pyproject_file = self.project_root / "pyproject.toml"
        self.changelog_file = self.project_root / "CHANGELOG.md"
        self.version_pattern = r'version = "(\d+)\.(\d+)\.(\d+)"'
        
    def get_current_version(self) -> Tuple[int, int, int]:
        """Get current version from pyproject.toml."""
        content = self.pyproject_file.read_text()
        match = re.search(self.version_pattern, content)
        if not match:
            raise ValueError("Could not find version in pyproject.toml")
        return tuple(map(int, match.groups()))
    
    def set_version(self, major: int, minor: int, patch: int) -> None:
        """Set version in pyproject.toml."""
        content = self.pyproject_file.read_text()
        new_version = f'version = "{major}.{minor}.{patch}"'
        content = re.sub(self.version_pattern, new_version, content)
        self.pyproject_file.write_text(content)
        print(f"Version set to {major}.{minor}.{patch}")
    
    def bump_version(self, bump_type: str) -> Tuple[int, int, int]:
        """Bump version according to semantic versioning."""
        major, minor, patch = self.get_current_version()
        
        if bump_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif bump_type == "minor":
            minor += 1
            patch = 0
        elif bump_type == "patch":
            patch += 1
        else:
            raise ValueError(f"Invalid bump type: {bump_type}")
        
        self.set_version(major, minor, patch)
        return major, minor, patch
    
    def get_git_changes(self, since_tag: Optional[str] = None) -> List[str]:
        """Get git commits since the last tag or specified tag."""
        if since_tag is None:
            # Get the last tag
            try:
                result = subprocess.run(
                    ["git", "describe", "--tags", "--abbrev=0"],
                    capture_output=True, text=True, check=True
                )
                since_tag = result.stdout.strip()
            except subprocess.CalledProcessError:
                # No tags found, get all commits
                since_tag = ""
        
        if since_tag:
            cmd = ["git", "log", f"{since_tag}..HEAD", "--oneline", "--no-merges"]
        else:
            cmd = ["git", "log", "--oneline", "--no-merges"]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        commits = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
        return commits
    
    def categorize_commits(self, commits: List[str]) -> dict:
        """Categorize commits by type (feat, fix, docs, etc.)."""
        categories = {
            "Features": [],
            "Bug Fixes": [],
            "Documentation": [],
            "Refactoring": [],
            "Other": []
        }
        
        for commit in commits:
            commit_hash, *message_parts = commit.split(' ', 1)
            message = message_parts[0] if message_parts else ""
            
            # Categorize based on conventional commit format
            if message.startswith("feat:"):
                categories["Features"].append((commit_hash, message[5:].strip()))
            elif message.startswith("fix:"):
                categories["Bug Fixes"].append((commit_hash, message[4:].strip()))
            elif message.startswith("docs:"):
                categories["Documentation"].append((commit_hash, message[5:].strip()))
            elif message.startswith("refactor:"):
                categories["Refactoring"].append((commit_hash, message[9:].strip()))
            else:
                categories["Other"].append((commit_hash, message))
        
        return categories
    
    def generate_changelog_entry(self, version: str, commits: List[str]) -> str:
        """Generate a changelog entry for the given version."""
        categories = self.categorize_commits(commits)
        date = datetime.now().strftime("%Y-%m-%d")
        
        entry = f"## [{version}] - {date}\n\n"
        
        for category, commit_list in categories.items():
            if commit_list:
                entry += f"### {category}\n"
                for commit_hash, message in commit_list:
                    entry += f"- {message} ({commit_hash})\n"
                entry += "\n"
        
        return entry
    
    def update_changelog(self, version: str, commits: List[str]) -> None:
        """Update CHANGELOG.md with new version entry."""
        if not self.changelog_file.exists():
            # Create new changelog
            content = f"# Changelog\n\nAll notable changes to this project will be documented in this file.\n\n"
            content += self.generate_changelog_entry(version, commits)
        else:
            # Prepend to existing changelog
            content = self.changelog_file.read_text()
            new_entry = self.generate_changelog_entry(version, commits)
            content = content.replace("# Changelog\n\n", f"# Changelog\n\n{new_entry}")
        
        self.changelog_file.write_text(content)
        print(f"Updated CHANGELOG.md with version {version}")
    
    def create_git_tag(self, version: str, message: Optional[str] = None) -> None:
        """Create a git tag for the version."""
        if message is None:
            message = f"Release version {version}"
        
        subprocess.run(["git", "add", "pyproject.toml", "CHANGELOG.md"], check=True)
        subprocess.run(["git", "commit", "-m", f"Bump version to {version}"], check=True)
        subprocess.run(["git", "tag", "-a", f"v{version}", "-m", message], check=True)
        print(f"Created git tag v{version}")
    
    def build_distribution(self) -> None:
        """Build distribution packages."""
        subprocess.run([sys.executable, "-m", "build"], check=True)
        print("Built distribution packages")
    
    def create_github_release(self, version: str, token: str) -> None:
        """Create a GitHub release using GitHub CLI or API."""
        # Check if GitHub CLI is available
        try:
            subprocess.run(["gh", "--version"], capture_output=True, check=True)
            self._create_github_release_cli(version)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("GitHub CLI not found. Please install it or create the release manually.")
            print(f"Release URL: https://github.com/BALOTIAS/urp/releases/new")
    
    def _create_github_release_cli(self, version: str) -> None:
        """Create GitHub release using GitHub CLI."""
        # Get changelog content for this version
        changelog_content = self.changelog_file.read_text()
        # Extract the entry for this version
        pattern = rf"## \[{version}\].*?(?=## \[|\Z)"
        match = re.search(pattern, changelog_content, re.DOTALL)
        release_notes = match.group(0) if match else f"Release version {version}"
        
        # Create release
        subprocess.run([
            "gh", "release", "create", f"v{version}",
            "--title", f"Release v{version}",
            "--notes", release_notes,
            "--draft"
        ], check=True)
        print(f"Created GitHub release draft for v{version}")
    
    def run_release_workflow(self, bump_type: str, create_release: bool = False) -> None:
        """Run the complete release workflow."""
        print(f"Starting release workflow with {bump_type} bump...")
        
        # Bump version
        major, minor, patch = self.bump_version(bump_type)
        version = f"{major}.{minor}.{patch}"
        
        # Get commits since last tag
        commits = self.get_git_changes()
        
        # Update changelog
        self.update_changelog(version, commits)
        
        # Create git tag
        self.create_git_tag(version)
        
        # Build distribution
        self.build_distribution()
        
        if create_release:
            token = os.getenv("GITHUB_TOKEN")
            if token:
                self.create_github_release(version, token)
            else:
                print("GITHUB_TOKEN not set. Please create the release manually.")
                print(f"Release URL: https://github.com/BALOTIAS/urp/releases/new")
        
        print(f"\nRelease workflow completed!")
        print(f"Version: {version}")
        print(f"Next steps:")
        print(f"1. Review the changes: git log --oneline v{version}")
        print(f"2. Push the tag: git push origin v{version}")
        if not create_release:
            print(f"3. Create GitHub release: https://github.com/BALOTIAS/urp/releases/new")


def main():
    parser = argparse.ArgumentParser(description="Version management for Unofficial Retro Patch")
    parser.add_argument("action", choices=["bump", "release"], help="Action to perform")
    parser.add_argument("--type", choices=["major", "minor", "patch"], default="patch",
                       help="Version bump type (default: patch)")
    parser.add_argument("--create-release", action="store_true",
                       help="Create GitHub release (requires GITHUB_TOKEN)")
    
    args = parser.parse_args()
    
    manager = VersionManager()
    
    if args.action == "bump":
        major, minor, patch = manager.bump_version(args.type)
        print(f"Version bumped to {major}.{minor}.{patch}")
    
    elif args.action == "release":
        manager.run_release_workflow(args.type, args.create_release)


if __name__ == "__main__":
    main()