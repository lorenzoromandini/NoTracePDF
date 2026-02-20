"""
PDF Comparison Service.

Provides PDF comparison with visual diff highlighting
using PyMuPDF and Pillow for in-memory processing.

Reference: PDF-23
Constraint: All operations use BytesIO (ARCH-01)
"""
from io import BytesIO
from typing import Tuple, Optional
import math

import fitz  # PyMuPDF
from PIL import Image, ImageChops
import numpy as np


def compare_pdfs(
    file1: BytesIO,
    file2: BytesIO,
    highlight_add: str = "#00FF00",
    highlight_del: str = "#FF0000",
    include_summary: bool = True,
    dpi: int = 150
) -> BytesIO:
    """
    Compare two PDFs and create a visual diff.
    
    This renders both PDFs to images and compares them pixel-by-pixel,
    creating a new PDF with highlighted differences.
    
    Args:
        file1: First PDF BytesIO object (original)
        file2: Second PDF BytesIO object (modified)
        highlight_add: Hex color for additions (content in file2 not in file1)
        highlight_del: Hex color for deletions (content in file1 not in file2)
        include_summary: Whether to include a summary page
        dpi: Rendering DPI for comparison (higher = more accurate but slower)
        
    Returns:
        BytesIO: Comparison PDF with highlighted differences
    """
    # Read files
    file1.seek(0)
    file2.seek(0)
    
    doc1 = fitz.open(stream=file1.read(), filetype="pdf")
    doc2 = fitz.open(stream=file2.read(), filetype="pdf")
    
    try:
        total_pages1 = len(doc1)
        total_pages2 = len(doc2)
        max_pages = max(total_pages1, total_pages2)
        
        # Parse colors
        add_color = hex_to_rgb(highlight_add)
        del_color = hex_to_rgb(highlight_del)
        
        # Statistics
        stats = {
            "pages_compared": 0,
            "pages_added": 0,
            "pages_removed": 0,
            "pages_modified": 0,
            "total_additions": 0,
            "total_deletions": 0,
        }
        
        # Create result document
        result_doc = fitz.open()
        
        # Compare each page
        for i in range(max_pages):
            page1 = doc1[i] if i < total_pages1 else None
            page2 = doc2[i] if i < total_pages2 else None
            
            if page1 is None:
                # Page added in file2
                stats["pages_added"] += 1
                stats["total_additions"] += 1
                
                # Add the new page with green border
                new_page = result_doc.new_page(width=page2.rect.width, height=page2.rect.height)
                new_page.show_pdf_page(
                    new_page.rect,
                    doc2,
                    i
                )
                # Add border indicator
                rect = new_page.rect
                new_page.draw_rect(rect, color=add_color, width=5)
                new_page.insert_text(
                    fitz.Point(10, 20),
                    "ADDED PAGE",
                    fontsize=14,
                    color=add_color
                )
                continue
            
            if page2 is None:
                # Page removed in file2
                stats["pages_removed"] += 1
                stats["total_deletions"] += 1
                
                # Add the old page with red border
                new_page = result_doc.new_page(width=page1.rect.width, height=page1.rect.height)
                new_page.show_pdf_page(
                    new_page.rect,
                    doc1,
                    i
                )
                rect = new_page.rect
                new_page.draw_rect(rect, color=del_color, width=5)
                new_page.insert_text(
                    fitz.Point(10, 20),
                    "REMOVED PAGE",
                    fontsize=14,
                    color=del_color
                )
                continue
            
            # Both pages exist - compare them
            stats["pages_compared"] += 1
            
            # Render both pages to images
            mat = fitz.Matrix(dpi / 72, dpi / 72)  # Scale matrix for DPI
            
            pix1 = page1.get_pixmap(matrix=mat)
            pix2 = page2.get_pixmap(matrix=mat)
            
            # Convert to PIL Images
            img1 = Image.frombytes("RGB", [pix1.width, pix1.height], pix1.samples)
            img2 = Image.frombytes("RGB", [pix2.width, pix2.height], pix2.samples)
            
            # Ensure same size for comparison
            max_width = max(img1.width, img2.width)
            max_height = max(img1.height, img2.height)
            
            if img1.size != img2.size:
                # Resize to match
                img1_resized = Image.new("RGB", (max_width, max_height), (255, 255, 255))
                img1_resized.paste(img1, (0, 0))
                img1 = img1_resized
                
                img2_resized = Image.new("RGB", (max_width, max_height), (255, 255, 255))
                img2_resized.paste(img2, (0, 0))
                img2 = img2_resized
            
            # Compare images
            diff_add = ImageChops.difference(img2, img1)  # Additions
            diff_del = ImageChops.difference(img1, img2)  # Deletions
            
            # Convert to numpy for analysis
            diff_add_arr = np.array(diff_add)
            diff_del_arr = np.array(diff_del)
            
            # Find pixels that are different
            add_mask = np.any(diff_add_arr > 20, axis=2)  # Threshold for noise
            del_mask = np.any(diff_del_arr > 20, axis=2)
            
            additions = np.sum(add_mask)
            deletions = np.sum(del_mask)
            
            if additions > 0 or deletions > 0:
                stats["pages_modified"] += 1
                stats["total_additions"] += additions
                stats["total_deletions"] += deletions
            
            # Create result page
            new_page = result_doc.new_page(width=page2.rect.width, height=page2.rect.height)
            
            # Show the second page as base
            new_page.show_pdf_page(
                new_page.rect,
                doc2,
                i
            )
            
            # If there are differences, create overlay with highlights
            if additions > 0 or deletions > 0:
                # Create highlight overlay image
                overlay = Image.new("RGBA", (max_width, max_height), (0, 0, 0, 0))
                overlay_arr = np.array(overlay)
                
                # Add highlights for additions (green, semi-transparent)
                overlay_arr[add_mask] = (*add_color, 80)
                
                # Add highlights for deletions (red, semi-transparent)
                overlay_arr[del_mask] = (*del_color, 80)
                
                overlay = Image.fromarray(overlay_arr)
                
                # Convert overlay to PDF page and merge
                overlay_pdf = fitz.open("png", overlay.tobytes("png"))
                new_page.show_pdf_page(
                    new_page.rect,
                    overlay_pdf,
                    0,
                    keep_proportion=False
                )
                overlay_pdf.close()
                
                # Add page number indicator
                new_page.insert_text(
                    fitz.Point(10, 20),
                    f"Page {i + 1} - MODIFIED",
                    fontsize=10,
                    color=(0, 0, 0)
                )
            else:
                # No changes
                new_page.insert_text(
                    fitz.Point(10, 20),
                    f"Page {i + 1} - NO CHANGES",
                    fontsize=10,
                    color=(0, 0.5, 0)
                )
        
        # Add summary page if requested
        if include_summary:
            summary_page = result_doc.new_page(width=595, height=842)  # A4
            
            # Title
            summary_page.insert_text(
                fitz.Point(50, 50),
                "PDF Comparison Summary",
                fontsize=24,
                color=(0, 0, 0)
            )
            
            # Statistics
            y = 100
            line_height = 25
            
            summary_lines = [
                f"Original document: {total_pages1} pages",
                f"Modified document: {total_pages2} pages",
                "",
                "Summary:",
                f"  Pages compared: {stats['pages_compared']}",
                f"  Pages added: {stats['pages_added']}",
                f"  Pages removed: {stats['pages_removed']}",
                f"  Pages modified: {stats['pages_modified']}",
                "",
                f"Total additions (pixels): {stats['total_additions']:,}",
                f"Total deletions (pixels): {stats['total_deletions']:,}",
                "",
                "Legend:",
            ]
            
            for line in summary_lines:
                summary_page.insert_text(
                    fitz.Point(50, y),
                    line,
                    fontsize=12,
                    color=(0, 0, 0)
                )
                y += line_height
            
            # Legend colors
            summary_page.draw_rect(fitz.Rect(50, y, 70, y + 15), color=add_color, fill=add_color)
            summary_page.insert_text(fitz.Point(80, y + 12), "Additions (new content)", fontsize=12)
            
            y += line_height
            summary_page.draw_rect(fitz.Rect(50, y, 70, y + 15), color=del_color, fill=del_color)
            summary_page.insert_text(fitz.Point(80, y + 12), "Deletions (removed content)", fontsize=12)
        
        # Save to bytes
        output = BytesIO()
        result_doc.save(output, garbage=4, deflate=True)
        output.seek(0)
        
        result_doc.close()
        return output
        
    finally:
        doc1.close()
        doc2.close()


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """
    Convert hex color to RGB tuple (0-255).
    
    Args:
        hex_color: Hex color string (e.g., "#00FF00")
        
    Returns:
        Tuple of (r, g, b) values 0-255
    """
    if hex_color.startswith('#'):
        hex_color = hex_color[1:]
    
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    
    return (r, g, b)
