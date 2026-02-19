"""
Services package.
"""
from app.services.pdf_service import (
    merge_pdfs,
    split_pdf,
    rotate_pages,
    reorder_pages,
    delete_pages,
    extract_page_as_pdf,
)
from app.services.pdf_security_service import (
    compress_pdf,
    add_password,
    remove_password,
    set_permissions,
    is_encrypted,
)
from app.services.pdf_watermark_service import (
    add_text_watermark,
    add_image_watermark,
)
from app.services.pdf_extract_service import (
    extract_text,
    extract_images,
    extract_pages,
    clean_text,
    get_pdf_metadata,
)
from app.services.image_service import (
    pdf_to_images,
    images_to_pdf,
    image_to_pdf_simple,
)

__all__ = [
    # PDF Core
    "merge_pdfs",
    "split_pdf",
    "rotate_pages",
    "reorder_pages",
    "delete_pages",
    "extract_page_as_pdf",
    # PDF Security
    "compress_pdf",
    "add_password",
    "remove_password",
    "set_permissions",
    "is_encrypted",
    # PDF Watermark
    "add_text_watermark",
    "add_image_watermark",
    # PDF Extraction
    "extract_text",
    "extract_images",
    "extract_pages",
    "clean_text",
    "get_pdf_metadata",
    # Image Conversion
    "pdf_to_images",
    "images_to_pdf",
    "image_to_pdf_simple",
]
