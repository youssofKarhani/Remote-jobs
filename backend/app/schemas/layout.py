"""Layout Reconstruction and Reading Order Schemas.

Defines Pydantic models for column layouts, heading candidates,
source blocks with stable identifiers and provenance, and reconstructed layout documents.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.schemas.spatial import BoundingBox


class HeadingCandidate(BaseModel):
    """Detected candidate section heading with confidence and typography signals."""

    text: str = Field(description="Normalized heading text")
    raw_text: str = Field(description="Raw heading text")
    page: int = Field(description="1-based page number")
    bbox: BoundingBox = Field(description="Bounding box enclosing heading")
    confidence: float = Field(default=1.0, description="Detection confidence score between 0.0 and 1.0")
    heading_level: int = Field(default=1, description="1 for primary section heading, 2 for subsection")
    font_size: Optional[float] = Field(default=None, description="Dominant font size in points")
    is_bold: bool = Field(default=False, description="True if font is bold")
    source_line_ids: List[str] = Field(default_factory=list, description="IDs of lines comprising this heading")
    detection_reasons: List[str] = Field(default_factory=list, description="Heuristic signals that triggered detection")


class ColumnLayout(BaseModel):
    """Geometric column structure detected on a single page."""

    page_number: int = Field(description="1-based page number")
    layout_type: str = Field(
        default="single_column",
        description="Layout classification: 'single_column', 'two_column', 'left_sidebar', 'right_sidebar', 'multi_column'"
    )
    num_columns: int = Field(default=1, description="Number of distinct vertical content columns")
    columns: List[BoundingBox] = Field(default_factory=list, description="Bounding boxes of detected columns")
    gutters: List[BoundingBox] = Field(default_factory=list, description="Empty vertical gutters between columns")
    has_header_band: bool = Field(default=False, description="True if a full-width header band exists at top")
    header_boundary_y: Optional[float] = Field(default=None, description="Bottom y-coordinate of header band")
    has_footer_band: bool = Field(default=False, description="True if a full-width footer band exists at bottom")
    footer_boundary_y: Optional[float] = Field(default=None, description="Top y-coordinate of footer band")


class SourceBlock(BaseModel):
    """Stable, traceable source block of CV content with strict provenance."""

    id: str = Field(description="Stable sequential identifier, e.g. BLOCK_001, BLOCK_012")
    page: int = Field(description="1-based page number")
    column: int = Field(default=0, description="0-indexed column assignment")
    region_type: str = Field(
        default="body",
        description="Region type: 'header', 'left_sidebar', 'right_sidebar', 'main_body', 'column_0', 'column_1', 'footer', etc."
    )
    bbox: BoundingBox = Field(description="Spatial bounding box enclosing this block")
    text: str = Field(description="Clean reconstructed text content")
    raw_text: str = Field(description="Original unedited text content")
    reading_order: int = Field(description="1-based document reading sequence index")
    is_heading: bool = Field(default=False, description="True if this block represents a section heading")
    heading_level: Optional[int] = Field(default=None, description="Heading level (1 or 2) if is_heading is True")
    font_size: Optional[float] = Field(default=None, description="Predominant font size")
    is_bold: bool = Field(default=False, description="True if block is predominantly or distinctly bold")
    source_line_ids: List[str] = Field(default_factory=list, description="IDs of source SpatialLine objects")
    source_word_ids: List[str] = Field(default_factory=list, description="IDs of source SpatialWord objects")


class LayoutDocument(BaseModel):
    """Fully reconstructed CV document with column detection, source blocks, and reading order."""

    filename: str = Field(description="Original filename")
    total_pages: int = Field(description="Total page count")
    source_blocks: List[SourceBlock] = Field(default_factory=list, description="All blocks in logical reading order")
    layouts_by_page: Dict[int, ColumnLayout] = Field(default_factory=dict, description="Page layouts keyed by page number")
    reading_order_text: str = Field(default="", description="Complete document text in logical reading order")
    extraction_mode: str = Field(default="pymupdf_spatial_layout", description="Extraction strategy identifier")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Document metadata")

    def get_blocks_by_region(self, region_type: str) -> List[SourceBlock]:
        """Return all blocks belonging to a specific region type."""
        return [b for b in self.source_blocks if b.region_type == region_type]

    def get_blocks_by_column(self, column: int, page: Optional[int] = None) -> List[SourceBlock]:
        """Return all blocks belonging to a specific column index, optionally filtered by page."""
        return [
            b for b in self.source_blocks
            if b.column == column and (page is None or b.page == page)
        ]

    def get_headings(self) -> List[SourceBlock]:
        """Return all blocks identified as section headings in reading order."""
        return [b for b in self.source_blocks if b.is_heading]

    def find_block_by_id(self, block_id: str) -> Optional[SourceBlock]:
        """Find a source block by its stable identifier (e.g. BLOCK_005)."""
        for b in self.source_blocks:
            if b.id == block_id:
                return b
        return None
