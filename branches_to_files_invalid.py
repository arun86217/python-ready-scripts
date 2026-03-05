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

Typical use case:
- Convert architecture notes into project scaffolding
- Quickly generate repositories from documentation
- Materialize AI-generated project structures

------------------------------------------------------------
USAGE
------------------------------------------------------------

Read structure from a file:

    python branches_to_files.py --file branch.txt

Read structure directly from clipboard:

    python branches_to_files.py --clipboard

------------------------------------------------------------
INPUT FORMAT
------------------------------------------------------------

Example tree layout:

cricket-volatility-trader
│
├── README.md
├── requirements.txt
├── config.py
├── run_strategy.py
│
├── strategy
│   ├── __init__.py
│   ├── market_decoder.py
│   ├── match_state.py
│   ├── probability_model.py
│   ├── edge_detector.py
│   └── bankroll.py
│
├── signals
│   ├── __init__.py
│   └── signal_engine.py
│
└── utils
    ├── __init__.py
    └── logger.py

------------------------------------------------------------
OUTPUT
------------------------------------------------------------

The script generates the corresponding filesystem:

./cricket-volatility-trader/
    README.md
    requirements.txt
    config.py
    run_strategy.py
    strategy/
        __init__.py
        market_decoder.py
        match_state.py
        probability_model.py
        edge_detector.py
        bankroll.py
    signals/
        __init__.py
        signal_engine.py
    utils/
        __init__.py
        logger.py

All files are created as empty placeholders.

------------------------------------------------------------
NOTES
------------------------------------------------------------

- Works on Windows, macOS, and Linux
- Existing files are not overwritten
- File detection is based on presence of '.' in the name
- Clipboard support requires pyperclip

Install dependency:

    pip install pyperclip

------------------------------------------------------------
ARCHITECTURE
------------------------------------------------------------

read_input()
    Loads tree structure from file or clipboard.

clean_name()
    Removes tree drawing characters and extracts the
    actual file or directory name.

indentation_level()
    Determines hierarchy level from indentation.

create_structure()
    Builds directories and files using a stack-based
    path tracker.

main()
    CLI entry point that parses arguments and executes
    structure generation.

------------------------------------------------------------
DESIGN
------------------------------------------------------------

Hierarchy detection uses indentation depth.

Example:

level 0 → project root
level 1 → direct children
level 2 → nested children

A stack maintains the current directory path.

Algorithm outline:

1. Read lines
2. Determine indentation level
3. Adjust stack depth
4. Construct path
5. Create directory or file

------------------------------------------------------------
"""

import os
import argparse
import re
import sys

try:
    import pyperclip
except:
    pyperclip = None


def read_input(file_path=None, clipboard=False):
    if file_path:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read().splitlines()

    if clipboard:
        if not pyperclip:
            sys.exit("Install pyperclip: pip install pyperclip")
        return pyperclip.paste().splitlines()

    sys.exit("Provide --file or --clipboard")


def clean_name(line):
    line = line.rstrip()

    # remove tree drawing chars
    line = re.sub(r"[│├└─]", "", line)

    # normalize spaces
    return line.strip()


def indentation_level(line):
    prefix = re.match(r"^[\s│]*", line).group()
    spaces = prefix.replace("│", " ")
    return len(spaces) // 4


def create_structure(lines):
    stack = []

    for raw in lines:
        if not raw.strip():
            continue

        level = indentation_level(raw)
        name = clean_name(raw)

        while len(stack) > level:
            stack.pop()

        path = os.path.join(*stack, name) if stack else name

        if "." in name:
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
            if not os.path.exists(path):
                open(path, "w").close()
            print("FILE :", path)
        else:
            os.makedirs(path, exist_ok=True)
            print("DIR  :", path)

        stack.append(name)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", help="Input file containing tree")
    parser.add_argument("--clipboard", action="store_true")
    args = parser.parse_args()

    lines = read_input(args.file, args.clipboard)
    create_structure(lines)


if __name__ == "__main__":
    main()
