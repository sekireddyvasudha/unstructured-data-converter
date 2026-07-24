import os
from typing import List
from PIL import Image
from .base import BaseParser, DocumentModel, DocumentMetadata, Section, TableData

class ImageParser(BaseParser):
    SUPPORTED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.bmp', '.webp', '.tiff', '.tif'}

    def can_parse(self, file_extension: str) -> bool:
        return file_extension.lower() in self.SUPPORTED_EXTENSIONS

    def parse(self, file_path: str) -> DocumentModel:
        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        filename = os.path.basename(file_path)
        ext = os.path.splitext(filename)[1].lower()

        image_info = {}
        ocr_text = ""

        try:
            with Image.open(file_path) as img:
                width, height = img.size
                format_name = img.format or ext.lstrip('.').upper()
                mode = img.mode
                image_info = {
                    "width": width,
                    "height": height,
                    "format": format_name,
                    "mode": mode
                }

                # OCR Extraction using pytesseract if available
                try:
                    import pytesseract
                    ocr_text = pytesseract.image_to_string(img).strip()
                except Exception:
                    ocr_text = f"[OCR not configured or tesseract binary unavailable. Image metadata: {width}x{height} px, {format_name} format, {mode} mode]"

        except Exception as e:
            ocr_text = f"Failed to inspect image: {str(e)}"

        raw_text = ocr_text or f"Image file: {filename}"
        lines = raw_text.splitlines()

        metadata = DocumentMetadata(
            filename=filename,
            file_type="IMAGE",
            file_size_bytes=file_size,
            char_count=len(raw_text),
            word_count=len(raw_text.split()),
            line_count=len(lines),
            extra=image_info
        )

        sections = [
            Section(
                title=f"Image Overview: {filename}",
                level=1,
                content=f"**Dimensions:** {image_info.get('width', 0)} x {image_info.get('height', 0)} px\n**Format:** {image_info.get('format', 'Unknown')}\n**Mode:** {image_info.get('mode', 'Unknown')}"
            ),
            Section(
                title="Extracted Text / OCR Output",
                level=2,
                content=ocr_text if ocr_text else "No text extracted."
            )
        ]

        return DocumentModel(
            metadata=metadata,
            title=f"Image Document ({filename})",
            sections=sections,
            tables=[],
            raw_text=raw_text,
            unstructured_elements=[{"type": "image", "info": image_info, "ocr_text": ocr_text}]
        )
