"""
repo_to_prompt.py

Exports the contents of a code repository into structured, prompt-ready text files.
The script walks a directory tree, extracts selected source files, and writes them
into numbered output files with clear file boundaries.

Features
- Extension-based file filtering (dynamic include/exclude)
- File-level filtering (include/exclude specific files)
- Directory-level filtering (include/exclude folders)
- Automatic exclusion of common environment and build folders
- Automatic splitting into multiple output files by line count
- Clipboard export support
- Clipboard-only export mode
- Deterministic ordering for reproducibility

Output
    full_code_part_001.txt
    full_code_part_002.txt
    ...

Usage

Default (uses built-in defaults)
    python repo_to_prompt.py

Clipboard + files
    python repo_to_prompt.py -c

Clipboard only
    python repo_to_prompt.py -oc

Include only certain directories
    python repo_to_prompt.py -id src utils

Exclude directories
    python repo_to_prompt.py -ed venv node_modules build

Include extensions
    python repo_to_prompt.py -ie py go js

Exclude extensions
    python repo_to_prompt.py -ee md txt

Include specific files
    python repo_to_prompt.py -if main.py config.py

Exclude specific files
    python repo_to_prompt.py -ef test.py

Designed for
- LLM prompt preparation
- Codebase archiving
- Offline review of repositories
- Dataset generation
"""

import os
import argparse

try:
    import pyperclip
except ImportError:
    pyperclip = None


DEFAULT_EXCLUDE_DIRS = {
    "venv", ".git", "__pycache__", "node_modules", ".idea", ".vscode", "vevn"
}

DEFAULT_EXTENSIONS = {
    ".py", ".txt", ".md", ".json", ".yaml", ".yml", ".sql", ".go", ".sum", ".mod",".php",".html",
}

LINES_PER_FILE = 1200


def normalize_extensions(ext_list):
    result = set()
    for e in ext_list or []:
        if not e.startswith("."):
            e = "." + e
        result.add(e.lower())
    return result


def is_text_file(path, blocksize=512):
    try:
        with open(path, "rb") as f:
            chunk = f.read(blocksize)
        if b"\0" in chunk:
            return False
        return True
    except Exception:
        return False


def repo_to_prompt(
    root=".",
    include_dirs=None,
    exclude_dirs=None,
    include_files=None,
    exclude_files=None,
    include_ext=None,
    exclude_ext=None,
    copy_clipboard=False,
    only_clipboard=False
):

    repo_name = os.path.basename(os.path.abspath(root))
    part = 1
    line_count = 0

    include_dirs = {os.path.normpath(d) for d in (include_dirs or [])}
    exclude_dirs = set(exclude_dirs or [])

    include_files = set(include_files or [])
    exclude_files = set(exclude_files or [])

    include_ext = normalize_extensions(include_ext)
    exclude_ext = normalize_extensions(exclude_ext)

    if include_ext:
        extensions = include_ext
    else:
        extensions = DEFAULT_EXTENSIONS.copy()

    extensions = {e for e in extensions if e not in exclude_ext}

    clipboard_buffer = []

    def open_new_file(part):
        return open(f"full_code_part_{part:03}.txt", "w", encoding="utf-8")

    def is_under_included_dir(path):
        if not include_dirs:
            return True
        rel = os.path.normpath(os.path.relpath(path, root))
        return any(rel == inc or rel.startswith(inc + os.sep) for inc in include_dirs)

    out = None

    if not only_clipboard:
        out = open_new_file(part)
        header = f"REPOSITORY: {repo_name}\n\n"
        out.write(header)
        clipboard_buffer.append(header)

    else:
        clipboard_buffer.append(f"REPOSITORY: {repo_name}\n\n")

    for dirpath, dirnames, filenames in os.walk(root):

        dirnames.sort()
        filenames.sort()

        rel_dir = os.path.normpath(os.path.relpath(dirpath, root))

        if rel_dir != "." and not is_under_included_dir(dirpath):
            dirnames[:] = []
            continue

        if include_dirs and rel_dir == ".":
            dirnames[:] = [
                d for d in dirnames
                if any(
                    os.path.normpath(d) == inc or inc.startswith(d + os.sep)
                    for inc in include_dirs
                )
            ]

        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]

        for filename in filenames:

            if include_files and filename not in include_files:
                continue

            if filename in exclude_files:
                continue

            ext = os.path.splitext(filename)[1].lower()

            if ext not in extensions:
                continue

            full_path = os.path.join(dirpath, filename)

            if not is_under_included_dir(full_path):
                continue

            if not is_text_file(full_path):
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

            for line in block:
                clipboard_buffer.append(line + "\n")

            if not only_clipboard:

                if line_count + len(block) > LINES_PER_FILE:
                    out.close()
                    part += 1
                    out = open_new_file(part)
                    line_count = 0
                    out.write(f"REPOSITORY: {repo_name} (continued)\n\n")

                for line in block:
                    out.write(line + "\n")
                    line_count += 1

    if out:
        out.close()

    if copy_clipboard or only_clipboard:

        if pyperclip is None:
            raise RuntimeError("Clipboard support requires: pip install pyperclip")

        full_text = "".join(clipboard_buffer)
        pyperclip.copy(full_text)

    if only_clipboard:
        print("Repository copied to clipboard")
    elif copy_clipboard:
        print(f"Repo split into {part} files and copied to clipboard")
    else:
        print(f"Repo split into {part} files")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("--root", default=".")

    parser.add_argument("-id", "--include-dir", nargs="*")
    parser.add_argument("-ed", "--exclude-dir", nargs="*")

    parser.add_argument("-if", "--include-file", nargs="*")
    parser.add_argument("-ef", "--exclude-file", nargs="*")

    parser.add_argument("-ie", "--include-ext", nargs="*")
    parser.add_argument("-ee", "--exclude-ext", nargs="*")

    parser.add_argument("-c", "--clipboard", action="store_true")
    parser.add_argument("-oc", "--only-clipboard", action="store_true")

    args = parser.parse_args()

    final_excludes = DEFAULT_EXCLUDE_DIRS.union(args.exclude_dir or [])

    repo_to_prompt(
        root=args.root,
        include_dirs=args.include_dir,
        exclude_dirs=final_excludes,
        include_files=args.include_file,
        exclude_files=args.exclude_file,
        include_ext=args.include_ext,
        exclude_ext=args.exclude_ext,
        copy_clipboard=args.clipboard,
        only_clipboard=args.only_clipboard
    )
