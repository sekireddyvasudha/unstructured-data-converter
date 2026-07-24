import os
import re
from typing import List
from .base import BaseParser, DocumentModel, DocumentMetadata, Section, TableData

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False


class HTMLParser(BaseParser):
    SUPPORTED_EXTENSIONS = {'.html', '.htm', '.xhtml'}

    def can_parse(self, file_extension: str) -> bool:
        return file_extension.lower() in self.SUPPORTED_EXTENSIONS

    def parse(self, file_path: str) -> DocumentModel:
        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        filename = os.path.basename(file_path)

        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            raw_html = f.read()

        sections: List[Section] = []
        tables: List[TableData] = []
        unstructured_elements = []

        if BS4_AVAILABLE:
            soup = BeautifulSoup(raw_html, 'html.parser')
            title_tag = soup.find('title')
            doc_title = title_tag.get_text().strip() if title_tag else os.path.splitext(filename)[0].title()

            for element in soup(["script", "style"]):
                element.extract()


            text_content = soup.get_text(separator='\n')
            lines = [line.strip() for line in text_content.splitlines() if line.strip()]
            clean_text = "\n".join(lines)

            # Extract HTML tables
            for idx, table_tag in enumerate(soup.find_all('table')):
                headers = []
                rows = []
                th_tags = table_tag.find_all('th')
                if th_tags:
                    headers = [th.get_text(strip=True) for th in th_tags]

                for tr in table_tag.find_all('tr'):
                    td_tags = tr.find_all('td')
                    if td_tags:
                        row_data = [td.get_text(strip=True) for td in td_tags]
                        if not headers and len(rows) == 0:
                            headers = [f"Col {i+1}" for i in range(len(row_data))]
                        rows.append(row_data)

                if headers or rows:
                    tables.append(TableData(headers=headers, rows=rows, caption=f"Table {idx+1}"))

            heading_tags = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            if heading_tags:
                for heading in heading_tags:
                    level = int(heading.name.lower()[1])
                    h_title = heading.get_text(strip=True)
                    sections.append(Section(title=h_title, level=level, content=""))
            else:
                sections.append(Section(title="Body Content", level=1, content=clean_text))
        else:
            # Simple regex fallback
            title_match = re.search(r'<title>(.*?)</title>', raw_html, re.IGNORECASE)
            doc_title = title_match.group(1).strip() if title_match else os.path.splitext(filename)[0].title()
            clean_text = re.sub(r'<[^>]+>', ' ', raw_html)
            lines = [line.strip() for line in clean_text.splitlines() if line.strip()]
            clean_text = "\n".join(lines)
            sections.append(Section(title="Body Content", level=1, content=clean_text))



        metadata = DocumentMetadata(
            filename=filename,
            file_type="HTML",
            file_size_bytes=file_size,
            char_count=len(clean_text),
            word_count=len(clean_text.split()),
            line_count=len(lines)
        )

        return DocumentModel(
            metadata=metadata,
            title=doc_title,
            sections=sections,
            tables=tables,
            raw_text=clean_text,
            unstructured_elements=unstructured_elements
        )

