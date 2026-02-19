"""
PDF Core Operations Service.

Provides merge, split, rotate, reorder, and delete operations
using pikepdf with in-memory processing.

Reference: PDF-01 to PDF-07
Constraint: All operations use BytesIO (ARCH-01)
"""
from io import BytesIO
from typing import List, Tuple, Optional, Union
from copy import copy

import pikepdf

from app.schemas.pdf import SplitMode, PageSelection
from app.utils.file_utils import (
    InvalidPageError,
    InvalidRotationError,
    EmptyResultError,
    validate_page_numbers,
)


def merge_pdfs(files: List[BytesIO]) -> BytesIO:
    """
    Merge multiple PDFs into a single PDF.
    
    Args:
        files: List of PDF BytesIO objects
        
    Returns:
        BytesIO: Merged PDF
    """
    output = BytesIO()
    
    with pikepdf.Pdf.new() as merged_pdf:
        for pdf_bytes in files:
            pdf_bytes.seek(0)
            with pikepdf.Pdf.open(pdf_bytes) as source:
                # Copy all pages from source to merged
                merged_pdf.pages.extend(source.pages)
        
        merged_pdf.save(output)
    
    output.seek(0)
    return output


def split_pdf(
    file: BytesIO,
    mode: SplitMode,
    start: Optional[int] = None,
    end: Optional[int] = None,
    n_pages: Optional[int] = None,
    pages: Optional[List[int]] = None
) -> List[Tuple[str, BytesIO]]:
    """
    Split PDF based on mode.
    
    Args:
        file: PDF BytesIO object
        mode: Split mode (range, every_n, specific)
        start: Start page for range mode (1-indexed)
        end: End page for range mode (1-indexed)
        n_pages: Split every N pages
        pages: Specific pages to extract (1-indexed)
        
    Returns:
        List of (filename, BytesIO) tuples
    """
    file.seek(0)
    
    with pikepdf.Pdf.open(file) as pdf:
        total_pages = len(pdf.pages)
        results = []
        
        if mode == SplitMode.RANGE:
            # Extract page range
            if start is None or end is None:
                raise ValueError("start and end required for range mode")
            
            validate_page_numbers([start, end], total_pages)
            
            output = BytesIO()
            with pikepdf.Pdf.new() as new_pdf:
                # pikepdf uses 0-indexed, user input is 1-indexed
                for i in range(start - 1, end):
                    new_pdf.pages.append(pdf.pages[i])
                new_pdf.save(output)
            output.seek(0)
            results.append((f"pages_{start}-{end}.pdf", output))
            
        elif mode == SplitMode.EVERY_N:
            # Split every N pages
            if n_pages is None or n_pages < 1:
                raise ValueError("n_pages must be >= 1")
            
            chunk_num = 1
            for i in range(0, total_pages, n_pages):
                output = BytesIO()
                with pikepdf.Pdf.new() as new_pdf:
                    end_idx = min(i + n_pages, total_pages)
                    for j in range(i, end_idx):
                        new_pdf.pages.append(pdf.pages[j])
                    new_pdf.save(output)
                output.seek(0)
                results.append((f"chunk_{chunk_num}.pdf", output))
                chunk_num += 1
                
        elif mode == SplitMode.SPECIFIC:
            # Extract specific pages
            if not pages:
                raise ValueError("pages required for specific mode")
            
            validate_page_numbers(pages, total_pages)
            
            # Create single PDF with all specified pages
            output = BytesIO()
            with pikepdf.Pdf.new() as new_pdf:
                for page_num in sorted(pages):
                    new_pdf.pages.append(pdf.pages[page_num - 1])
                new_pdf.save(output)
            output.seek(0)
            
            if len(pages) == 1:
                results.append((f"page_{pages[0]}.pdf", output))
            else:
                pages_str = "_".join(map(str, sorted(pages)))
                results.append((f"pages_{pages_str}.pdf", output))
    
    return results


def rotate_pages(
    file: BytesIO,
    pages: Union[str, List[int]],
    degrees: int
) -> BytesIO:
    """
    Rotate pages in PDF.
    
    Args:
        file: PDF BytesIO object
        pages: 'all' or list of page numbers (1-indexed)
        degrees: Rotation angle (90, 180, 270)
        
    Returns:
        BytesIO: Rotated PDF
    """
    # Validate degrees
    valid_degrees = [90, 180, 270, -90, -180, -270]
    if degrees not in valid_degrees:
        raise InvalidRotationError(f"Degrees must be one of {valid_degrees}")
    
    file.seek(0)
    output = BytesIO()
    
    with pikepdf.Pdf.open(file) as pdf:
        total_pages = len(pdf.pages)
        
        if pages == "all":
            # Rotate all pages
            for page in pdf.pages:
                page.rotate(degrees, relative=True)
        else:
            # Rotate specific pages
            validate_page_numbers(pages, total_pages)
            for page_num in pages:
                pdf.pages[page_num - 1].rotate(degrees, relative=True)
        
        pdf.save(output)
    
    output.seek(0)
    return output


def reorder_pages(
    file: BytesIO,
    page_order: List[int]
) -> BytesIO:
    """
    Reorder pages in PDF.
    
    Args:
        file: PDF BytesIO object
        page_order: New page order (1-indexed, e.g., [3, 1, 2, 4])
        
    Returns:
        BytesIO: Reordered PDF
    """
    file.seek(0)
    output = BytesIO()
    
    with pikepdf.Pdf.open(file) as pdf:
        total_pages = len(pdf.pages)
        
        # Validate page order
        if len(page_order) != total_pages:
            raise InvalidPageError(
                f"Page order must include all {total_pages} pages"
            )
        
        validate_page_numbers(page_order, total_pages)
        
        # Check for duplicates
        if len(set(page_order)) != len(page_order):
            raise InvalidPageError("Page order contains duplicates")
        
        # Create new page list in specified order
        # Use copy to avoid reference issues
        new_pages = [copy(pdf.pages[i - 1]) for i in page_order]
        
        # Remove all pages and add in new order
        while len(pdf.pages) > 0:
            del pdf.pages[0]
        
        for page in new_pages:
            pdf.pages.append(page)
        
        pdf.save(output)
    
    output.seek(0)
    return output


def delete_pages(
    file: BytesIO,
    pages: List[int]
) -> BytesIO:
    """
    Delete pages from PDF.
    
    Args:
        file: PDF BytesIO object
        pages: Pages to delete (1-indexed)
        
    Returns:
        BytesIO: PDF with pages deleted
        
    Raises:
        EmptyResultError: If all pages would be deleted
    """
    file.seek(0)
    output = BytesIO()
    
    with pikepdf.Pdf.open(file) as pdf:
        total_pages = len(pdf.pages)
        
        # Validate pages
        validate_page_numbers(pages, total_pages)
        
        # Check if all pages would be deleted
        if len(pages) >= total_pages:
            raise EmptyResultError("Cannot delete all pages from PDF")
        
        # Sort in reverse order to delete from end first
        # (avoiding index shifting issues)
        pages_to_delete = sorted(set(pages), reverse=True)
        
        for page_num in pages_to_delete:
            del pdf.pages[page_num - 1]
        
        pdf.save(output)
    
    output.seek(0)
    return output


def extract_page_as_pdf(
    file: BytesIO,
    page_num: int
) -> BytesIO:
    """
    Extract a single page as a new PDF.
    
    Args:
        file: PDF BytesIO object
        page_num: Page number to extract (1-indexed)
        
    Returns:
        BytesIO: Single-page PDF
    """
    file.seek(0)
    output = BytesIO()
    
    with pikepdf.Pdf.open(file) as pdf:
        total_pages = len(pdf.pages)
        
        if page_num < 1 or page_num > total_pages:
            raise InvalidPageError(
                f"Page {page_num} out of range. PDF has {total_pages} pages."
            )
        
        with pikepdf.Pdf.new() as new_pdf:
            new_pdf.pages.append(pdf.pages[page_num - 1])
            new_pdf.save(output)
    
    output.seek(0)
    return output
