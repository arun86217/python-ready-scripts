"""
drive_indexer.py

Multiprocessing-based drive scanner and file indexer.

Purpose:
- Scan all available drives (Windows) or root "/" (Linux/macOS)
- Recursively traverse directories using multiprocessing
- Exclude system and heavy folders (Windows, Program Files, venv, node_modules, etc.)
- Save full absolute paths to an index file
- Allow searching indexed paths
- Provide optional move/copy operations on matched results

Designed for:
- Fast filesystem indexing
- Large drive auditing
- Building a lightweight local file search database
- Operational file relocation based on indexed search

Usage:

    # Build index (default output: file_index.txt)
    python drive_indexer.py --scan

    # Build index and save to custom file
    python drive_indexer.py --scan -o my_index.txt

    # Search indexed file
    python drive_indexer.py --search "report"

    # Move matched results
    python drive_indexer.py --search "invoice" --move "D:\\Archive"

    # Copy matched results
    python drive_indexer.py --search "backup" --copy "E:\\Backup"

Arguments:

    --scan              Scan drives and build index
    --search TEXT       Search keyword inside indexed file paths
    --move DEST         Move matched results to destination
    --copy DEST         Copy matched results to destination
    -o, --output FILE   Index output filename (default: file_index.txt)

Notes:
- Uses multiprocessing for top-level drive parallel scanning
- Excludes heavy/system directories
- Safe against permission errors
- Does not follow symlinked directories
"""

import os
import argparse
import multiprocessing as mp
import shutil
import string
import sys

DEFAULT_EXCLUDES = {
    "Windows",
    "Program Files",
    "Program Files (x86)",
    "ProgramData",
    "$Recycle.Bin",
    "System Volume Information",
    "node_modules",
    "venv",
    ".venv",
    "__pycache__",
    ".git",
}


def get_available_drives():
    drives = []
    if os.name == "nt":
        for letter in string.ascii_uppercase:
            drive = f"{letter}:\\"
            if os.path.exists(drive):
                drives.append(drive)
    else:
        drives.append("/")
    return drives


def should_exclude(path):
    parts = set(part.lower() for part in path.split(os.sep))
    for exclude in DEFAULT_EXCLUDES:
        if exclude.lower() in parts:
            return True
    return False


def scan_drive(root):
    collected = []
    for dirpath, dirnames, filenames in os.walk(root, topdown=True):
        if should_exclude(dirpath):
            dirnames[:] = []
            continue

        for d in dirnames:
            full_path = os.path.join(dirpath, d)
            collected.append(full_path)

        for f in filenames:
            full_path = os.path.join(dirpath, f)
            collected.append(full_path)

    return collected


def build_index(output_file):
    drives = get_available_drives()
    with mp.Pool(processes=len(drives)) as pool:
        results = pool.map(scan_drive, drives)

    with open(output_file, "w", encoding="utf-8") as f:
        for drive_result in results:
            for path in drive_result:
                f.write(path + "\n")


def search_index(index_file, keyword):
    matches = []
    if not os.path.exists(index_file):
        print("Index file not found. Run --scan first.")
        sys.exit(1)

    with open(index_file, "r", encoding="utf-8") as f:
        for line in f:
            if keyword.lower() in line.lower():
                matches.append(line.strip())

    return matches


def move_files(paths, destination):
    os.makedirs(destination, exist_ok=True)
    for path in paths:
        if os.path.exists(path):
            try:
                shutil.move(path, destination)
            except Exception:
                pass


def copy_files(paths, destination):
    os.makedirs(destination, exist_ok=True)
    for path in paths:
        if os.path.exists(path):
            try:
                if os.path.isdir(path):
                    shutil.copytree(path, os.path.join(destination, os.path.basename(path)), dirs_exist_ok=True)
                else:
                    shutil.copy2(path, destination)
            except Exception:
                pass


def main():
    parser = argparse.ArgumentParser(description="Multiprocessing Drive Indexer")

    parser.add_argument("--scan", action="store_true", help="Scan drives and build index")
    parser.add_argument("--search", help="Search keyword in indexed paths")
    parser.add_argument("--move", help="Move matched results to destination")
    parser.add_argument("--copy", help="Copy matched results to destination")
    parser.add_argument("-o", "--output", default="file_index.txt", help="Index output file")

    args = parser.parse_args()

    if args.scan:
        print("Scanning drives...")
        build_index(args.output)
        print(f"Index saved to {args.output}")

    if args.search:
        matches = search_index(args.output, args.search)
        print(f"Found {len(matches)} matches")
        for m in matches:
            print(m)

        if args.move:
            move_files(matches, args.move)
            print("Move completed")

        if args.copy:
            copy_files(matches, args.copy)
            print("Copy completed")


if __name__ == "__main__":
    main()
