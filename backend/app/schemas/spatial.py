"""Spatial PDF Document Representation Schemas.

Defines coordinate-aware Pydantic models for physical document structure:
BoundingBox, SpatialWord, SpatialLine, SpatialBlock, SpatialPage, and SpatialDocument.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, computed_field


class BoundingBox(BaseModel):
    """2D spatial bounding box in PDF coordinate space (points, origin at top-left)."""

    x0: float = Field(description="Left coordinate")
    y0: float = Field(description="Top coordinate")
    x1: float = Field(description="Right coordinate")
    y1: float = Field(description="Bottom coordinate")

    @computed_field
    @property
    def width(self) -> float:
        """Horizontal extent of the bounding box."""
        return max(0.0, round(self.x1 - self.x0, 2))

    @computed_field
    @property
    def height(self) -> float:
        """Vertical extent of the bounding box."""
        return max(0.0, round(self.y1 - self.y0, 2))

    @property
    def center_x(self) -> float:
        """Horizontal centroid."""
        return round((self.x0 + self.x1) / 2.0, 2)

    @property
    def center_y(self) -> float:
        """Vertical centroid."""
        return round((self.y0 + self.y1) / 2.0, 2)

    def overlaps(self, other: "BoundingBox") -> bool:
        """Return True if this bounding box overlaps another bounding box in 2D space."""
        return not (
            self.x1 < other.x0
            or self.x0 > other.x1
            or self.y1 < other.y0
            or self.y0 > other.y1
        )

    def contains(self, other: "BoundingBox") -> bool:
        """Return True if this bounding box completely contains the other."""
        return (
            self.x0 <= other.x0
            and self.y0 <= other.y0
            and self.x1 >= other.x1
            and self.y1 >= other.y1
        )

    def horizontal_distance_to(self, other: "BoundingBox") -> float:
        """Horizontal gap distance between two bounding boxes (0.0 if overlapping horizontally)."""
        if self.x1 < other.x0:
            return round(other.x0 - self.x1, 2)
        if other.x1 < self.x0:
            return round(self.x0 - other.x1, 2)
        return 0.0

    def vertical_distance_to(self, other: "BoundingBox") -> float:
        """Vertical gap distance between two bounding boxes (0.0 if overlapping vertically)."""
        if self.y1 < other.y0:
            return round(other.y0 - self.y1, 2)
        if other.y1 < self.y0:
            return round(self.y0 - other.y1, 2)
        return 0.0


class SpatialWord(BaseModel):
    """Atomic token with precise bounding box coordinates and typography metadata."""

    text: str = Field(description="Token text content")
    page: int = Field(description="1-based page number")
    x0: float = Field(description="Left boundary coordinate")
    y0: float = Field(description="Top boundary coordinate")
    x1: float = Field(description="Right boundary coordinate")
    y1: float = Field(description="Bottom boundary coordinate")
    block_id: Optional[str] = Field(default=None, description="Identifier of parent block, e.g. p1_b2")
    line_id: Optional[str] = Field(default=None, description="Identifier of parent line, e.g. p1_b2_l0")
    word_id: Optional[str] = Field(default=None, description="Identifier of word within line, e.g. p1_b2_l0_w0")
    font_name: Optional[str] = Field(default=None, description="Font family or PostScript name")
    font_size: Optional[float] = Field(default=None, description="Font size in points")
    is_bold: bool = Field(default=False, description="True if font weight is bold")
    is_italic: bool = Field(default=False, description="True if font style is italic / oblique")
    font_style: Optional[str] = Field(default="normal", description="Style descriptor: normal, bold, italic, bold_italic")
    weight: Optional[int] = Field(default=None, description="Numeric font weight, e.g. 700 (bold) or 400 (normal)")
    color: Optional[int] = Field(default=None, description="sRGB integer color")

    @property
    def bbox(self) -> BoundingBox:
        """Return BoundingBox representation of word boundaries."""
        return BoundingBox(x0=self.x0, y0=self.y0, x1=self.x1, y1=self.y1)


class SpatialLine(BaseModel):
    """Horizontal run of words on a page with geometry and font metadata."""

    line_id: str = Field(description="Identifier of line, e.g. p1_b2_l0")
    block_id: str = Field(description="Identifier of parent block, e.g. p1_b2")
    page: int = Field(description="1-based page number")
    bbox: BoundingBox = Field(description="Bounding box enclosing line")
    text: str = Field(description="Joined text of line")
    words: List[SpatialWord] = Field(default_factory=list, description="Tokens belonging to this line")
    font_name: Optional[str] = Field(default=None, description="Predominant font name")
    font_size: Optional[float] = Field(default=None, description="Predominant font size")
    is_bold: bool = Field(default=False, description="True if line contains bold text")
    is_italic: bool = Field(default=False, description="True if line contains italic text")


class SpatialBlock(BaseModel):
    """Cohesive spatial block of text or graphics on a page."""

    block_id: str = Field(description="Identifier of block, e.g. p1_b2")
    page: int = Field(description="1-based page number")
    bbox: BoundingBox = Field(description="Bounding box enclosing block")
    block_type: str = Field(default="text", description="Block type: 'text', 'image', or 'separator'")
    raw_text: str = Field(description="Unmodified raw text of the block")
    lines: List[SpatialLine] = Field(default_factory=list, description="Lines in this block")

    @property
    def words(self) -> List[SpatialWord]:
        """Flattened list of words in this block."""
        return [w for line in self.lines for w in line.words]

    @property
    def is_multi_line(self) -> bool:
        """True if the block spans more than one line."""
        return len(self.lines) > 1


class SpatialPage(BaseModel):
    """Spatial representation of a single PDF page."""

    page_number: int = Field(description="1-based page number")
    width: float = Field(description="Page width in points")
    height: float = Field(description="Page height in points")
    bbox: BoundingBox = Field(description="Page dimensions bounding box")
    blocks: List[SpatialBlock] = Field(default_factory=list, description="Blocks on this page")
    raw_text: str = Field(default="", description="Unmodified raw text of page")

    @property
    def all_lines(self) -> List[SpatialLine]:
        """All lines on this page across all blocks."""
        return [line for b in self.blocks for line in b.lines]

    @property
    def all_words(self) -> List[SpatialWord]:
        """All words on this page across all lines and blocks."""
        return [w for b in self.blocks for line in b.lines for w in line.words]


class SpatialDocument(BaseModel):
    """Complete spatial document representation containing hierarchical layout geometry."""

    filename: str = Field(description="Original document filename")
    total_pages: int = Field(description="Total number of pages")
    pages: List[SpatialPage] = Field(default_factory=list, description="Extracted spatial pages")
    raw_text: str = Field(default="", description="Complete unmodified raw text of the document")
    extraction_mode: str = Field(default="pymupdf_spatial", description="'pymupdf_spatial' or 'pypdf_fallback'")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Document metadata / PDF info")

    def get_words(self, page_number: Optional[int] = None) -> List[SpatialWord]:
        """Return words across all pages or filtered by page number."""
        if page_number is not None:
            for p in self.pages:
                if p.page_number == page_number:
                    return p.all_words
            return []
        return [w for p in self.pages for w in p.all_words]

    def get_lines(self, page_number: Optional[int] = None) -> List[SpatialLine]:
        """Return lines across all pages or filtered by page number."""
        if page_number is not None:
            for p in self.pages:
                if p.page_number == page_number:
                    return p.all_lines
            return []
        return [line for p in self.pages for line in p.all_lines]

    def get_blocks(self, page_number: Optional[int] = None) -> List[SpatialBlock]:
        """Return blocks across all pages or filtered by page number."""
        if page_number is not None:
            for p in self.pages:
                if p.page_number == page_number:
                    return p.blocks
            return []
        return [b for p in self.pages for b in p.blocks]
