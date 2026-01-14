"""
tree_one_level.py

A lightweight utility that prints a one-level directory tree for the given path.
It lists only the immediate files and folders, using a visual tree format similar
to the Unix `tree` command, without recursion.

Useful for:
- Quickly inspecting project roots
- Showing folder structure in documentation
- Verifying generated directories

Usage:
    python tree_one_level.py
    python tree_one_level.py   # prints tree of current directory

Example output:
    .
    ├── src/
    ├── tests/
    ├── README.md
    └── setup.py

No external dependencies. Cross-platform.
"""

import os

def print_tree_one_level(path="."):
    items = sorted(os.listdir(path))

    for i, name in enumerate(items):
        full_path = os.path.join(path, name)
        connector = "└──" if i == len(items) - 1 else "├──"

        if os.path.isdir(full_path):
            print(f"{connector} {name}/")
        else:
            print(f"{connector} {name}")

if __name__ == "__main__":
    print(".")
    print_tree_one_level(".")

