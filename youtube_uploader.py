"""
youtube_uploader.py

A command-line YouTube upload utility built on the Google YouTube Data API v3.
Supports silent OAuth authentication using a refresh token, resumable uploads,
progress reporting, optional thumbnail upload, and batch uploads from a folder.

The script is designed for automation workflows where manual browser-based
authentication is not desired after initial token setup.

Features:
- Silent OAuth authentication via refresh token
- Resumable video uploads
- Upload progress reporting
- Optional thumbnail upload
- Tag and privacy configuration
- Batch folder upload mode
- Environment-based configuration

Environment variables required (.env supported):
    YT_CLIENT_ID
    YT_CLIENT_SECRET
    YT_REFRESH_TOKEN

Optional environment variables:
    YT_DEFAULT_DESCRIPTION
    YT_DEFAULT_TAGS
    YT_DEFAULT_PRIVACY   (public | unlisted | private)

Usage:

    Upload a single video:
        python youtube_uploader.py --file video.mp4 \
            --title "My Video Title" \
            --description "My description" \
            --tags "gaming,highlights,fun" \
            --privacy unlisted \
            --thumbnail thumb.jpg

    Batch upload all .mp4 videos in a folder:
        python youtube_uploader.py --batch-folder ./videos --privacy public

Arguments:
    --file            Path to a single video file to upload
    --batch-folder   Upload all .mp4 files inside a folder
    --title           Video title (single mode)
    --description     Video description
    --tags            Comma-separated tags
    --privacy         public | unlisted | private
    --thumbnail       Path to thumbnail image

Output:
- Prints live upload progress
- Prints final YouTube video URL on success

Designed for:
- Automated content pipelines
- Batch channel management
- Game highlight uploads
- Media automation workflows

Requirements:
- Python 3.9+
- google-api-python-client
- google-auth
- python-dotenv
"""

import os
import argparse
from pathlib import Path
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from typing import Iterable, List, Optional

import sys

from dotenv import load_dotenv


def load_env(dotenv_path: Optional[Path] = None) -> None:
    """
    Load environment variables (.env if present).
    """
    if dotenv_path:
        load_dotenv(dotenv_path)
    else:
        load_dotenv()


def log_info(msg: str) -> None:
    print(msg)


def log_err(msg: str) -> None:
    sys.stderr.write(msg + "\n")


SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def get_authenticated_service():
    """Authenticate silently using stored refresh token"""
    load_dotenv()
    creds = Credentials(
        None,
        refresh_token=os.getenv("YT_REFRESH_TOKEN"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("YT_CLIENT_ID"),
        client_secret=os.getenv("YT_CLIENT_SECRET"),
        scopes=SCOPES,
    )

    if not creds or not creds.valid:
        try:
            creds.refresh(Request())
        except Exception as e:
            log_err(f"❌ Failed to refresh credentials: {e}")
            return None

    return build("youtube", "v3", credentials=creds)


def upload_to_youtube(
    file_path: Path,
    title: str,
    description: str,
    thumbnail_path: Path = None,
    tags: str = "",
    privacy: str = None,
):
    """
    Uploads a single video to YouTube using refresh token flow.
    """
    file_path = Path(file_path).resolve()
    if not file_path.exists():
        log_err(f"❌ Video file not found: {file_path}")
        return None

    youtube = get_authenticated_service()
    if not youtube:
        log_err("❌ Could not authenticate YouTube API.")
        return None

    privacy = privacy or os.getenv("YT_DEFAULT_PRIVACY", "unlisted")
    tags_list = [
        t.strip()
        for t in (tags or os.getenv("YT_DEFAULT_TAGS", "")).split(",")
        if t.strip()
    ]

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags_list,
            "categoryId": "20",  # Gaming
        },
        "status": {"privacyStatus": privacy},
    }

    media = MediaFileUpload(str(file_path), chunksize=-1, resumable=True)

    log_info(f"🎬 Uploading: {file_path.name} ...")
    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media,
    )

    response = None
    try:
        while response is None:
            status, response = request.next_chunk()
            if status:
                log_info(f"📤 Upload progress: {int(status.progress() * 100)}%")
        video_id = response.get("id")
        video_url = f"https://youtu.be/{video_id}"
        log_info(f"✅ Upload complete → {video_url}")

        if thumbnail_path and Path(thumbnail_path).exists():
            youtube.thumbnails().set(
                videoId=video_id, media_body=MediaFileUpload(str(thumbnail_path))
            ).execute()
            log_info("🖼️ Thumbnail applied successfully.")

        return video_url
    except Exception as e:
        log_err(f"❌ Upload failed: {e}")
        return None


if __name__ == "__main__":
    load_env()
    parser = argparse.ArgumentParser(description="Manual YouTube uploader")

    parser.add_argument("--file", type=str, help="Path to video file to upload")
    parser.add_argument("--title", type=str, help="Video title")
    parser.add_argument("--description", type=str, help="Video description")
    parser.add_argument("--tags", type=str, help="Comma-separated video tags")
    parser.add_argument(
        "--privacy",
        type=str,
        choices=["public", "unlisted", "private"],
        default="unlisted",
    )
    parser.add_argument("--thumbnail", type=str, help="Path to thumbnail image")
    parser.add_argument("--batch-folder", type=str, help="Upload all videos in folder")

    args = parser.parse_args()

    if args.file:
        upload_to_youtube(
            file_path=args.file,
            title=args.title or f"Game Highlights – {Path(args.file).stem}",
            description=args.description
            or os.getenv("YT_DEFAULT_DESCRIPTION", "Automated highlight upload"),
            thumbnail_path=args.thumbnail,
            tags=args.tags,
            privacy=args.privacy,
        )

    elif args.batch_folder:
        folder = Path(args.batch_folder).resolve()
        if not folder.exists():
            log_err(f"⚠️ Folder not found: {folder}")
        for video in folder.glob("*.mp4"):
            upload_to_youtube(
                file_path=video,
                title=f"Game Highlights – {video.stem}",
                description=os.getenv("YT_DEFAULT_DESCRIPTION", "Auto batch upload"),
                thumbnail_path=args.thumbnail,
                tags=args.tags,
                privacy=args.privacy,
            )

    else:
        log_err("⚠️ Please provide either --file or --batch-folder.")
