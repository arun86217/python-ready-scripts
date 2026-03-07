"""
pdf_to_text.py

Extracts text content from PDF files and exports it into structured, prompt-ready
text files. The script can process a single PDF or scan a directory and convert
multiple PDFs.

Features:
- Extract text from one or many PDF files
- Recursive directory scanning
- Automatic splitting into multiple output files by line count
- Preserves page boundaries for clarity
- Handles large PDFs safely

Output:
    extracted_text_part_001.txt
    extracted_text_part_002.txt
    ...

Dependencies:
    pip install pypdf

Usage:
    python pdf_to_text.py --input document.pdf
    python pdf_to_text.py --input ./pdf_folder
    python pdf_to_text.py --input ./pdf_folder --max-lines 3000
    python pdf_to_text.py --input report.pdf --output-dir output_text

Arguments:
    --input        PDF file or directory containing PDFs
    --output-dir   Output directory for text files (default: ./pdf_text_output)
    --max-lines    Maximum lines per output file (default: 4000)

Designed for:
- LLM prompt preparation
- Document archiving
- Dataset generation
- Offline text analysis
"""

import argparse
from pathlib import Path
from pypdf import PdfReader


def extract_pdf_text(pdf_path: Path):
    reader = PdfReader(str(pdf_path))
    content = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        header = f"\n\n===== FILE: {pdf_path.name} | PAGE {page_number} =====\n\n"
        content.append(header + text)

    return "\n".join(content)


def split_and_write(text, output_dir: Path, max_lines: int):
    lines = text.splitlines()
    total = len(lines)

    part = 1
    index = 0

    while index < total:
        chunk = lines[index:index + max_lines]

        file_path = output_dir / f"extracted_text_part_{part:03d}.txt"

        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(chunk))

        part += 1
        index += max_lines


def process_input(input_path: Path):
    if input_path.is_file() and input_path.suffix.lower() == ".pdf":
        return [input_path]

    pdf_files = []
    for p in input_path.rglob("*.pdf"):
        pdf_files.append(p)

    return pdf_files


def main():
    parser = argparse.ArgumentParser(description="Extract text from PDFs into structured text files.")

    parser.add_argument("--input", required=True, help="PDF file or directory containing PDFs")
    parser.add_argument("--output-dir", default="pdf_text_output", help="Output directory")
    parser.add_argument("--max-lines", type=int, default=4000, help="Max lines per output file")

    args = parser.parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    pdf_files = process_input(input_path)

    all_text = []

    for pdf in pdf_files:
        print(f"Processing {pdf}")
        extracted = extract_pdf_text(pdf)
        all_text.append(extracted)

    combined_text = "\n".join(all_text)

    split_and_write(combined_text, output_dir, args.max_lines)

    print("Extraction completed.")


if __name__ == "__main__":
    main()