"""
PDF Security and Compression Service.

Provides compression, password protection, and permission management
using pikepdf with in-memory processing.

Reference: PDF-08 to PDF-11
"""
from io import BytesIO
from typing import List, Optional, Dict

import pikepdf

from app.schemas.pdf import QualityPreset
from app.utils.file_utils import FileValidationError


# Permission mapping for pikepdf
PERMISSION_MAP = {
    "print": pikepdf.Permissions.extract_printing,
    "copy": pikepdf.Permissions.copy_content,
    "edit": pikepdf.Permissions.modify_form_fields,
    "annotate": pikepdf.Permissions.modify_annotations,
    "fill_forms": pikepdf.Permissions.fill_form_fields,
    "extract": pikepdf.Permissions.extract_content,
}


# Quality preset configurations
QUALITY_SETTINGS = {
    QualityPreset.LOW: {
        "dpi": 72,
        "image_quality": 60,
        "downsample": True,
    },
    QualityPreset.MEDIUM: {
        "dpi": 150,
        "image_quality": 75,
        "downsample": True,
    },
    QualityPreset.HIGH: {
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
    Compress PDF using quality presets.
    
    Args:
        file: PDF BytesIO object
        quality: Compression quality preset
        
    Returns:
        BytesIO: Compressed PDF
    """
    file.seek(0)
    output = BytesIO()
    settings = QUALITY_SETTINGS[quality]
    
    with pikepdf.Pdf.open(file) as pdf:
        # Apply compression settings
        # pikepdf's save method supports linearize and compress options
        pdf.save(
            output,
            linearize=True,  # Optimize for fast web viewing
            compress_streams=True,  # Compress content streams
            object_stream_mode=pikepdf.ObjectStreamMode.generate,
        )
    
    output.seek(0)
    return output


def add_password(
    file: BytesIO,
    password: str,
    permissions: Optional[List[str]] = None
) -> BytesIO:
    """
    Add password protection to PDF.
    
    Args:
        file: PDF BytesIO object
        password: Password to set (both owner and user password)
        permissions: Optional list of permissions to allow
        
    Returns:
        BytesIO: Encrypted PDF
    """
    file.seek(0)
    output = BytesIO()
    
    with pikepdf.Pdf.open(file) as pdf:
        # Build permissions
        perms = pikepdf.Permissions()
        if permissions:
            for perm_name in permissions:
                if perm_name in PERMISSION_MAP:
                    perms |= PERMISSION_MAP[perm_name]
        
        # Create encryption with AES-256
        encryption = pikepdf.Encryption(
            owner=password,
            user=password,
            allow=perms,
            R=6,  # AES-256 encryption
        )
        
        pdf.save(output, encryption=encryption)
    
    output.seek(0)
    return output


def remove_password(
    file: BytesIO,
    password: str
) -> BytesIO:
    """
    Remove password protection from PDF.
    
    Args:
        file: PDF BytesIO object
        password: Current password
        
    Returns:
        BytesIO: Decrypted PDF
        
    Raises:
        FileValidationError: If password is incorrect
    """
    file.seek(0)
    output = BytesIO()
    
    try:
        with pikepdf.Pdf.open(file, password=password) as pdf:
            # Save without encryption
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
    """
    Modify permissions on an encrypted PDF.
    
    Args:
        file: PDF BytesIO object
        password: Owner password
        permissions: List of permissions to allow
        
    Returns:
        BytesIO: PDF with modified permissions
    """
    file.seek(0)
    output = BytesIO()
    
    try:
        with pikepdf.Pdf.open(file, password=password) as pdf:
            # Build new permissions
            perms = pikepdf.Permissions()
            for perm_name in permissions:
                if perm_name in PERMISSION_MAP:
                    perms |= PERMISSION_MAP[perm_name]
            
            # Re-encrypt with new permissions
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
    """
    Check if PDF is password protected.
    
    Args:
        file: PDF BytesIO object
        
    Returns:
        bool: True if encrypted, False otherwise
    """
    file.seek(0)
    try:
        with pikepdf.Pdf.open(file) as pdf:
            return pdf.is_encrypted
    except pikepdf.PasswordError:
        return True
    finally:
        file.seek(0)
