"""
video_concat_fade.py

A command-line utility for concatenating multiple MP4 video clips into a single
output file, with optional fade-in and fade-out effects applied to each clip.

The script scans a directory for .mp4 files, sorts them alphabetically, builds an
FFmpeg concat list, and merges them into one continuous video. When enabled, a
short fade-in and fade-out effect is applied to each clip for smoother transitions.

Features:
- Automatic detection and sorting of MP4 clips
- Fast, lossless concatenation mode (stream copy)
- Optional fade-in / fade-out effect using FFmpeg filters
- Simple CLI interface

Requirements:
- FFmpeg installed and available in PATH
- Python 3.8+

Usage:

    Basic merge (no re-encoding, fastest):
        python video_concat_fade.py --clips_dir "./clips" --out final.mp4

    Merge with fade-in / fade-out:
        python video_concat_fade.py --clips_dir "./clips" --out final.mp4 --fade

Arguments:
    --clips_dir    Directory containing MP4 clips to concatenate
    --out          Output video file path (default: merged_highlights.mp4)
    --fade         Apply fade-in and fade-out effect to each clip

Behavior:
- Creates a temporary concat.txt file in the clips directory
- Clips are merged in alphabetical order
- Output video is written to the specified path

Designed for:
- Highlight compilation
- Short clip merging
- Automated video pipelines
- Content creation workflows
"""

import os
import argparse


def concat_with_fade(clips_dir: str, output_path: str, apply_fade: bool = False) -> None:
    """
    Concatenate MP4 clips from a directory into a single video, optionally applying
    a short fade-in and fade-out effect to each clip.

    Args:
        clips_dir (str): Directory containing .mp4 clips to concatenate.
        output_path (str): Path to the final merged video file.
        apply_fade (bool): If True, applies fade-in and fade-out to each clip.

    Raises:
        FileNotFoundError: If no MP4 clips are found in the directory.
    """
    concat_file = os.path.join(clips_dir, "concat.txt")
    clips = sorted(c for c in os.listdir(clips_dir) if c.lower().endswith(".mp4"))

    if not clips:
        raise FileNotFoundError("No MP4 clips found in the specified directory.")

    with open(concat_file, "w", encoding="utf-8") as f:
        for clip in clips:
            path = os.path.join(clips_dir, clip).replace(os.sep, "/")
            f.write(f"file '{path}'\n")

    if apply_fade:
        fade_filter = (
            '-filter_complex '
            '"[0:v]split[v0][v1];'
            '[v0]fade=t=in:st=0:d=0.25[v0f];'
            '[v1]reverse,fade=t=in:st=0:d=0.25,reverse[v1f];'
            '[v0f][v1f]concat=n=1:v=1:a=0[v]" '
            '-map "[v]" -c:v libx264 -crf 18 -preset veryfast'
        )
    else:
        fade_filter = "-c copy"

    ffmpeg_cmd = (
        f'ffmpeg -y -f concat -safe 0 -i "{concat_file}" '
        f'{fade_filter} "{output_path}"'
    )

    os.system(ffmpeg_cmd)
    print(f"Output saved to: {output_path}")


def main() -> None:
    """
    CLI entry point.

    Usage:
        python merge.py --clips_dir "D:/clips" --out "final.mp4"
        python merge.py --clips_dir "D:/clips" --out "final.mp4" --fade
    """
    parser = argparse.ArgumentParser(
        description="Concatenate MP4 clips with optional fade-in/fade-out."
    )
    parser.add_argument("--clips_dir", required=True, help="Directory containing MP4 clips")
    parser.add_argument("--out", default="merged_highlights.mp4", help="Output file path")
    parser.add_argument("--fade", action="store_true", help="Apply fade-in/out effect")

    args = parser.parse_args()

    concat_with_fade(
        clips_dir=args.clips_dir,
        output_path=args.out,
        apply_fade=args.fade,
    )


if __name__ == "__main__":
    main()
