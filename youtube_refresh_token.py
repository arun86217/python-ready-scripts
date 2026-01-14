"""
youtube_refresh_token.py

Standalone utility to generate a YouTube Data API refresh token using OAuth 2.0.

The script launches a local browser-based authentication flow and prints a
long-lived refresh token, which can then be stored securely and used by
automation tools such as upload bots, schedulers, and CI pipelines.

This tool is intended to be run once per Google account/project to bootstrap
API-based workflows.

Requirements:
    pip install google-auth-oauthlib

Required environment variables:
    YT_CLIENT_ID
    YT_CLIENT_SECRET

Usage:

    Windows (PowerShell):
        setx YT_CLIENT_ID "your_client_id"
        setx YT_CLIENT_SECRET "your_client_secret"
        python yt_refresh_token.py

    Linux / macOS:
        export YT_CLIENT_ID="your_client_id"
        export YT_CLIENT_SECRET="your_client_secret"
        python yt_refresh_token.py

Output:
    Prints a YouTube API refresh token to the console.

Security notes:
    - Treat the refresh token like a password.
    - Do NOT commit it to GitHub.
    - Store it in a secure .env file or secret manager.

Designed for:
    - YouTube automation pipelines
    - Headless upload systems
    - CI/CD media workflows
    - Content management tools
"""

import json
import os
import sys
from google_auth_oauthlib.flow import InstalledAppFlow


SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def main() -> None:
    client_id = os.getenv("YT_CLIENT_ID")
    client_secret = os.getenv("YT_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("Missing environment variables:")
        print("  YT_CLIENT_ID")
        print("  YT_CLIENT_SECRET")
        sys.exit(1)

    creds_data = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost"]
        }
    }

    temp_json = "yt_oauth_client.json"
    with open(temp_json, "w", encoding="utf-8") as f:
        json.dump(creds_data, f, indent=2)

    try:
        print("Opening browser for Google authentication...")
        flow = InstalledAppFlow.from_client_secrets_file(temp_json, SCOPES)
        creds = flow.run_local_server(port=0)

        print("\nRefresh token:\n")
        print("----------------------------------------")
        print(creds.refresh_token)
        print("----------------------------------------")

    finally:
        if os.path.exists(temp_json):
            os.remove(temp_json)


if __name__ == "__main__":
    main()

