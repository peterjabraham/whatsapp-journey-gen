"""
PDF extraction tool - extracts text and structure from PDF files.

Uses pymupdf4llm for clean markdown extraction optimized for LLM processing.
Falls back to basic PyMuPDF if pymupdf4llm has issues.
"""

import os
import tempfile
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class PDFExtractionResult:
    """Result of PDF extraction."""
    content: str  # Extracted text (markdown formatted)
    source: str   # Original filename
    pages: int    # Number of pages
    success: bool
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def extract_pdf(file_path: str) -> PDFExtractionResult:
    """
    Extract text content from a PDF file.
    
    Uses pymupdf4llm for markdown-formatted extraction that works well
    with LLMs. Falls back to basic extraction if needed.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        PDFExtractionResult with extracted content
    """
    if not os.path.exists(file_path):
        return PDFExtractionResult(
            content="",
            source=file_path,
            pages=0,
            success=False,
            error=f"File not found: {file_path}"
        )
    
    # Try pymupdf4llm first (best for LLM processing)
    try:
        import pymupdf4llm
        
        md_text = pymupdf4llm.to_markdown(file_path)
        
        # Get page count
        import pymupdf
        doc = pymupdf.open(file_path)
        page_count = len(doc)
        doc.close()
        
        return PDFExtractionResult(
            content=md_text,
            source=os.path.basename(file_path),
            pages=page_count,
            success=True
        )
        
    except ImportError:
        # pymupdf4llm not installed, try basic PyMuPDF
        pass
    except Exception as e:
        # pymupdf4llm failed, try fallback
        pass
    
    # Fallback to basic PyMuPDF extraction
    try:
        import pymupdf
        
        doc = pymupdf.open(file_path)
        text_parts = []
        
        for page_num, page in enumerate(doc, 1):
            text = page.get_text()
            if text.strip():
                text_parts.append(f"## Page {page_num}\n\n{text}")
        
        page_count = len(doc)
        doc.close()
        
        return PDFExtractionResult(
            content="\n\n".join(text_parts),
            source=os.path.basename(file_path),
            pages=page_count,
            success=True
        )
        
    except ImportError:
        return PDFExtractionResult(
            content="",
            source=file_path,
            pages=0,
            success=False,
            error="PyMuPDF not installed. Run: pip install pymupdf pymupdf4llm"
        )
    except Exception as e:
        return PDFExtractionResult(
            content="",
            source=file_path,
            pages=0,
            success=False,
            error=f"PDF extraction failed: {str(e)}"
        )


def extract_pdf_from_bytes(pdf_bytes: bytes, filename: str = "upload.pdf") -> PDFExtractionResult:
    """
    Extract text from PDF bytes (e.g., from file upload).
    
    Args:
        pdf_bytes: Raw PDF file bytes
        filename: Original filename for reference
        
    Returns:
        PDFExtractionResult with extracted content
    """
    # Write to temporary file
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
        tmp.write(pdf_bytes)
        tmp_path = tmp.name
    
    try:
        result = extract_pdf(tmp_path)
        result.source = filename  # Use original filename
        return result
    finally:
        # Clean up temp file
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def get_pdf_metadata(file_path: str) -> Dict[str, Any]:
    """
    Get metadata from a PDF file without full extraction.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Dictionary with metadata (title, author, pages, etc.)
    """
    try:
        import pymupdf
        
        doc = pymupdf.open(file_path)
        metadata = doc.metadata or {}
        
        result = {
            "title": metadata.get("title", ""),
            "author": metadata.get("author", ""),
            "subject": metadata.get("subject", ""),
            "creator": metadata.get("creator", ""),
            "pages": len(doc),
            "file_size": os.path.getsize(file_path),
        }
        
        doc.close()
        return result
        
    except Exception as e:
        return {
            "error": str(e),
            "pages": 0,
        }

