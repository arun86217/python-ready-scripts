"""
pngs_to_video.py

A command-line utility that converts a folder of PNG images into an MP4 video
using FFmpeg. The script automatically sorts frames numerically, renames them
into a sequential order, and encodes them into a video file.

It attempts to use Intel Quick Sync Video (h264_qsv) for hardware-accelerated
encoding first, and automatically falls back to CPU encoding (libx264) if QSV
is unavailable or fails.

Features:
- Numeric (natural) frame sorting
- Automatic temporary workspace handling
- Hardware-accelerated encoding (Intel QSV) with safe fallback
- Fixed FPS output
- Clean MP4 (yuv420p) compatibility format

Requirements:
- FFmpeg installed and available in PATH
- Python 3.8+

Usage:

    Basic:
        python pngs_to_video.py ./frames

    Custom output file:
        python pngs_to_video.py ./frames final.mp4

Behavior:
- Reads all *.png files from the given folder
- Sorts frames numerically (e.g., frame2.png < frame10.png)
- Builds a temporary sequential frame set
- Encodes at fixed FPS (default: 30)
- Outputs an MP4 file

Arguments:
    png_folder     Folder containing PNG frames
    output.mp4     Optional output file (default: output.mp4)

Designed for:
- Frame sequence rendering
- AI image/video generation pipelines
- Simulation output rendering
- Timelapse and animation building
- Automated media workflows
"""

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

FPS = 30
OUTPUT_NAME = "output.mp4"


def natural_key(path: Path):
    """
    Extract a numeric sort key from a filename for natural ordering.

    Example:
        frame2.png, frame10.png → 2, 10
    """
    numbers = re.findall(r"\d+", path.stem)
    return int(numbers[0]) if numbers else path.stem


def run_ffmpeg(temp_dir: Path, output_path: str, encoder: str) -> None:
    """
    Run FFmpeg to encode sequential PNG frames into a video.

    Args:
        temp_dir (Path): Directory containing sequentially named PNG frames.
        output_path (str): Output video path.
        encoder (str): FFmpeg video encoder (e.g., h264_qsv, libx264).

    Raises:
        subprocess.CalledProcessError: If FFmpeg fails.
    """
    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(FPS),
        "-i", str(temp_dir / "%04d.png"),
        "-c:v", encoder,
        "-pix_fmt", "yuv420p",
        output_path,
    ]
    print("Running FFmpeg:")
    print(" ".join(cmd))
    subprocess.run(cmd, check=True)


def pngs_to_video(png_dir: str, output_path: str) -> None:
    """
    Convert a directory of PNG images into a video file.

    The function attempts Intel QSV encoding first and automatically
    falls back to CPU (libx264) if QSV is unavailable.

    Args:
        png_dir (str): Directory containing PNG files.
        output_path (str): Output video file path.

    Raises:
        FileNotFoundError: If the directory does not exist.
        RuntimeError: If no PNG files are found.
    """
    png_dir = Path(png_dir)

    if not png_dir.exists():
        raise FileNotFoundError(png_dir)

    pngs = sorted(png_dir.glob("*.png"), key=natural_key)
    if not pngs:
        raise RuntimeError("No PNG files found in the specified directory.")

    temp_dir = Path(tempfile.mkdtemp(prefix="frames_"))

    try:
        for i, src in enumerate(pngs, start=1):
            shutil.copy(src, temp_dir / f"{i:04d}.png")

        try:
            print("Trying Intel QSV...")
            run_ffmpeg(temp_dir, output_path, "h264_qsv")
        except subprocess.CalledProcessError:
            print("QSV failed. Falling back to libx264.")
            run_ffmpeg(temp_dir, output_path, "libx264")

        print(f"Video created: {output_path}")

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def main() -> None:
    """
    CLI entry point.

    Usage:
        python pngs_to_video.py <png_folder>
        python pngs_to_video.py <png_folder> output.mp4

    Notes:
        - Frames are sorted numerically based on digits in filenames.
        - Default FPS is 30.
        - Output defaults to 'output.mp4' in the current directory.
    """
    if len(sys.argv) < 2:
        print("Usage: python pngs_to_video.py <png_folder> [output.mp4]")
        sys.exit(1)

    folder = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else OUTPUT_NAME

    pngs_to_video(folder, output)


if __name__ == "__main__":
    main()

