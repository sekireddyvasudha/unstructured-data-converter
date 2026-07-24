import os
from typing import List
from .base import BaseParser, DocumentModel, DocumentMetadata, Section, TableData

class PDFParser(BaseParser):
    SUPPORTED_EXTENSIONS = {'.pdf'}

    def can_parse(self, file_extension: str) -> bool:
        return file_extension.lower() in self.SUPPORTED_EXTENSIONS

    def parse(self, file_path: str) -> DocumentModel:
        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        filename = os.path.basename(file_path)

        sections: List[Section] = []
        tables: List[TableData] = []
        unstructured_elements = []
        raw_text_pages = []
        total_pages = 0

        parsed_with_fitz = False

        # Strategy 1: PyMuPDF (fitz)
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(file_path)
            total_pages = len(doc)

            for page_num in range(total_pages):
                page = doc[page_num]
                page_text = page.get_text()
                raw_text_pages.append(page_text)

                # Section for page
                p_lines = [l.strip() for l in page_text.splitlines() if l.strip()]
                sec_title = f"Page {page_num + 1}"
                if p_lines:
                    # Potential header line
                    possible_h = p_lines[0]
                    if len(possible_h) < 80:
                        sec_title = f"Page {page_num + 1}: {possible_h}"

                sections.append(Section(
                    title=sec_title,
                    level=2,
                    content=page_text.strip(),
                    metadata={"page_number": page_num + 1}
                ))

                unstructured_elements.append({
                    "type": "page",
                    "page_number": page_num + 1,
                    "text": page_text
                })

                # Try table extraction from fitz if available
                try:
                    tabs = page.find_tables()
                    for t_idx, tab in enumerate(tabs):
                        t_data = tab.extract()
                        if t_data and len(t_data) > 0:
                            headers = [str(c) if c is not None else "" for c in t_data[0]]
                            rows = [[str(c) if c is not None else "" for c in r] for r in t_data[1:]]
                            tables.append(TableData(
                                headers=headers,
                                rows=rows,
                                caption=f"Page {page_num + 1} Table {t_idx + 1}"
                            ))
                except Exception:
                    pass

            doc.close()
            parsed_with_fitz = True
        except Exception:
            parsed_with_fitz = False

        # Strategy 2: Fallback to pypdf
        if not parsed_with_fitz:
            try:
                import pypdf
                reader = pypdf.PdfReader(file_path)
                total_pages = len(reader.pages)
                for idx, page in enumerate(reader.pages):
                    txt = page.extract_text() or ""
                    raw_text_pages.append(txt)
                    sections.append(Section(
                        title=f"Page {idx + 1}",
                        level=2,
                        content=txt.strip(),
                        metadata={"page_number": idx + 1}
                    ))
                    unstructured_elements.append({
                        "type": "page",
                        "page_number": idx + 1,
                        "text": txt
                    })
            except Exception as e:
                sections.append(Section(
                    title="Error Parsing PDF",
                    level=1,
                    content=f"Could not extract text from PDF: {str(e)}"
                ))

        full_raw_text = "\n\n".join(raw_text_pages)
        char_count = len(full_raw_text)
        word_count = len(full_raw_text.split())
        line_count = len(full_raw_text.splitlines())

        metadata = DocumentMetadata(
            filename=filename,
            file_type="PDF",
            file_size_bytes=file_size,
            char_count=char_count,
            word_count=word_count,
            line_count=line_count,
            extra={"total_pages": total_pages}
        )

        doc_title = os.path.splitext(filename)[0].replace('_', ' ').replace('-', ' ').title()

        return DocumentModel(
            metadata=metadata,
            title=doc_title,
            sections=sections,
            tables=tables,
            raw_text=full_raw_text,
            unstructured_elements=unstructured_elements
        )
