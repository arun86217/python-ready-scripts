"""
clean_env_folders.py

A command-line utility that recursively scans a directory and deletes common
environment and dependency folders such as Python virtual environments and
Node.js dependency directories.

This tool is useful for quickly cleaning large development directories,
reducing disk usage, and preparing folders for archiving or backup.

Target folders:
    env, venv, .venv, .env, node_modules

Features:
- Recursive directory scanning
- Automatic detection of common environment folders
- Safe deletion with per-folder logging
- Cross-platform (Windows, macOS, Linux)

Requirements:
- Python 3.8+

Usage:

    python clean_env_folders.py <path>

Example:

    python clean_env_folders.py D:/projects

⚠️ WARNING:
    This script permanently deletes folders.
    Review the target path carefully before running.

Designed for:
- Development workspace cleanup
- Removing heavy dependency folders before backup
- Disk space recovery
- Project archiving workflows
"""


import os
import shutil
import sys
from pathlib import Path

TARGET_FOLDERS = {"env", "node_modules", ".env", "venv", ".venv"}


def delete_folders(base_path: Path) -> None:
    """
    Recursively delete common environment and dependency folders.

    Targeted folder names:
        env, venv, .venv, .env, node_modules

    Args:
        base_path (Path): Root directory to scan and clean.
    """
    for root, dirs, _ in os.walk(base_path, topdown=True):
        for dir_name in list(dirs):
            if dir_name in TARGET_FOLDERS:
                folder_path = Path(root) / dir_name
                try:
                    shutil.rmtree(folder_path)
                    print(f"Deleted: {folder_path}")
                except Exception as e:
                    print(f"Failed to delete {folder_path}: {e}")


def main() -> None:
    """
    CLI entry point.

    Usage:
        python clean_env_folders.py <path>

    Example:
        python clean_env_folders.py D:/projects
    """
    if len(sys.argv) != 2:
        print("Usage: python clean_env_folders.py <path>")
        sys.exit(1)

    base_path = Path(sys.argv[1])

    if not base_path.exists():
        print("Error: Path does not exist.")
        sys.exit(1)

    delete_folders(base_path.resolve())


if __name__ == "__main__":
    main()
