"""
tree_full.py

A command-line utility that prints a full recursive directory tree starting from
the current working directory.

Features:
- Recursive traversal of all subdirectories
- Exclusion of common or user-defined folders (e.g., venv, .git)
- Optional root-level include filter to show only selected directories/files
- Option to display only folders (exclude all files)
- Optional output redirection to a file
- Clean tree-style visual formatting
- Safe directory scanning using os.scandir()
- Avoids following symlinked directories

Usage:
    python tree_full.py
    python tree_full.py --exclude venv,.git
    python tree_full.py --include-only src,tests
    python tree_full.py --folders
    python tree_full.py --folders -o result.txt
    python tree_full.py -e node_modules,.git -io backend -o structure.txt

Arguments:
    -e, --exclude        Comma-separated directory names to exclude
    -io, --include-only  Comma-separated names to include at root level only
    --folders            Show only folders (exclude files)
    -o, --output         Write output to specified file

Examples:
    python tree_full.py --exclude venv,.git
    python tree_full.py --include-only src,tools
    python tree_full.py --folders
    python tree_full.py --folders -o folders.txt
    python tree_full.py -e node_modules,.git -io backend -o result.txt

Useful for:
- Auditing project structures
- Preparing architecture documentation
- Debugging file layouts
- Sharing repository layouts
- Exporting folder structures for documentation
"""

import os
import argparse
import sys

DEFAULT_EXCLUDES = {"venv", "env", ".venv", "__pycache__", ".git"}


def should_include(entry, include_only, is_root):
    """
    Inclusion logic:
    - If include_only is empty → include everything
    - If at root and include_only exists → include ONLY listed dirs/files
    - Once inside included dir → show everything (except excludes)
    """
    if not include_only:
        return True

    if is_root:
        return entry in include_only

    return True


def print_tree(
    root_path,
    exclude_dirs,
    include_only,
    folders_only=False,
    prefix="",
    is_root=False,
    output_stream=sys.stdout,
):
    try:
        with os.scandir(root_path) as it:
            entries = sorted(
                [
                    e for e in it
                    if e.name not in exclude_dirs
                    and should_include(e.name, include_only, is_root)
                    and (not folders_only or e.is_dir(follow_symlinks=False))
                ],
                key=lambda x: x.name.lower(),
            )
    except PermissionError:
        return

    for index, entry in enumerate(entries):
        connector = "└── " if index == len(entries) - 1 else "├── "
        is_directory = entry.is_dir(follow_symlinks=False)
        label = entry.name + "/" if is_directory else entry.name
        print(prefix + connector + label, file=output_stream)

        if is_directory:
            extension = "    " if index == len(entries) - 1 else "│   "
            print_tree(
                entry.path,
                exclude_dirs,
                include_only,
                folders_only,
                prefix + extension,
                is_root=False,
                output_stream=output_stream,
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
        help="Comma-separated names to include at root level only"
    )

    parser.add_argument(
        "--folders",
        action="store_true",
        help="Show only folders (exclude files)"
    )

    parser.add_argument(
        "-o", "--output",
        help="Write output to file (e.g., result.txt)"
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

    if args.output:
        output_stream = open(args.output, "w", encoding="utf-8")
    else:
        output_stream = sys.stdout

    print(base_path, file=output_stream)

    print_tree(
        base_path,
        exclude_dirs,
        include_only,
        folders_only=args.folders,
        is_root=True,
        output_stream=output_stream
    )

    if args.output:
        output_stream.close()


if __name__ == "__main__":
    main()
