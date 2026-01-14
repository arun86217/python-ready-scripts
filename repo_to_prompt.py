"""
repo_to_prompt.py

Exports the contents of a code repository into structured, prompt-ready text files.
The script walks a directory tree, extracts selected source files, and writes them
into numbered output files with clear file boundaries.

Features:
- Extension-based file filtering
- Include-only directory scoping
- Automatic exclusion of common environment and build folders
- Automatic splitting into multiple output files by line count

Output:
    full_code_part_001.txt
    full_code_part_002.txt
    ...

Usage:
    python repo_to_prompt.py
    python repo_to_prompt.py --root .
    python repo_to_prompt.py --exclude venv .git
    python repo_to_prompt.py --include src utils
    python repo_to_prompt.py --root myrepo --include src --exclude venv .git

Arguments:
    --root        Root directory to scan (default: current directory)
    --include     Space-separated directories to include
    --exclude     Space-separated directories to exclude

Designed for:
- LLM prompt preparation
- Codebase archiving
- Offline review of repositories
- Dataset generation
"""

import os
import argparse

DEFAULT_EXCLUDE_DIRS = {
    "venv", ".git", "__pycache__", "node_modules", ".idea", ".vscode", "vevn"
}

INCLUDE_EXTENSIONS = (
    ".py", ".txt", ".md", ".json", ".yaml", ".yml", ".sql"
)

LINES_PER_FILE = 1200


def repo_to_prompt(root=".", include_dirs=None, exclude_dirs=None):
    repo_name = os.path.basename(os.path.abspath(root))
    part = 1
    line_count = 0

    include_dirs = {os.path.normpath(d) for d in (include_dirs or [])}
    exclude_dirs = set(exclude_dirs or [])

    def open_new_file(part):
        return open(f"full_code_part_{part:03}.txt", "w", encoding="utf-8")

    def is_under_included_dir(path):
        if not include_dirs:
            return True
        rel = os.path.normpath(os.path.relpath(path, root))
        return any(
            rel == inc or rel.startswith(inc + os.sep)
            for inc in include_dirs
        )

    out = open_new_file(part)
    out.write(f"REPOSITORY: {repo_name}\n\n")

    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = os.path.normpath(os.path.relpath(dirpath, root))

        # Always allow root so we can reach included folders
        if rel_dir != "." and not is_under_included_dir(dirpath):
            dirnames[:] = []
            continue

        # Prune directories not leading to an included path
        if include_dirs and rel_dir == ".":
            dirnames[:] = [
                d for d in dirnames
                if any(
                    os.path.normpath(d) == inc or inc.startswith(d + os.sep)
                    for inc in include_dirs
                )
            ]

        # Apply excludes
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]

        for filename in filenames:
            full_path = os.path.join(dirpath, filename)

            # Only write files under included dirs
            if not is_under_included_dir(full_path):
                continue

            if not filename.endswith(INCLUDE_EXTENSIONS):
                continue

            rel_path = os.path.relpath(full_path, root)

            header = [
                "=" * 40,
                f"FILE: {rel_path}",
                "=" * 40
            ]

            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read().splitlines()
            except Exception as e:
                content = [f"# ERROR reading file: {e}"]

            block = header + content + ["", ""]

            if line_count + len(block) > LINES_PER_FILE:
                out.close()
                part += 1
                out = open_new_file(part)
                line_count = 0
                out.write(f"REPOSITORY: {repo_name} (continued)\n\n")

            for line in block:
                out.write(line + "\n")
                line_count += 1

    out.close()
    print(f"Repo split into {part} files")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--include", nargs="*")
    parser.add_argument("--exclude", nargs="*")

    args = parser.parse_args()

    final_excludes = DEFAULT_EXCLUDE_DIRS.union(args.exclude or [])

    repo_to_prompt(
        root=args.root,
        include_dirs=args.include,
        exclude_dirs=final_excludes
    )


