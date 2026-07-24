import os
import json
from typing import Tuple
from .base import DocumentModel, Section, TableData

class Exporter:
    @staticmethod
    def render_table_to_markdown(table: TableData) -> str:
        if not table.headers and not table.rows:
            return ""

        headers = table.headers if table.headers else [f"Col {i+1}" for i in range(len(table.rows[0])) if table.rows]
        
        md_lines = []
        if table.caption:
            md_lines.append(f"_{table.caption}_\n")

        # Header row
        md_lines.append("| " + " | ".join(headers) + " |")
        # Separator row
        md_lines.append("| " + " | ".join(["---"] * len(headers)) + " |")

        # Data rows
        for row in table.rows:
            # Pad row if fewer items than headers
            padded_row = row + [""] * (len(headers) - len(row))
            # Escape pipe symbols in cell text
            safe_row = [str(cell).replace('|', '\\|').replace('\n', ' ') for cell in padded_row[:len(headers)]]
            md_lines.append("| " + " | ".join(safe_row) + " |")

        return "\n".join(md_lines)

    @classmethod
    def render_section_to_markdown(cls, section: Section) -> str:
        prefix = "#" * max(1, min(section.level, 6))
        md_parts = [f"{prefix} {section.title}\n"]

        if section.content:
            md_parts.append(f"{section.content}\n")

        for table in section.tables:
            t_md = cls.render_table_to_markdown(table)
            if t_md:
                md_parts.append(f"{t_md}\n")

        for sub in section.subsections:
            md_parts.append(cls.render_section_to_markdown(sub))

        return "\n".join(md_parts)

    @classmethod
    def to_markdown(cls, doc: DocumentModel) -> str:
        md_lines = []

        # Document Header & Metadata Banner
        md_lines.append(f"# {doc.title}\n")
        md_lines.append("> **Document Metadata**")
        md_lines.append(f"> - **Original File:** `{doc.metadata.filename}`")
        md_lines.append(f"> - **Format:** `{doc.metadata.file_type}` ({doc.metadata.file_size_bytes} bytes)")
        md_lines.append(f"> - **Stats:** {doc.metadata.word_count} words | {doc.metadata.line_count} lines | {doc.metadata.char_count} chars")
        md_lines.append(f"> - **Converted At:** {doc.metadata.created_at}\n")
        md_lines.append("---\n")

        # Table of Contents if multiple sections
        if len(doc.sections) > 1:
            md_lines.append("## Table of Contents\n")
            for idx, sec in enumerate(doc.sections, 1):
                anchor = sec.title.lower().replace(' ', '-').replace(':', '')
                md_lines.append(f"{idx}. [{sec.title}](#{anchor})")
            md_lines.append("\n---\n")

        # Global standalone tables if any
        if doc.tables:
            md_lines.append("## Extracted Tables\n")
            for t in doc.tables:
                t_md = cls.render_table_to_markdown(t)
                if t_md:
                    md_lines.append(f"{t_md}\n")

        # Sections
        for sec in doc.sections:
            md_lines.append(cls.render_section_to_markdown(sec))

        return "\n".join(md_lines)

    @classmethod
    def to_json_dict(cls, doc: DocumentModel) -> dict:
        return doc.model_dump()

    @classmethod
    def export(cls, doc: DocumentModel, output_dir: str, base_filename: str = None) -> Tuple[str, str]:
        os.makedirs(output_dir, exist_ok=True)
        if not base_filename:
            base_filename = os.path.splitext(doc.metadata.filename)[0]

        md_path = os.path.join(output_dir, f"{base_filename}.md")
        json_path = os.path.join(output_dir, f"{base_filename}.json")

        # Write Markdown
        md_content = cls.to_markdown(doc)
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_content)

        # Write JSON
        json_dict = cls.to_json_dict(doc)
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_dict, f, indent=2, ensure_ascii=False)

        return md_path, json_path
