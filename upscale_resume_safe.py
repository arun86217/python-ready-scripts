"""
video_upscale_4k.py

A high-performance, resume-safe video upscaling utility built on FFmpeg.
The script splits a video into fixed-length segments, upscales them to 4K
(3840x2160) in parallel using multiprocessing, and concatenates the results
into a final output file.

If the process is interrupted, it can resume automatically by skipping
already completed segments.

Features:
- Automatic video segmentation
- Parallel processing across CPU cores
- Resume support via progress log
- 4K upscaling with Lanczos resampling and sharpening
- Stream-safe concatenation
- Automatic cleanup of temporary files

Requirements:
- FFmpeg and FFprobe installed and available in PATH
- Python 3.8+

Output behavior:
- Temporary files: seg_000.mp4, seg_001.mp4, ...
- Resume file: resume_log.txt
- Final merged output file

Usage:
    python video_upscale_4k.py -i input.mp4 -o output_4k.mp4

Arguments:
    -i, --input     Input video file
    -o, --output    Output upscaled video file

Example:
    python video_upscale_4k.py -i movie.mp4 -o movie_4k.mp4

Designed for:
- Long video upscaling jobs
- Crash-safe batch processing
- High-resolution content preparation
- Automated media pipelines
"""

import os, time, math, glob, subprocess, multiprocessing as mp, argparse
from datetime import timedelta

SEGMENT_DURATION = 120  # seconds
RESUME_FILE = "resume_log.txt"


def run(cmd):
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def get_duration(f):
    r = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            f,
        ],
        capture_output=True,
        text=True,
    )
    return float(r.stdout.strip())


def get_resolution(f):
    r = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height",
            "-of",
            "csv=p=0",
            f,
        ],
        capture_output=True,
        text=True,
    )
    w, h = map(int, r.stdout.strip().split(","))
    return w, h


def upscale_segment(args):
    INPUT, start, dur, idx = args
    out = f"seg_{idx:03d}.mp4"

    if os.path.exists(out):
        return out, 0

    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-ss",
        str(start),
        "-t",
        str(dur),
        "-i",
        INPUT,
        "-vf",
        "scale=3840:2160:flags=lanczos,unsharp=5:5:1.2",
        "-c:v",
        "h264_qsv",
        "-b:v",
        "35M",
        "-maxrate",
        "45M",
        "-bufsize",
        "70M",
        "-pix_fmt",
        "yuv420p",
        "-colorspace",
        "bt709",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-movflags",
        "+faststart",
        out,
    ]

    t0 = time.time()
    run(cmd)
    took = time.time() - t0

    with open(RESUME_FILE, "a") as f:
        f.write(f"{idx}\n")

    return out, took


def concat_segments(files, output):
    with open("concat.txt", "w") as f:
        for s in files:
            f.write(f"file '{os.path.abspath(s)}'\n")

    run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            "concat.txt",
            "-c",
            "copy",
            output,
        ]
    )


def cleanup():
    for f in glob.glob("seg_*.mp4"):
        os.remove(f)
    if os.path.exists("concat.txt"):
        os.remove("concat.txt")
    if os.path.exists(RESUME_FILE):
        os.remove(RESUME_FILE)


def main():
    ap = argparse.ArgumentParser(description="Resume-safe 4K upscaler")
    ap.add_argument("-i", "--input", required=True, help="Input video")
    ap.add_argument("-o", "--output", required=True, help="Output video")
    args = ap.parse_args()

    INPUT = os.path.abspath(args.input)
    OUTPUT = os.path.abspath(args.output)
    NUM_WORKERS = max(1, mp.cpu_count() - 2)

    w, h = get_resolution(INPUT)
    total = get_duration(INPUT)
    nseg = math.ceil(total / SEGMENT_DURATION)

    print(f"Upscaling started: {w}x{h} → 3840x2160")
    print(f"Total segments: {nseg}")

    done = set()
    if os.path.exists(RESUME_FILE):
        with open(RESUME_FILE) as f:
            done = {int(x.strip()) for x in f if x.strip()}
        print(f"Resuming. Skipping {len(done)} finished segments.")

    jobs = [
        (
            INPUT,
            i * SEGMENT_DURATION,
            min(SEGMENT_DURATION, total - i * SEGMENT_DURATION),
            i,
        )
        for i in range(nseg)
        if i not in done
    ]

    start = time.time()
    with mp.Pool(NUM_WORKERS) as p:
        for i, (seg, dur) in enumerate(p.imap_unordered(upscale_segment, jobs), 1):
            print(f"Segment {i}/{len(jobs)} done ({timedelta(seconds=int(dur))})")

    files = sorted(glob.glob("seg_*.mp4"))
    concat_segments(files, OUTPUT)
    cleanup()

    print(f"Finished in {timedelta(seconds=int(time.time()-start))}")
    print("Output:", OUTPUT)


if __name__ == "__main__":
    main()
