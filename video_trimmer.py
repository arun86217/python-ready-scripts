"""
video_clip.py

A command-line utility for cutting precise time ranges from video files using
FFmpeg. Supports fast stream-copy trimming, optional re-encoding, FPS control,
and audio inclusion/exclusion.

The script automatically generates descriptive output filenames based on the
input file and selected time range.

Features:
- Frame-accurate time clipping
- Fast mode (stream copy, no re-encode)
- Re-encode mode with FPS control
- Optional audio removal
- Automatic output naming
- Custom output file or directory support

Requirements:
- FFmpeg installed and available in PATH
- Python 3.8+

Usage:

    Basic fast trim (no re-encode):
        python video_clip.py input.mp4 -st 00:01:00 -et 00:02:30

    Re-encode with FPS change:
        python video_clip.py input.mp4 -st 00:01:00 -et 00:02:30 --fps 24

    Remove audio:
        python video_clip.py input.mp4 -st 00:00:10 -et 00:00:40 -a no

    Custom output file:
        python video_clip.py input.mp4 -st 00:00:03 -et 00:12:04 -o "D:/clips/out.mp4"

    Output to a directory:
        python video_clip.py input.mp4 -st 00:00:03 -et 00:12:04 -o "D:/clips/"

Arguments:
    input             Input video file
    -st, --start-time Start timestamp (HH:MM:SS or HH:MM:SS.ms)
    -et, --end-time   End timestamp (HH:MM:SS or HH:MM:SS.ms)
    --fps             Target FPS (forces re-encode)
    -a, --audio       yes | no (include or remove audio)
    -o, --output      Output file path or directory

Behavior:
- If --fps is omitted, the clip is stream-copied (fastest).
- If --fps is provided, the video is re-encoded using libx264.
- Output defaults to the input file’s directory.

Designed for:
- Highlight extraction
- Dataset generation
- Content trimming
- Automated video workflows
"""
import argparse
import subprocess
import sys
from pathlib import Path


def safe_ts(ts: str) -> str:
    """
    Convert a timestamp from HH:MM:SS(.ms) to a filename-safe format.

    Example:
        00:01:02.500 → 00-01-02.500
    """
    return ts.replace(":", "-")


def run_cmd(cmd: list[str]) -> None:
    """
    Execute an FFmpeg command and terminate the program if FFmpeg fails.

    Args:
        cmd (list[str]): FFmpeg command as a list of arguments.
    """
    print("Running FFmpeg:")
    print(" ".join(cmd))
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print("FFmpeg execution failed.")
        sys.exit(result.returncode)


def main() -> None:
    """
    Cut a time range from a video file using FFmpeg.

    Usage examples:
        python clip.py input.mp4 -st 00:01:00 -et 00:02:30
        python clip.py input.mp4 -st 00:01:00 -et 00:02:30 --fps 24 -a no
        python clip.py input.mp4 -st 00:00:03 -et 00:12:04 -o "D:/clips/out.mp4"

    Notes:
        - If --fps is omitted, the clip is stream-copied (fast, no re-encode).
        - If --fps is provided, the video is re-encoded with libx264.
        - Output defaults to the same directory as the input file.
    """
    parser = argparse.ArgumentParser(
        description="Cut a video clip using system FFmpeg."
    )

    parser.add_argument("input", help="Input video file path")
    parser.add_argument("-st", "--start-time", required=True,
                        help="Start time (HH:MM:SS or HH:MM:SS.ms)")
    parser.add_argument("-et", "--end-time", required=True,
                        help="End time (HH:MM:SS or HH:MM:SS.ms)")
    parser.add_argument("--fps", type=int, default=None,
                        help="Target FPS (forces re-encode)")
    parser.add_argument("-a", "--audio", choices=["yes", "no"],
                        default="yes", help="Include audio stream")
    parser.add_argument("-o", "--output", default=None,
                        help="Custom output file or directory")

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Input file not found: {input_path}")
        sys.exit(1)

    start_tag = safe_ts(args.start_time)
    end_tag = safe_ts(args.end_time)
    default_name = f"{input_path.stem}_{start_tag}_{end_tag}_trimmed{input_path.suffix}"

    if args.output:
        out_path = Path(args.output)
        if out_path.is_dir() or args.output.endswith(("/", "\\")):
            output_path = out_path / default_name
        else:
            output_path = out_path
    else:
        output_path = input_path.parent / default_name

    cmd = [
        "ffmpeg", "-y",
        "-ss", args.start_time,
        "-to", args.end_time,
        "-i", str(input_path),
    ]

    if args.fps:
        cmd += ["-r", str(args.fps)]

    if args.audio == "no":
        cmd += ["-an"]

    if args.fps is None:
        cmd += ["-c", "copy"]
    else:
        cmd += ["-c:v", "libx264", "-preset", "fast", "-crf", "18"]
        if args.audio == "yes":
            cmd += ["-c:a", "aac"]

    cmd.append(str(output_path))

    run_cmd(cmd)
    print(f"Clip created: {output_path}")


if __name__ == "__main__":
    main()


