"""
Document parsers for Markdown, Plain Text, and PDF files.
"""
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import yaml

from rag.schemas import Document, DocumentMetadata
from rag.ingestion.preprocessor import DocumentPreprocessor


class MarkdownDocumentParser:
    """
    Parses Markdown documents with optional YAML frontmatter.
    Extracts metadata fields: document_id, title, category, effective_date, department, status, etc.
    """

    @classmethod
    def parse_text(cls, content: str, default_id: str = "DOC-UNKNOWN", file_path: Optional[str] = None) -> Document:
        metadata_dict: Dict[str, Any] = {}
        body = content

        # Check for YAML frontmatter between `---` delimiters
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                frontmatter_raw = parts[1]
                body = parts[2].strip()
                try:
                    parsed_yaml = yaml.safe_load(frontmatter_raw)
                    if isinstance(parsed_yaml, dict):
                        metadata_dict = parsed_yaml
                except Exception:
                    metadata_dict = {}

        # Fallback or extract title if missing
        if "title" not in metadata_dict:
            # Look for first # header
            for line in body.split("\n"):
                if line.startswith("# "):
                    metadata_dict["title"] = line.replace("# ", "").strip()
                    break
            if "title" not in metadata_dict:
                metadata_dict["title"] = default_id

        doc_id = str(metadata_dict.get("document_id", default_id))
        title = str(metadata_dict.get("title", doc_id))
        category = str(metadata_dict.get("category", "General"))
        policy_type = metadata_dict.get("policy_type")
        version = str(metadata_dict.get("version", "1.0"))
        effective_date = metadata_dict.get("effective_date")
        department = metadata_dict.get("department")
        last_reviewed = metadata_dict.get("last_reviewed")
        status = str(metadata_dict.get("status", "Active"))

        # Extra keys
        known_keys = {
            "document_id", "title", "category", "policy_type",
            "version", "effective_date", "department", "last_reviewed", "status"
        }
        extra = {k: v for k, v in metadata_dict.items() if k not in known_keys}

        cleaned_body, stats = DocumentPreprocessor.preprocess(body)
        extra.update(stats)

        metadata = DocumentMetadata(
            document_id=doc_id,
            title=title,
            category=category,
            policy_type=policy_type,
            version=version,
            effective_date=effective_date,
            department=department,
            last_reviewed=last_reviewed,
            status=status,
            extra=extra
        )

        return Document(
            document_id=doc_id,
            metadata=metadata,
            raw_content=cleaned_body,
            source_path=file_path
        )

    @classmethod
    def parse_file(cls, file_path: Union[str, Path]) -> Document:
        path = Path(file_path)
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        default_id = path.stem
        return cls.parse_text(content, default_id=default_id, file_path=str(path))


class PDFDocumentParser:
    """
    Parses PDF documents using pypdf.
    """

    @classmethod
    def parse_file(cls, file_path: Union[str, Path]) -> Document:
        path = Path(file_path)
        default_id = path.stem
        extracted_pages: List[str] = []

        try:
            from pypdf import PdfReader
            reader = PdfReader(str(path))
            for page_idx, page in enumerate(reader.pages):
                text = page.extract_text()
                if text:
                    extracted_pages.append(f"--- Page {page_idx + 1} ---\n" + text)
        except Exception as e:
            extracted_pages.append(f"Error parsing PDF: {str(e)}")

        raw_content = "\n\n".join(extracted_pages)
        cleaned_body, stats = DocumentPreprocessor.preprocess(raw_content)

        metadata = DocumentMetadata(
            document_id=default_id,
            title=default_id.replace("_", " ").title(),
            category="PDF Documents",
            extra=stats
        )

        return Document(
            document_id=default_id,
            metadata=metadata,
            raw_content=cleaned_body,
            source_path=str(path)
        )


class DocumentParser:
    """
    Unified entrypoint that routes file to appropriate parser based on extension.
    """

    @classmethod
    def parse(cls, file_path: Union[str, Path]) -> Document:
        path = Path(file_path)
        ext = path.suffix.lower()
        if ext in [".md", ".markdown"]:
            return MarkdownDocumentParser.parse_file(path)
        elif ext == ".pdf":
            return PDFDocumentParser.parse_file(path)
        elif ext in [".txt", ".rst"]:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            cleaned, stats = DocumentPreprocessor.preprocess(content)
            metadata = DocumentMetadata(
                document_id=path.stem,
                title=path.stem.replace("_", " ").title(),
                category="General",
                extra=stats
            )
            return Document(
                document_id=path.stem,
                metadata=metadata,
                raw_content=cleaned,
                source_path=str(path)
            )
        else:
            raise ValueError(f"Unsupported document file extension: {ext}")

    @classmethod
    def load_directory(cls, dir_path: Union[str, Path], recursive: bool = True) -> List[Document]:
        """
        Loads all supported documents from a directory.
        """
        directory = Path(dir_path)
        if not directory.exists():
            return []

        supported_extensions = {".md", ".markdown", ".txt", ".pdf"}
        pattern = "**/*" if recursive else "*"
        documents: List[Document] = []

        for p in directory.glob(pattern):
            if p.is_file() and p.suffix.lower() in supported_extensions:
                try:
                    doc = cls.parse(p)
                    documents.append(doc)
                except Exception as ex:
                    print(f"Warning: Failed to parse {p}: {ex}")

        return documents
