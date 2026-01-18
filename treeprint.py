"""
treeprint.py

Description:
------------
A small utility script to display a directory structure in a tree-like
format using ASCII / Unicode characters. Useful for documentation,
README files, architecture notes, and quick visualization of project
layouts without external tools.

The output can be copied directly into Notepad, Markdown files, or
GitHub READMEs.

Usage:
------
1. Print the current directory structure:
   python treeprint.py

2. Print a specific directory:
   python treeprint.py path/to/directory

3. Redirect output to a file:
   python treeprint.py path/to/directory > structure.txt

Notes:
------
- Uses simple text characters for maximum compatibility.
- Designed for clarity, not filesystem metadata.
- Ideal for developers documenting folder layouts quickly.
"""
import re

INPUT_FILE = "tree.txt"
OUTPUT_FILE = "cmd.txt"

commands = []
stack = []

def strip_tree_chars(line: str) -> str:
    # remove tree drawing characters
    return re.sub(r"[├└│─]", "", line).rstrip()

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    lines = [l.rstrip("\n") for l in f if l.strip()]

# root directory
root = strip_tree_chars(lines[0]).strip().rstrip("/")
commands.append(f"mkdir {root}")
commands.append(f"cd {root}")

for line in lines[1:]:
    # count depth by tree pipes instead of spaces
    depth = line.count("│")
    name = strip_tree_chars(line).strip()

    stack = stack[:depth]

    if name.endswith("/"):
        folder = name.rstrip("/")
        path = "\\".join(stack + [folder])
        commands.append(f"mkdir {path}")
        stack.append(folder)
    else:
        path = "\\".join(stack + [name])
        commands.append(f"type nul > {path}")

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(commands))

