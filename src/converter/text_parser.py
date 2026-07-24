import os
import csv
import json
import io
from typing import List
from .base import BaseParser, DocumentModel, DocumentMetadata, Section, TableData

class TextParser(BaseParser):
    SUPPORTED_EXTENSIONS = {'.txt', '.log', '.csv', '.tsv', '.json', '.yaml', '.yml', '.md', '.rtf'}

    def can_parse(self, file_extension: str) -> bool:
        return file_extension.lower() in self.SUPPORTED_EXTENSIONS

    def parse(self, file_path: str) -> DocumentModel:
        ext = os.path.splitext(file_path)[1].lower()
        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        filename = os.path.basename(file_path)

        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

        lines = content.splitlines()
        char_count = len(content)
        word_count = len(content.split())
        line_count = len(lines)

        metadata = DocumentMetadata(
            filename=filename,
            file_type=ext.lstrip('.').upper(),
            file_size_bytes=file_size,
            char_count=char_count,
            word_count=word_count,
            line_count=line_count
        )

        sections: List[Section] = []
        tables: List[TableData] = []
        unstructured_elements = []

        if ext in ('.csv', '.tsv'):
            delimiter = ',' if ext == '.csv' else '\t'
            reader = csv.reader(io.StringIO(content), delimiter=delimiter)
            rows = [row for row in reader if row]
            if rows:
                headers = rows[0]
                data_rows = rows[1:] if len(rows) > 1 else []
                table = TableData(headers=headers, rows=data_rows, caption=f"Table extracted from {filename}")
                tables.append(table)
                sections.append(Section(
                    title=f"Data Table ({filename})",
                    level=1,
                    content=f"Extracted {len(data_rows)} rows and {len(headers)} columns.",
                    tables=[table]
                ))

        elif ext in ('.json', '.yaml', '.yml'):
            try:
                parsed_obj = json.loads(content) if ext == '.json' else content
                formatted = json.dumps(parsed_obj, indent=2) if isinstance(parsed_obj, (dict, list)) else str(content)
                sections.append(Section(
                    title=f"Structured Content ({ext.upper()})",
                    level=1,
                    content=f"```json\n{formatted}\n```"
                ))
            except Exception:
                sections.append(Section(
                    title="Content",
                    level=1,
                    content=content
                ))

        else:  # TXT, LOG, MD, RTF
            # Split into heading sections if lines start with #, or split by double newline
            current_section = Section(title="Main Content", level=1, content="")
            curr_lines = []

            for line in lines:
                stripped = line.strip()
                if stripped.startswith('#') and ' ' in stripped:
                    # Heading line
                    if curr_lines:
                        current_section.content = "\n".join(curr_lines)
                        sections.append(current_section)
                        curr_lines = []
                    
                    level = len(stripped.split(' ')[0])
                    title = stripped.lstrip('#').strip()
                    current_section = Section(title=title, level=min(level, 6), content="")
                else:
                    curr_lines.append(line)
                    unstructured_elements.append({"type": "paragraph", "text": line})

            if curr_lines:
                current_section.content = "\n".join(curr_lines)
                sections.append(current_section)

        if not sections:
            sections.append(Section(title="Content", level=1, content=content))

        return DocumentModel(
            metadata=metadata,
            title=os.path.splitext(filename)[0].replace('_', ' ').replace('-', ' ').title(),
            sections=sections,
            tables=tables,
            raw_text=content,
            unstructured_elements=unstructured_elements
        )
