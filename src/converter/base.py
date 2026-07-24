import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class TableData(BaseModel):
    headers: List[str] = Field(default_factory=list)
    rows: List[List[str]] = Field(default_factory=list)
    caption: Optional[str] = None

class Section(BaseModel):
    title: str = ""
    level: int = 1  # 1 for H1, 2 for H2, etc.
    content: str = ""
    subsections: List['Section'] = Field(default_factory=list)
    tables: List[TableData] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class DocumentMetadata(BaseModel):
    filename: str
    file_type: str
    file_size_bytes: int
    created_at: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    char_count: int = 0
    word_count: int = 0
    line_count: int = 0
    extra: Dict[str, Any] = Field(default_factory=dict)

class DocumentModel(BaseModel):
    metadata: DocumentMetadata
    title: str = "Untitled Document"
    summary: Optional[str] = None
    sections: List[Section] = Field(default_factory=list)
    tables: List[TableData] = Field(default_factory=list)
    raw_text: str = ""
    unstructured_elements: List[Dict[str, Any]] = Field(default_factory=list)

class BaseParser:
    def can_parse(self, file_extension: str) -> bool:
        raise NotImplementedError

    def parse(self, file_path: str) -> DocumentModel:
        raise NotImplementedError
