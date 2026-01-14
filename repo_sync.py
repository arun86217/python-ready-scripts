"""
repo_sync.py

A utility script that automatically clones and keeps multiple GitHub repositories
up to date from a predefined list.

The script reads repository URLs from a text file, clones any repositories that
do not yet exist locally, and pulls the latest changes for repositories that are
already present. All actions and errors are logged with timestamps.

Directory structure:
    script_folder/
        repo_sync.py
        git_repo_to_clone.txt
        repo_clone_log.txt
        projects/

Features:
- Bulk clone GitHub repositories from a list
- Auto-update existing repositories using git pull
- Timestamped activity and error logging
- Automatic project folder creation

Input file:
    git_repo_to_clone.txt
        One GitHub repository URL per line.

Output:
    projects/              → cloned repositories
    repo_clone_log.txt     → activity and error log

Usage:
    python repo_sync.py

Setup:
    1. Create a file named "git_repo_to_clone.txt" in the same folder.
    2. Add one repository URL per line, for example:

        https://github.com/pallets/flask.git
        https://github.com/psf/requests.git

    3. Run:
        python repo_sync.py

Designed for:
- Building local mirrors of GitHub projects
- Maintaining research or tooling repositories
- Dataset and codebase collection
- Automated project synchronization

Requirements:
- Git installed and available in PATH
- Python 3.8+
"""

import os
import subprocess
from datetime import datetime

script_dir = os.path.dirname(os.path.abspath(__file__))
projects_folder = os.path.join(script_dir, 'projects')
log_file = os.path.join(script_dir, 'repo_clone_log.txt')

os.makedirs(projects_folder, exist_ok=True)

clone_list_file = os.path.join(script_dir, 'git_repo_to_clone.txt')
try:
    with open(clone_list_file, 'r') as file:
        repo_urls = [line.strip() for line in file if line.strip()]
except FileNotFoundError:
    print(f"Error: File '{clone_list_file}' not found.")
    exit(1)

def write_log(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(log_file, 'a') as log:
        log.write(f"[{timestamp}] {message}\n")

for url in repo_urls:
    repo_name = url.rstrip('/').split('/')[-1].replace('.git', '')
    repo_path = os.path.join(projects_folder, repo_name)

    if os.path.exists(repo_path):
        try:
            print(f"[UPDATE] Pulling updates for {repo_name}...")
            subprocess.run(['git', '-C', repo_path, 'pull'], check=True)
            print(f"[SUCCESS] Updated {repo_name}")
            write_log(f"UPDATED: {repo_name} successfully.")
        except subprocess.CalledProcessError as e:
            print(f"[FAIL] Failed to update {repo_name}: {e}")
            write_log(f"FAILED TO UPDATE: {repo_name} - {e}")
        except Exception as e:
            print(f"[ERROR] Unexpected error updating {repo_name}: {e}")
            write_log(f"ERROR UPDATING: {repo_name} - {e}")
    else:
        try:
            print(f"[CLONE] Cloning {repo_name}...")
            subprocess.run(['git', 'clone', url, repo_path], check=True)
            print(f"[SUCCESS] Cloned {repo_name}")
            write_log(f"CLONED: {repo_name} successfully.")
        except subprocess.CalledProcessError as e:
            print(f"[FAIL] Failed to clone {repo_name}: {e}")
            write_log(f"FAILED TO CLONE: {repo_name} - {e}")
        except Exception as e:
            print(f"[ERROR] Unexpected error cloning {repo_name}: {e}")
            write_log(f"ERROR CLONING: {repo_name} - {e}")
