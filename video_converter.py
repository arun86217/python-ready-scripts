"""
video_converter.py

Purpose:
    Convert video files from one format to another using FFmpeg via Python.
    Supports:
        - Single file conversion
        - Batch folder conversion
        - Fast remuxing (no re-encoding)

Requirements:
    - FFmpeg installed and available in system PATH
      Verify with: ffmpeg -version

Usage:

    1. Convert single file (re-encode):
        python video_converter.py single input.mkv output.mp4

    2. Batch convert folder:
        python video_converter.py batch ./videos .mp4

    3. Remux (no re-encoding, fast):
        python video_converter.py remux input.mkv output.mp4

Notes:
    - Re-encoding ensures compatibility but is slower.
    - Remux only works if codecs are already compatible with target container.
"""

import subprocess
import os
import sys


def run_ffmpeg(command):
    """Execute FFmpeg command and handle errors."""
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode != 0:
            print("FFmpeg Error:")
            print(result.stderr)
        else:
            print("Success")

    except FileNotFoundError:
        print("FFmpeg not found. Install FFmpeg and ensure it's in PATH.")


def convert_video(input_file, output_file):
    """
    Convert video with re-encoding (safe, compatible).
    """
    command = [
        "ffmpeg",
        "-i", input_file,
        "-c:v", "libx264",
        "-c:a", "aac",
        "-preset", "fast",
        "-crf", "23",
        output_file
    ]

    print(f"Converting: {input_file} -> {output_file}")
    run_ffmpeg(command)


def remux_video(input_file, output_file):
    """
    Change container without re-encoding (fast).
    """
    command = [
        "ffmpeg",
        "-i", input_file,
        "-c", "copy",
        output_file
    ]

    print(f"Remuxing: {input_file} -> {output_file}")
    run_ffmpeg(command)


def batch_convert(folder, output_ext):
    """
    Convert all supported video files in a folder.
    """
    supported_formats = (".mkv", ".avi", ".mov", ".flv", ".webm")

    for file in os.listdir(folder):
        if file.lower().endswith(supported_formats):
            input_path = os.path.join(folder, file)
            output_name = os.path.splitext(file)[0] + output_ext
            output_path = os.path.join(folder, output_name)

            convert_video(input_path, output_path)


def main():
    if len(sys.argv) < 2:
        print("Invalid usage. Read the file header for instructions.")
        return

    mode = sys.argv[1]

    if mode == "single":
        if len(sys.argv) != 4:
            print("Usage: python video_converter.py single input output")
            return
        convert_video(sys.argv[2], sys.argv[3])

    elif mode == "batch":
        if len(sys.argv) != 4:
            print("Usage: python video_converter.py batch folder output_ext")
            return
        batch_convert(sys.argv[2], sys.argv[3])

    elif mode == "remux":
        if len(sys.argv) != 4:
            print("Usage: python video_converter.py remux input output")
            return
        remux_video(sys.argv[2], sys.argv[3])

    else:
        print("Unknown mode. Use: single | batch | remux")


if __name__ == "__main__":
    main()
