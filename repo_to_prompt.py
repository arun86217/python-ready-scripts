"""
repo_to_prompt.py

Exports repository source files into structured prompt-ready text.

Adds clipboard functionality.

Features
- Export repo code into segmented text files
- Copy entire export to clipboard
- Optional clipboard-only mode
- Extension filtering
- Include / exclude directory filtering

Usage

Create text files
python repo_to_prompt.py

Create text files + copy to clipboard
python repo_to_prompt.py -c
python repo_to_prompt.py --clipboard

Only copy to clipboard (no text files)
python repo_to_prompt.py -oc
python repo_to_prompt.py --only-clipboard
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

INCLUDE_EXTENSIONS = (
    ".py", ".txt", ".md", ".json", ".yaml", ".yml",
    ".sql", ".go", ".sum", ".mod"
)

LINES_PER_FILE = 1200


def repo_to_prompt(
    root=".",
    include_dirs=None,
    exclude_dirs=None,
    copy_clipboard=False,
    only_clipboard=False
):

    repo_name = os.path.basename(os.path.abspath(root))

    include_dirs = {os.path.normpath(d) for d in (include_dirs or [])}
    exclude_dirs = set(exclude_dirs or [])

    part = 1
    line_count = 0

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
        out.write(f"REPOSITORY: {repo_name}\n\n")

    clipboard_buffer.append(f"REPOSITORY: {repo_name}\n\n")

    for dirpath, dirnames, filenames in os.walk(root):

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

            full_path = os.path.join(dirpath, filename)

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
            raise RuntimeError("pyperclip required. Install using: pip install pyperclip")

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
    parser.add_argument("--include", nargs="*")
    parser.add_argument("--exclude", nargs="*")

    parser.add_argument("-c", "--clipboard", action="store_true")
    parser.add_argument("-oc", "--only-clipboard", action="store_true")

    args = parser.parse_args()

    final_excludes = DEFAULT_EXCLUDE_DIRS.union(args.exclude or [])

    repo_to_prompt(
        root=args.root,
        include_dirs=args.include,
        exclude_dirs=final_excludes,
        copy_clipboard=args.clipboard,
        only_clipboard=args.only_clipboard
    )
