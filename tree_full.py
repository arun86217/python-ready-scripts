"""
tree_full.py

A command-line utility that prints a full recursive directory tree starting from
the current working directory.

Features:
- Recursive traversal of all subdirectories
- Exclusion of common or user-defined folders (e.g., venv, .git)
- Optional root-level include filter to show only selected directories/files
- Clean tree-style visual formatting

Usage:
    python tree_full.py
    python tree_full.py --exclude venv,.git
    python tree_full.py --include-only src,tests
    python tree_full.py --exclude venv,.git --include-only src

Arguments:
    -e, --exclude        Comma-separated directory names to exclude
    -io, --include-only  Comma-separated names to include at root level only

Examples:
    python tree_full.py --exclude venv,.git
    python tree_full.py --include-only src,tools
    python tree_full.py -e node_modules,.git -io backend

Useful for:
- Auditing project structures
- Preparing architecture documentation
- Debugging file layouts
- Sharing repository layouts
"""

import os
import argparse

DEFAULT_EXCLUDES = {"venv", "env", ".venv", "__pycache__", ".git"}


def should_include(entry, include_only, is_root):
    """
    Inclusion logic:
    - If include_only is empty → include everything (normal behavior)
    - If at root and include_only exists → include ONLY listed dirs/files
    - Once inside included dir → show everything (except excludes)
    """
    if not include_only:
        return True

    if is_root:
        return entry in include_only

    return True


def print_tree(root_path, exclude_dirs, include_only, prefix="", is_root=False):
    try:
        entries = sorted(os.listdir(root_path))
    except PermissionError:
        return

    entries = [
        e for e in entries
        if e not in exclude_dirs and should_include(e, include_only, is_root)
    ]

    for index, entry in enumerate(entries):
        path = os.path.join(root_path, entry)
        connector = "└── " if index == len(entries) - 1 else "├── "
        print(prefix + connector + entry)

        if os.path.isdir(path):
            extension = "    " if index == len(entries) - 1 else "│   "
            print_tree(
                path,
                exclude_dirs,
                include_only,
                prefix + extension,
                is_root=False
            )


def main():
    parser = argparse.ArgumentParser(description="Print directory tree")

    parser.add_argument(
        "-e", "--exclude",
        default="",
        help="Comma-separated directory names to exclude"
    )

    parser.add_argument(
        "-io", "--include-only",
        default="",
        help="Comma-separated directory names to include at root level only"
    )

    args = parser.parse_args()

    exclude_dirs = set(DEFAULT_EXCLUDES)
    if args.exclude:
        for name in args.exclude.split(","):
            name = name.strip()
            if name:
                exclude_dirs.add(name)

    include_only = set()
    if args.include_only:
        for name in args.include_only.split(","):
            name = name.strip()
            if name:
                include_only.add(name)

    base_path = os.getcwd()

    print(base_path)
    print_tree(
        base_path,
        exclude_dirs,
        include_only,
        is_root=True
    )


if __name__ == "__main__":
    main()

