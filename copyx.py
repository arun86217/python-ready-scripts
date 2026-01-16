"""
copyx.py — Selective directory copy CLI (rsync-like behavior in pure Python)

------------------------------------------------------------
DESCRIPTION
------------------------------------------------------------
copyx copies files and folders from a source directory to a
destination directory with include / exclude rules.

Behavior:
- If --include is provided:
    → ONLY included paths are copied (whitelist mode)
- If --include is NOT provided:
    → Everything is copied except excluded paths
- --exclude ALWAYS wins over --include

------------------------------------------------------------
USAGE
------------------------------------------------------------
Basic copy:
    python copyx.py money moneyextended

Exclude paths:
    python copyx.py money moneyextended --exclude venv storage haha.txt

Include only specific paths:
    python copyx.py money moneyextended --include src README.md

Include but exclude subpaths:
    python copyx.py money moneyextended --include src --exclude tests

Dry run (no files copied):
    python copyx.py money moneyextended --exclude venv --dry-run

------------------------------------------------------------
NOTES
------------------------------------------------------------
- Cross-platform (Windows / macOS / Linux)
- Does not do delta-sync like rsync
- Designed for scripting, automation, and micro-tools
"""

import shutil
import argparse
from pathlib import Path


def should_copy(rel_parts, includes, excludes):
    """
    Decide whether a path should be copied.

    Rules:
    1. Exclude always wins
    2. If includes are present → whitelist mode
    3. Otherwise copy everything

    Args:
        rel_parts (tuple): Relative path parts (Path.parts)
        includes (set): Included names
        excludes (set): Excluded names

    Returns:
        bool: True if path should be copied
    """
    if any(part in excludes for part in rel_parts):
        return False

    if includes:
        return any(part in includes for part in rel_parts)

    return True


def copy_filtered(src, dst, includes, excludes, dry_run=False):
    """
    Copy files from src to dst based on include/exclude rules.

    Args:
        src (Path): Source directory
        dst (Path): Destination directory
        includes (set): Included path names
        excludes (set): Excluded path names
        dry_run (bool): If True, only print actions
    """
    for path in src.rglob("*"):
        rel = path.relative_to(src)

        if not should_copy(rel.parts, includes, excludes):
            if dry_run:
                print(f"SKIP  {rel}")
            continue

        target = dst / rel

        if dry_run:
            print(f"COPY  {rel}")
            continue

        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)


def main():
    """
    CLI entry point.
    Parses arguments and runs the copy operation.
    """
    parser = argparse.ArgumentParser(
        description="Selective directory copy with include/exclude support"
    )

    parser.add_argument("source", help="Source directory")
    parser.add_argument("destination", help="Destination directory")

    parser.add_argument(
        "--include",
        nargs="*",
        default=[],
        help="Only copy these paths (whitelist mode)"
    )

    parser.add_argument(
        "--exclude",
        nargs="*",
        default=[],
        help="Exclude these paths"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show actions without copying files"
    )

    args = parser.parse_args()

    src = Path(args.source).resolve()
    dst = Path(args.destination).resolve()

    if not src.exists():
        raise SystemExit(f"❌ Source not found: {src}")

    print(f"📂 Source      : {src}")
    print(f"📁 Destination : {dst}")
    print(f"✅ Include     : {args.include or 'ALL'}")
    print(f"🚫 Exclude     : {args.exclude or 'NONE'}")
    print()

    copy_filtered(
        src=src,
        dst=dst,
        includes=set(args.include),
        excludes=set(args.exclude),
        dry_run=args.dry_run,
    )

    if not args.dry_run:
        print("\n✅ Copy completed successfully")


if __name__ == "__main__":
    main()
