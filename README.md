# Unstructured File to Markdown & JSON Converter

A python project and web development that ingests unstructured files (PDF, Word DOCX, HTML, TXT, CSV, TSV, Images) and converts them into standardized `.md` (Markdown) and `.json` (Structured JSON AST) files.

---

## Features

- **Multi-Format Ingestion**: Supports `.pdf`, `.docx`, `.doc`, `.html`, `.htm`, `.txt`, `.log`, `.csv`, `.tsv`, `.json`, `.yaml`, `.png`, `.jpg`, `.jpeg`, `.bmp`, `.webp`.
- **Dual Output Format**:
  - Clean **Markdown (`.md`)** with document headers, table of contents, formatted tables, sections, code blocks, and blockquotes.
  - Rich **JSON (`.json`) AST** containing metadata (file size, MIME type, word/line/char stats, timestamp), document structure, sections, table arrays, and element lists.
- **Command Line Interface (CLI)**: Process single files or entire folders recursively with batch execution summaries.
- **Web Application Dashboard**: Interactive web UI built with FastAPI & HTML/CSS/JS featuring drag-and-drop uploads, live Markdown rendering, JSON AST inspector, and one-click downloads.
- **Modular Extensibility**: Pluggable architecture allowing new file parsers to be added easily.

---

## Directory Structure

```text
unstructured_converter/
├── app.py                      # FastAPI Web Application server
├── main.py                     # Command Line Interface (CLI)
├── requirements.txt            # Project dependencies
├── README.md                   # Documentation
├── src/
│   ├── __init__.py
│   └── converter/
│       ├── __init__.py
│       ├── base.py             # Data models & Abstract Base Parser
│       ├── text_parser.py       # TXT, CSV, TSV, JSON, LOG parser
│       ├── html_parser.py       # HTML & Web page parser
│       ├── pdf_parser.py        # PDF parser (PyMuPDF & PyPDF)
│       ├── docx_parser.py       # Word .docx parser
│       ├── image_parser.py      # Image metadata & OCR parser
│       ├── exporter.py          # Markdown & JSON export engine
│       └── router.py            # Main conversion router
├── static/                     # Web UI frontend assets
│   ├── index.html
│   ├── style.css
│   └── app.js
├── samples/                    # Sample unstructured files for testing
│   ├── sample_report.txt
│   ├── sample_webpage.html
│   └── sample_data.csv
├── tests/                      # Unit test suite
│   └── test_converter.py
└── output/                     # Output directory for converted .md & .json files
```

---

## Quickstart Guide

### 1. Installation

Install project dependencies:

```bash
pip install -r requirements.txt
```

### 2. Command Line Interface (CLI)

#### Convert a single file:
```bash
python main.py convert samples/sample_report.txt --output-dir ./output
```

#### Convert an entire folder (batch processing):
```bash
python main.py convert-batch samples/ --output-dir ./output --recursive
```

### 3. Web UI Application

Start the FastAPI development server:

```bash
python app.py
```

Then open your browser and navigate to:
**`http://127.0.0.1:8000`**

- Drag and drop any unstructured file into the upload dropzone.
- View live rendered Markdown preview and inspect the generated JSON AST.
- Download the generated `.md` and `.json` files directly.

---

## Python API Usage

```python
from src.converter import UnstructuredConverter

converter = UnstructuredConverter()

# Convert a single file
md_path, json_path, doc_model = converter.convert_file("samples/sample_webpage.html", output_dir="./output")

print(f"Converted Title: {doc_model.title}")
print(f"Word Count: {doc_model.metadata.word_count}")
print(f"Saved Markdown to: {md_path}")
print(f"Saved JSON AST to: {json_path}")
```

---

## Running Unit Tests

Run the test suite to verify all parsers and export features:

```bash
python -m unittest discover -s tests
```
