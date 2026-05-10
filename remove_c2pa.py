#!/usr/bin/env python3

"""
Filename:
    remove_c2pa.py

Description:
    Local Python utility to remove:
    - C2PA manifests
    - EXIF metadata
    - XMP metadata
    - PNG text chunks
    - Hidden provenance metadata

    The script rebuilds the image from raw pixel data only,
    ensuring metadata is stripped completely.

Usage:
    python remove_c2pa.py -i input.jpg -o output.jpg

Examples:
    python remove_c2pa.py -i image.jpg -o clean.jpg
    python remove_c2pa.py -i ai_image.png -o cleaned.png

Install:
    pip install pillow

Verify:
    exiftool output.jpg
"""

import argparse
import os
import sys

from PIL import Image
from PIL.PngImagePlugin import PngInfo


SUPPORTED_EXTENSIONS = [
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".bmp",
    ".tiff"
]


def validate_input(path):
    if not os.path.exists(path):
        print(f"[-] File does not exist: {path}")
        sys.exit(1)

    ext = os.path.splitext(path)[1].lower()

    if ext not in SUPPORTED_EXTENSIONS:
        print(f"[-] Unsupported file format: {ext}")
        print(f"[!] Supported formats: {', '.join(SUPPORTED_EXTENSIONS)}")
        sys.exit(1)


def rebuild_image(img):
    """
    Rebuild image from raw pixels only.
    This destroys most embedded metadata including C2PA.
    """

    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGB")

    pixels = list(img.getdata())

    clean_img = Image.new(img.mode, img.size)
    clean_img.putdata(pixels)

    return clean_img


def save_clean_image(clean_img, output_path):
    ext = os.path.splitext(output_path)[1].lower()

    if ext in [".jpg", ".jpeg"]:
        clean_img = clean_img.convert("RGB")

        clean_img.save(
            output_path,
            "JPEG",
            quality=95,
            optimize=True
        )

    elif ext == ".png":
        clean_img.save(
            output_path,
            "PNG",
            pnginfo=PngInfo()
        )

    elif ext == ".webp":
        clean_img.save(
            output_path,
            "WEBP",
            quality=95
        )

    elif ext == ".bmp":
        clean_img.save(
            output_path,
            "BMP"
        )

    elif ext == ".tiff":
        clean_img.save(
            output_path,
            "TIFF"
        )

    else:
        clean_img.save(output_path)


def strip_metadata(input_path, output_path):
    print(f"[+] Loading image: {input_path}")

    img = Image.open(input_path)

    print("[+] Rebuilding image from raw pixel data")

    clean_img = rebuild_image(img)

    print("[+] Saving cleaned image")

    save_clean_image(clean_img, output_path)

    print(f"[+] Done")
    print(f"[+] Clean image saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Remove C2PA and metadata from images"
    )

    parser.add_argument(
        "-i",
        "--input",
        required=True,
        help="Input image path"
    )

    parser.add_argument(
        "-o",
        "--output",
        required=True,
        help="Output image path"
    )

    args = parser.parse_args()

    validate_input(args.input)

    strip_metadata(args.input, args.output)


if __name__ == "__main__":
    main()
