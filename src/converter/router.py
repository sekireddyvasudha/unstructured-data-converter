import os
from typing import List, Tuple, Dict, Any, Optional
from .base import BaseParser, DocumentModel
from .text_parser import TextParser
from .html_parser import HTMLParser
from .pdf_parser import PDFParser
from .docx_parser import DOCXParser
from .image_parser import ImageParser
from .exporter import Exporter

class UnstructuredConverter:
    def __init__(self):
        self.parsers: List[BaseParser] = [
            TextParser(),
            HTMLParser(),
            PDFParser(),
            DOCXParser(),
            ImageParser()
        ]

    def get_parser(self, file_path: str) -> Optional[BaseParser]:
        ext = os.path.splitext(file_path)[1].lower()
        for parser in self.parsers:
            if parser.can_parse(ext):
                return parser
        return None

    def convert_file(self, file_path: str, output_dir: str) -> Tuple[str, str, DocumentModel]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Source file not found: {file_path}")

        parser = self.get_parser(file_path)
        if not parser:
            # Fallback to TextParser if unsupported extension
            parser = TextParser()

        doc_model = parser.parse(file_path)
        md_path, json_path = Exporter.export(doc_model, output_dir)
        return md_path, json_path, doc_model

    def convert_batch(self, input_dir: str, output_dir: str, recursive: bool = False) -> List[Dict[str, Any]]:
        results = []
        if not os.path.exists(input_dir):
            raise FileNotFoundError(f"Input directory not found: {input_dir}")

        files_to_process = []
        if recursive:
            for root, _, files in os.walk(input_dir):
                for f in files:
                    files_to_process.append(os.path.join(root, f))
        else:
            for f in os.listdir(input_dir):
                full_p = os.path.join(input_dir, f)
                if os.path.isfile(full_p):
                    files_to_process.append(full_p)

        for f_path in files_to_process:
            try:
                md_path, json_path, doc = self.convert_file(f_path, output_dir)
                results.append({
                    "status": "success",
                    "file": f_path,
                    "filename": doc.metadata.filename,
                    "md_path": md_path,
                    "json_path": json_path,
                    "word_count": doc.metadata.word_count,
                    "char_count": doc.metadata.char_count
                })
            except Exception as e:
                results.append({
                    "status": "error",
                    "file": f_path,
                    "error": str(e)
                })

        return results
