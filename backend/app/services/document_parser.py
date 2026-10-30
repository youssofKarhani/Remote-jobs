"""CV Document Parser supporting Plain Text, PDF, and DOCX formats."""

from dataclasses import dataclass, field
import io
import re
import zipfile
import xml.etree.ElementTree as ET
from typing import List, Optional

import docx
from pypdf import PdfReader


class DocumentParsingError(ValueError):
    """Base exception for document parsing failures."""
    pass


class EmptyDocumentError(DocumentParsingError):
    """Raised when an uploaded document contains no extractable text."""
    pass


class UnsupportedFileFormatError(DocumentParsingError):
    """Raised when the document file extension/MIME type is not supported."""
    pass


@dataclass
class ParsedPage:
    """Represents a single extracted document page with raw and cleaned text preserved."""
    page_number: int
    raw_text: str
    cleaned_text: str
    extraction_mode: str = "layout"


@dataclass
class ParsedDocument:
    """Structured document extraction output preserving raw text, cleaned text, and page boundaries."""
    raw_text: str
    cleaned_text: str
    pages: List[ParsedPage] = field(default_factory=list)
    filename: str = ""
    file_extension: str = ""


def reconstruct_broken_urls(text: str) -> str:
    """Reconstruct URLs broken across line breaks or two-column layout spacing."""
    if not text:
        return text

    # 1. Two-column or single-column wrap where /<handle> is on the next line:
    #    e.g. "https://www.linkedin.com/in\n/youssof-el-karhani"
    #    or   "Left Col Text           https://www.linkedin.com/in\nLeft Col Line 2         /youssof-el-karhani"
    def _join_wrapped_path(match: re.Match) -> str:
        base_url = match.group(1).rstrip("/")
        intervening_left_col = match.group(2) or ""
        slug = match.group(3)
        if intervening_left_col.strip():
            return f"{base_url}/{slug}\n{intervening_left_col.rstrip()}"
        return f"{base_url}/{slug}"

    text = re.sub(
        r"(https?://(?:www\.)?(?:linkedin\.com/in|linkedin\.com|github\.com))/?[ \t]*\n([^\n]*?[ \t]{2,})?/([a-zA-Z0-9][\w\-\./]*)",
        _join_wrapped_path,
        text,
        flags=re.I,
    )

    # 2. Wrap where the trailing slash was on line 1 and the slug starts on line 2 without leading slash:
    #    e.g. "https://www.linkedin.com/in/\nyoussof-el-karhani"
    text = re.sub(
        r"(https?://(?:www\.)?(?:linkedin\.com/in|github\.com))/[ \t]*\n[ \t]*([a-zA-Z0-9][\w\-]+)(?=[ \t\n]|$)",
        r"\1/\2",
        text,
        flags=re.I,
    )

    # 3. Wrap mid-handle after a hyphen:
    #    e.g. "https://www.linkedin.com/in/youssof-el-\nkarhani"
    text = re.sub(
        r"(https?://(?:www\.)?(?:linkedin\.com/in|github\.com)/[a-zA-Z0-9][\w\-]*-)[ \t]*\n[ \t]*([a-zA-Z0-9][\w\-]+)",
        r"\1\2",
        text,
        flags=re.I,
    )

    return text


def clean_extracted_cv_text(raw_text: str) -> str:
    """Produce cleaned/interpreted text from raw extraction without mutating candidate claims.

    - Normalizes line endings
    - Reconstructs broken URLs (e.g. wrapped LinkedIn/GitHub URLs)
    - Repairs layout-corrupted intra-word hyphen spacing (e.g. 'scikit   -learn' -> 'scikit-learn')
    - Repairs layout-corrupted spacing before commas/closing parens
    - Never alters candidate spelling claims (e.g. 'MangoDB' remains 'MangoDB')
    """
    if not raw_text:
        return ""

    cleaned = re.sub(r"\r\n|\r", "\n", raw_text)
    cleaned = reconstruct_broken_urls(cleaned)
    # Fix layout intra-word hyphen spacing (2+ spaces before hyphen followed immediately by alphanumeric)
    cleaned = re.sub(r"([A-Za-z0-9])[ \t]{2,}-([A-Za-z0-9])", r"\1-\2", cleaned)
    # Fix layout spacing before commas or closing parentheses
    cleaned = re.sub(r"[ \t]{2,}([,)])", r"\1", cleaned)
    return cleaned


def extract_pdf_pages(file_bytes: bytes) -> List[ParsedPage]:
    """Extract per-page text from PDF binary, attempting layout mode first with safe fallback."""
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        pages: List[ParsedPage] = []
        for page_idx, page in enumerate(reader.pages):
            page_raw: Optional[str] = None
            mode = "layout"
            try:
                page_raw = page.extract_text(extraction_mode="layout")
            except Exception:
                page_raw = None

            if not page_raw or not page_raw.strip():
                mode = "plain_fallback"
                page_raw = page.extract_text() or ""

            cleaned_page = clean_extracted_cv_text(page_raw).strip()
            pages.append(
                ParsedPage(
                    page_number=page_idx + 1,
                    raw_text=page_raw,
                    cleaned_text=cleaned_page,
                    extraction_mode=mode,
                )
            )
        return pages
    except Exception as e:
        raise DocumentParsingError(f"Failed to extract text from PDF: {str(e)}") from e


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF binary using pypdf (layout mode first, preserving page boundaries and raw text)."""
    pages = extract_pdf_pages(file_bytes)
    non_empty_raw = [p.raw_text for p in pages if p.raw_text and p.raw_text.strip()]
    return "\n\f\n".join(non_empty_raw)


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract text from DOCX binary using python-docx with zipfile fallback."""
    try:
        doc = docx.Document(io.BytesIO(file_bytes))
        parts = []
        for p in doc.paragraphs:
            if p.text.strip():
                parts.append(p.text.strip())
        for table in doc.tables:
            for row in table.rows:
                row_texts = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_texts:
                    parts.append(" | ".join(row_texts))
        if parts:
            return "\n\n".join(parts)
    except Exception:
        # Fallback to direct XML parsing of Word OpenXML archive
        pass

    try:
        with zipfile.ZipFile(io.BytesIO(file_bytes)) as zf:
            xml_content = zf.read("word/document.xml")
            tree = ET.fromstring(xml_content)
            # Namespace for Word OpenXML
            ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
            text_nodes = tree.findall(".//w:t", ns)
            text_list = [node.text for node in text_nodes if node.text]
            return " ".join(text_list)
    except Exception as e:
        raise DocumentParsingError(f"Failed to extract text from DOCX: {str(e)}") from e


def extract_text_from_txt(file_bytes: bytes) -> str:
    """Extract text from plain text binary trying common encodings."""
    encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252", "iso-8859-1"]
    for enc in encodings:
        try:
            return file_bytes.decode(enc)
        except UnicodeDecodeError:
            continue
    return file_bytes.decode("utf-8", errors="replace")


def parse_document_detailed(file_bytes: bytes, filename: str) -> ParsedDocument:
    """Parse binary document and return structured ParsedDocument with raw text, cleaned text, and page boundaries."""
    if not file_bytes:
        raise EmptyDocumentError("The uploaded file is empty (0 bytes).")

    ext = filename.lower().split(".")[-1] if "." in filename else ""
    pages: List[ParsedPage] = []

    if ext == "pdf":
        pages = extract_pdf_pages(file_bytes)
        raw_text = "\n\f\n".join(p.raw_text for p in pages if p.raw_text and p.raw_text.strip())
        cleaned_pages = [p.cleaned_text for p in pages if p.cleaned_text]
        cleaned_text = clean_extracted_cv_text("\n\f\n".join(cleaned_pages)).strip()
    elif ext in ("docx", "doc"):
        raw_text = extract_text_from_docx(file_bytes)
        cleaned_text = clean_extracted_cv_text(raw_text).strip()
        pages = [
            ParsedPage(
                page_number=1,
                raw_text=raw_text,
                cleaned_text=cleaned_text,
                extraction_mode="docx",
            )
        ]
    elif ext in ("txt", "md", "text", "rtf", ""):
        raw_text = extract_text_from_txt(file_bytes)
        cleaned_text = clean_extracted_cv_text(raw_text).strip()
        pages = [
            ParsedPage(
                page_number=1,
                raw_text=raw_text,
                cleaned_text=cleaned_text,
                extraction_mode="txt",
            )
        ]
    else:
        try:
            raw_text = extract_text_from_txt(file_bytes)
            cleaned_text = clean_extracted_cv_text(raw_text).strip()
            pages = [
                ParsedPage(
                    page_number=1,
                    raw_text=raw_text,
                    cleaned_text=cleaned_text,
                    extraction_mode="txt_fallback",
                )
            ]
        except Exception:
            raise UnsupportedFileFormatError(
                f"Unsupported file format '.{ext}'. Please upload a PDF, DOCX, or TXT resume."
            )

    if not cleaned_text or len(cleaned_text.strip()) < 10:
        raise EmptyDocumentError(
            "The document contains no readable text or is a scanned image. "
            "Please provide a text-based PDF, DOCX, or paste plain text directly."
        )

    return ParsedDocument(
        raw_text=raw_text,
        cleaned_text=cleaned_text,
        pages=pages,
        filename=filename,
        file_extension=ext,
    )


def parse_document(file_bytes: bytes, filename: str) -> str:
    """Parse binary document and return raw extracted text string (preserving page boundaries and raw source claims).

    Supports .pdf, .docx, .doc, .txt, .md.
    Raises EmptyDocumentError if no readable text is found.
    Raises UnsupportedFileFormatError if extension is unsupported.
    """
    parsed = parse_document_detailed(file_bytes, filename)
    return re.sub(r"\r\n|\r", "\n", parsed.raw_text).strip()


def extract_spatial_pdf(file_bytes: bytes, filename: str = "document.pdf"):
    """Extract coordinate-aware spatial document representation from PDF binary."""
    from app.services.spatial_parser import extract_spatial_document
    return extract_spatial_document(file_bytes, filename)


def reconstruct_layout_pdf(file_bytes: bytes, filename: str = "document.pdf"):
    """Extract spatial document and reconstruct logical layout, columns, and reading order."""
    from app.services.spatial_parser import extract_spatial_document
    from app.services.layout import reconstruct_reading_order
    spatial_doc = extract_spatial_document(file_bytes, filename)
    return reconstruct_reading_order(spatial_doc)


