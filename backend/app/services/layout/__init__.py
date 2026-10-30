"""Layout Reconstruction and Reading Order Package.

Provides deterministic column detection, heading detection, block reconstruction,
and logical reading-order sequencing for spatial CV documents.
"""

from app.services.layout.heading_detector import (
    PRIMARY_SECTION_PATTERNS,
    detect_heading_candidates,
)
from app.services.layout.column_detector import detect_page_columns
from app.services.layout.block_builder import build_source_blocks
from app.services.layout.reading_order import reconstruct_reading_order

__all__ = [
    "PRIMARY_SECTION_PATTERNS",
    "detect_heading_candidates",
    "detect_page_columns",
    "build_source_blocks",
    "reconstruct_reading_order",
]
