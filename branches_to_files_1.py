```python
"""
branches_to_files.py — Generate directory and file structures from tree layouts

------------------------------------------------------------
DESCRIPTION
------------------------------------------------------------
branches_to_files converts a tree-style project structure
(text format) into actual directories and files.

It parses common tree characters used in documentation
and automatically creates the corresponding filesystem
structure in the current working directory.

Supported tree symbols:
    │
    ├──
    └──

The script determines hierarchy using indentation and
creates folders and empty files accordingly.

------------------------------------------------------------
USAGE
------------------------------------------------------------

Read structure from a file:

    python branches_to_files.py --file branch.txt

Read structure directly from clipboard:

    python branches_to_files.py --clipboard

------------------------------------------------------------
NOTES
------------------------------------------------------------

- Works on Windows, macOS, and Linux
- Existing files are not overwritten
- File detection is based on presence of '.' in the name
- Connector-only lines like "│" are ignored
- Clipboard support requires pyperclip

Install dependency:

    pip install pyperclip
"""

import os
import argparse
import re
import sys

try:
    import pyperclip
except Exception:
    pyperclip = None


def read_input(file_path=None, clipboard=False):
    """
    Load tree layout from file or clipboard.
    """
    if file_path:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read().splitlines()

    if clipboard:
        if not pyperclip:
            sys.exit("pyperclip required for clipboard usage: pip install pyperclip")
        return pyperclip.paste().splitlines()

    sys.exit("Provide --file or --clipboard")


def clean_name(line):
    """
    Remove tree drawing characters and return the name.
    """
    line = line.rstrip()
    line = re.sub(r"[│├└─]", "", line)
    name = line.strip()
    return name if name else None


def indentation_level(line):
    """
    Determine indentation depth of a tree line.
    """
    prefix = re.match(r"^[\s│]*", line).group()
    spaces = prefix.replace("│", " ")
    return len(spaces) // 4


def create_structure(lines):
    """
    Parse tree lines and create directories/files.
    """
    stack = []

    for raw in lines:

        if not raw.strip():
            continue

        level = indentation_level(raw)
        name = clean_name(raw)

        # Skip connector-only lines like "│"
        if not name:
            continue

        while len(stack) > level:
            stack.pop()

        path = os.path.join(*stack, name) if stack else name

        if "." in name:
            parent = os.path.dirname(path)

            if parent:
                os.makedirs(parent, exist_ok=True)

            if not os.path.exists(path):
                open(path, "w").close()

            print("FILE :", path)

        else:
            os.makedirs(path, exist_ok=True)
            print("DIR  :", path)

        stack.append(name)


def main():
    """
    CLI entry point.
    """
    parser = argparse.ArgumentParser(
        description="Generate directories and files from tree layout"
    )

    parser.add_argument(
        "--file",
        help="Input file containing tree structure",
    )

    parser.add_argument(
        "--clipboard",
        action="store_true",
        help="Read tree structure from clipboard",
    )

    args = parser.parse_args()

    lines = read_input(args.file, args.clipboard)
    create_structure(lines)


if __name__ == "__main__":
    main()
```
