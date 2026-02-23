"""
PDF Security and Compression Service.

Provides compression, password protection, and permission management
using pikepdf and PyMuPDF with in-memory processing.

Reference: PDF-08 to PDF-11
"""
import os
from io import BytesIO
from typing import List, Optional, Dict, Tuple
from pathlib import Path

import fitz  # PyMuPDF
import pikepdf
import zlib
from PIL import Image

from app.schemas.pdf import QualityPreset
from app.utils.file_utils import FileValidationError


# Permission field mapping for pikepdf (v9+ API)
PERMISSION_FIELDS = {
    "print": ("print_lowres", "print_highres"),
    "copy": ("extract",),
    "edit": ("modify_form", "modify_other"),
    "annotate": ("modify_annotation",),
    "fill_forms": ("modify_form",),
    "extract": ("extract",),
}


def build_permissions(allowed: List[str]) -> pikepdf.Permissions:
    """Build a Permissions object from a list of allowed permission names."""
    perm_dict = {
        'accessibility': True,
        'extract': False,
        'modify_annotation': False,
        'modify_assembly': False,
        'modify_form': False,
        'modify_other': False,
        'print_lowres': False,
        'print_highres': False,
    }
    
    for perm_name in allowed:
        if perm_name in PERMISSION_FIELDS:
            for field in PERMISSION_FIELDS[perm_name]:
                perm_dict[field] = True
    
    return pikepdf.Permissions(**perm_dict)


# Quality preset configurations
# Note: Preset names indicate compression LEVEL, not quality level
# HIGH = maximum compression (smallest file), LOW = minimal compression (preserve quality)
QUALITY_SETTINGS = {
    QualityPreset.HIGH: {
        "dpi": 72,
        "image_quality": 60,
        "downsample": True,
    },
    QualityPreset.MEDIUM: {
        "dpi": 150,
        "image_quality": 75,
        "downsample": True,
    },
    QualityPreset.LOW: {
        "dpi": 300,
        "image_quality": 90,
        "downsample": False,
    },
}


def compress_pdf(
    file: BytesIO,
    quality: QualityPreset = QualityPreset.MEDIUM
) -> BytesIO:
    """
    Compress PDF using quality presets with actual image recompression.
    
    This function uses PyMuPDF to recompress images with the specified quality,
    which provides much better compression than stream compression alone.
    
    Args:
        file: PDF BytesIO object
        quality: Compression quality preset
        
    Returns:
        BytesIO: Compressed PDF
    """
    file.seek(0)
    settings = QUALITY_SETTINGS[quality]
    
    # Open PDF with PyMuPDF
    pdf = fitz.open(stream=file.read(), filetype="pdf")
    output = BytesIO()
    
    try:
        dpi = settings["dpi"]
        img_quality = settings["image_quality"]
        downsample = settings["downsample"]
        
        # Calculate dimensions for target DPI
        # Standard PDF is 72 DPI, so scale factor is dpi/72
        scale_factor = dpi / 72.0
        
        for page_num in range(len(pdf)):
            page = pdf[page_num]
            
            # Get all images on the page
            image_list = page.get_images(full=True)
            
            for img_index, img in enumerate(image_list):
                xref = img[0]
                
                try:
                    # Extract image
                    base_image = pdf.extract_image(xref)
                    image_bytes = base_image["image"]
                    ext = base_image["ext"]
                    
                    # Open with PIL for recompression
                    pil_image = Image.open(BytesIO(image_bytes))
                    
                    # Skip if image is already small
                    orig_width, orig_height = pil_image.size
                    if orig_width * orig_height < 10000:  # Skip small images
                        continue
                    
                    # Calculate new size if downsampling
                    if downsample and scale_factor < 1.0:
                        new_width = int(orig_width * scale_factor)
                        new_height = int(orig_height * scale_factor)
                        pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    
                    # Recompress based on image mode
                    output_buffer = BytesIO()
                    
                    if pil_image.mode == "RGBA":
                        # For images with transparency, use PNG with optimization
                        pil_image.save(output_buffer, format="PNG", optimize=True)
                    elif pil_image.mode == "CMYK":
                        # For CMYK images (common in PDFs), convert to RGB
                        pil_image = pil_image.convert("RGB")
                        pil_image.save(output_buffer, format="JPEG", quality=img_quality, optimize=True)
                    else:
                        # Standard RGB or grayscale - use JPEG with specified quality
                        if pil_image.mode != "RGB":
                            pil_image = pil_image.convert("RGB")
                        pil_image.save(output_buffer, format="JPEG", quality=img_quality, optimize=True)
                    
                    output_buffer.seek(0)
                    new_image_bytes = output_buffer.read()
                    
                    # Only replace if we actually saved space
                    if len(new_image_bytes) < len(image_bytes) * 0.95:  # 5% threshold
                        # Replace image in PDF
                        pdf.update_stream(xref, new_image_bytes)
                        
                except Exception:
                    # If image processing fails, skip this image
                    continue
            
            # Clean up page
            page.clean_contents()
        
        # Garbage collection and save with compression
        pdf.save(
            output,
            garbage=4,  # Maximum garbage collection
            deflate=True,  # Compress streams
            clean=True,  # Clean content streams
        )
        
        output.seek(0)
        return output
        
    finally:
        pdf.close()


def add_password(
    file: BytesIO,
    password: str,
    permissions: Optional[List[str]] = None
) -> BytesIO:
    """Add password protection to PDF."""
    file.seek(0)
    output = BytesIO()
    
    with pikepdf.Pdf.open(file) as pdf:
        perms = build_permissions(permissions) if permissions else pikepdf.Permissions(
            accessibility=True,
            extract=False,
            modify_annotation=False,
            modify_assembly=False,
            modify_form=False,
            modify_other=False,
            print_lowres=False,
            print_highres=False,
        )
        
        encryption = pikepdf.Encryption(
            owner=password,
            user=password,
            allow=perms,
            R=6,
        )
        
        pdf.save(output, encryption=encryption)
    
    output.seek(0)
    return output


def remove_password(
    file: BytesIO,
    password: str
) -> BytesIO:
    """Remove password protection from PDF."""
    file.seek(0)
    output = BytesIO()
    
    try:
        with pikepdf.Pdf.open(file, password=password) as pdf:
            pdf.save(output)
    except pikepdf.PasswordError:
        raise FileValidationError(
            status_code=401,
            detail="Incorrect password provided"
        )
    except pikepdf.PdfError as e:
        raise FileValidationError(
            status_code=400,
            detail=f"Error opening PDF: {str(e)}"
        )
    
    output.seek(0)
    return output


def set_permissions(
    file: BytesIO,
    password: str,
    permissions: List[str]
) -> BytesIO:
    """Modify permissions on an encrypted PDF."""
    file.seek(0)
    output = BytesIO()
    
    try:
        with pikepdf.Pdf.open(file, password=password) as pdf:
            perms = build_permissions(permissions)
            
            encryption = pikepdf.Encryption(
                owner=password,
                user=password,
                allow=perms,
                R=6,
            )
            
            pdf.save(output, encryption=encryption)
    except pikepdf.PasswordError:
        raise FileValidationError(
            status_code=401,
            detail="Incorrect password provided"
        )
    
    output.seek(0)
    return output


def is_encrypted(file: BytesIO) -> bool:
    """Check if PDF is password protected."""
    file.seek(0)
    try:
        with pikepdf.Pdf.open(file) as pdf:
            return pdf.is_encrypted
    except pikepdf.PasswordError:
        return True
    finally:
        file.seek(0)
