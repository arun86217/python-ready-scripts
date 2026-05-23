"""
video_metadata.py

Display detailed metadata about a video file using FFprobe (from FFmpeg).

Features:
- File format
- Video codec
- Audio codec
- Resolution
- Video quality category (480p / 720p / 1080p / 2K / 4K / 8K)
- FPS
- Bitrate
- Duration
- File size
- Aspect ratio
- Pixel format

Requirements:
- FFmpeg installed and available in PATH

Verify:
    ffprobe -version

Usage:
    python video_metadata.py video.mp4
"""

import json
import subprocess
import sys
from pathlib import Path


def run_ffprobe(video_path: Path) -> dict:
    """
    Run ffprobe and return parsed JSON metadata.
    """
    command = [
        "ffprobe",
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        str(video_path),
    ]

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.returncode != 0:
        print("Failed to read video metadata.")
        print(result.stderr)
        sys.exit(1)

    return json.loads(result.stdout)


def calculate_fps(fps_string: str) -> float:
    """
    Convert FFmpeg FPS fraction string into float.

    Example:
        "30000/1001" -> 29.97
    """
    try:
        num, den = fps_string.split("/")
        return round(float(num) / float(den), 2)
    except Exception:
        return 0.0


def bytes_to_mb(size_bytes: int) -> float:
    """
    Convert bytes to MB.
    """
    return round(size_bytes / (1024 * 1024), 2)


def detect_video_quality(width: int, height: int) -> str:
    """
    Detect standard video quality label from resolution.
    """

    max_dim = max(width, height)

    if max_dim >= 7680:
        return "8K"

    if max_dim >= 3840:
        return "4K"

    if max_dim >= 2560:
        return "2K"

    if max_dim >= 1920:
        return "1080p (Full HD)"

    if max_dim >= 1280:
        return "720p (HD)"

    if max_dim >= 854:
        return "480p"

    if max_dim >= 640:
        return "360p"

    return "Low Resolution"


def print_metadata(video_path: Path, metadata: dict) -> None:
    """
    Pretty-print video metadata.
    """
    format_info = metadata.get("format", {})
    streams = metadata.get("streams", [])

    video_stream = next(
        (s for s in streams if s.get("codec_type") == "video"),
        None
    )

    audio_stream = next(
        (s for s in streams if s.get("codec_type") == "audio"),
        None
    )

    print("\n========== VIDEO METADATA ==========\n")

    print(f"File            : {video_path.name}")
    print(f"Path            : {video_path.resolve()}")
    print(f"Format          : {format_info.get('format_name', 'Unknown')}")
    print(f"Duration        : {round(float(format_info.get('duration', 0)), 2)} sec")
    print(f"File Size       : {bytes_to_mb(int(format_info.get('size', 0)))} MB")
    print(f"Overall Bitrate : {format_info.get('bit_rate', 'Unknown')} bps")

    if video_stream:
        width = video_stream.get("width", 0)
        height = video_stream.get("height", 0)

        fps = calculate_fps(video_stream.get("r_frame_rate", "0/1"))

        quality = detect_video_quality(width, height)

        print("\n------ VIDEO ------")
        print(f"Codec           : {video_stream.get('codec_name', 'Unknown')}")
        print(f"Resolution      : {width}x{height}")
        print(f"Quality         : {quality}")
        print(f"FPS             : {fps}")
        print(f"Aspect Ratio    : {round(width / height, 2) if height else 'Unknown'}")
        print(f"Pixel Format    : {video_stream.get('pix_fmt', 'Unknown')}")
        print(f"Video Bitrate   : {video_stream.get('bit_rate', 'Unknown')} bps")

    if audio_stream:
        print("\n------ AUDIO ------")
        print(f"Codec           : {audio_stream.get('codec_name', 'Unknown')}")
        print(f"Channels        : {audio_stream.get('channels', 'Unknown')}")
        print(f"Sample Rate     : {audio_stream.get('sample_rate', 'Unknown')} Hz")
        print(f"Audio Bitrate   : {audio_stream.get('bit_rate', 'Unknown')} bps")

    print("\n====================================\n")


def main() -> None:
    """
    CLI entry point.
    """
    if len(sys.argv) != 2:
        print("Usage:")
        print("    python video_metadata.py <video_file>")
        sys.exit(1)

    video_path = Path(sys.argv[1])

    if not video_path.exists():
        print(f"Video file not found: {video_path}")
        sys.exit(1)

    metadata = run_ffprobe(video_path)
    print_metadata(video_path, metadata)


if __name__ == "__main__":
    main()