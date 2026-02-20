"""
Web content conversion service.

Provides conversions from HTML, Markdown, and URLs to PDF
using WeasyPrint (pure Python HTML/CSS renderer).

All conversions maintain zero-trace in-memory processing.

Reference: CONV-07 to CONV-09
Constraint: All operations use BytesIO (ARCH-01)
"""
import asyncio
import ipaddress
from io import BytesIO
from typing import Optional
from urllib.parse import urlparse

import httpx
import markdown
from weasyprint import HTML, CSS


# Default timeout for URL fetching (seconds)
DEFAULT_URL_TIMEOUT = 30


def _is_safe_url(url: str) -> bool:
    """
    Validate URL for safety (SSRF prevention).
    
    Blocks:
    - Non-HTTP schemes
    - Localhost
    - Private IP addresses
    - Loopback addresses
    
    Args:
        url: URL to validate
        
    Returns:
        bool: True if URL is safe to fetch
    """
    try:
        parsed = urlparse(url)
    except Exception:
        return False
    
    # Only allow http and https schemes
    if parsed.scheme not in ('http', 'https'):
        return False
    
    # Get hostname
    hostname = parsed.hostname
    if not hostname:
        return False
    
    # Block common localhost variants
    blocked_hostnames = {
        'localhost',
        '127.0.0.1',
        '0.0.0.0',
        '::1',
        '0:0:0:0:0:0:0:1',
    }
    if hostname.lower() in blocked_hostnames:
        return False
    
    # Try to parse as IP address and check for private/loopback
    try:
        ip = ipaddress.ip_address(hostname)
        if ip.is_private or ip.is_loopback or ip.is_link_local:
            return False
        # Block multicast and reserved
        if ip.is_multicast or ip.is_reserved:
            return False
    except ValueError:
        # Not an IP address, might be a domain name
        # Block domains that look like internal services
        lower_host = hostname.lower()
        if any(pattern in lower_host for pattern in [
            'localhost', 'internal', 'local', 'intranet',
            '.local', '.internal', '.localhost'
        ]):
            return False
    
    return True


def html_to_pdf(html_content: str, base_url: Optional[str] = None) -> BytesIO:
    """
    Convert HTML content to PDF.
    
    Args:
        html_content: HTML string to convert
        base_url: Optional base URL for resolving relative URLs
        
    Returns:
        BytesIO: PDF document
    """
    output = BytesIO()
    
    # Create HTML document
    html = HTML(string=html_content, base_url=base_url)
    
    # Use default CSS for better rendering
    default_css = CSS(string='''
        @page {
            size: A4;
            margin: 2cm;
        }
        body {
            font-family: sans-serif;
            line-height: 1.4;
        }
    ''')
    
    # Write PDF
    html.write_pdf(output, stylesheets=[default_css])
    
    output.seek(0)
    return output


def markdown_to_pdf(markdown_content: str) -> BytesIO:
    """
    Convert Markdown content to PDF.
    
    Converts Markdown to HTML first, then to PDF.
    Supports common Markdown extensions: tables, code blocks, TOC.
    
    Args:
        markdown_content: Markdown string to convert
        
    Returns:
        BytesIO: PDF document
    """
    # Convert markdown to HTML with extensions
    html_content = markdown.markdown(
        markdown_content,
        extensions=[
            'tables',
            'fenced_code',
            'toc',
            'nl2br',  # Newline to <br>
            'sane_lists',  # Better list handling
        ]
    )
    
    # Wrap in styled HTML document
    styled_html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Converted Document</title>
</head>
<body>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 
                         'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            max-width: 100%;
            color: #333;
        }}
        h1, h2, h3, h4, h5, h6 {{
            margin-top: 1.5em;
            margin-bottom: 0.5em;
            line-height: 1.2;
        }}
        h1 {{ font-size: 2em; border-bottom: 1px solid #eee; padding-bottom: 0.3em; }}
        h2 {{ font-size: 1.5em; border-bottom: 1px solid #eee; padding-bottom: 0.3em; }}
        h3 {{ font-size: 1.25em; }}
        p {{ margin: 1em 0; }}
        code {{
            background-color: #f4f4f4;
            padding: 0.2em 0.4em;
            border-radius: 3px;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 0.9em;
        }}
        pre {{
            background-color: #f4f4f4;
            padding: 1em;
            border-radius: 5px;
            overflow-x: auto;
            line-height: 1.45;
        }}
        pre code {{
            background: none;
            padding: 0;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 1em 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px 12px;
            text-align: left;
        }}
        th {{
            background-color: #f5f5f5;
            font-weight: bold;
        }}
        tr:nth-child(even) {{
            background-color: #fafafa;
        }}
        blockquote {{
            border-left: 4px solid #ddd;
            margin: 1em 0;
            padding-left: 1em;
            color: #666;
        }}
        hr {{
            border: none;
            border-top: 1px solid #eee;
            margin: 2em 0;
        }}
        ul, ol {{
            padding-left: 2em;
            margin: 1em 0;
        }}
        li {{
            margin: 0.25em 0;
        }}
        img {{
            max-width: 100%;
            height: auto;
        }}
    </style>
    {html_content}
</body>
</html>'''
    
    return html_to_pdf(styled_html)


async def url_to_pdf(url: str, timeout: int = DEFAULT_URL_TIMEOUT) -> BytesIO:
    """
    Fetch URL and convert to PDF.
    
    Args:
        url: URL to fetch and convert
        timeout: Fetch timeout in seconds
        
    Returns:
        BytesIO: PDF document
        
    Raises:
        ValueError: If URL is invalid or blocked
        httpx.HTTPError: If fetch fails
    """
    # Validate URL for SSRF prevention
    if not _is_safe_url(url):
        raise ValueError(
            "Invalid or blocked URL. Only public HTTP/HTTPS URLs are allowed. "
            "Private IPs, localhost, and internal URLs are blocked."
        )
    
    # Fetch HTML content
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        response = await client.get(url)
        response.raise_for_status()
        html_content = response.text
    
    # Convert to PDF with original URL as base
    return html_to_pdf(html_content, base_url=url)


# Synchronous wrapper for async function (for use in non-async contexts)
def url_to_pdf_sync(url: str, timeout: int = DEFAULT_URL_TIMEOUT) -> BytesIO:
    """
    Synchronous wrapper for url_to_pdf.
    
    Args:
        url: URL to fetch and convert
        timeout: Fetch timeout in seconds
        
    Returns:
        BytesIO: PDF document
    """
    return asyncio.run(url_to_pdf(url, timeout))
