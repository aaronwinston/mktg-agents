"""Sanitization utilities for ForgeOS API."""

import re
from typing import Any, Optional
from html import escape as html_escape
import json


def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize a string by removing control characters and optionally limiting length.
    
    Args:
        value: String to sanitize
        max_length: Maximum length (if exceeded, string is truncated)
    
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return str(value)
    
    # Remove control characters
    sanitized = ''.join(ch for ch in value if ord(ch) >= 32 or ch in '\n\r\t')
    
    # Optionally truncate
    if max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized


def sanitize_html(value: str) -> str:
    """Escape HTML special characters."""
    if not isinstance(value, str):
        return str(value)
    
    return html_escape(value)


def sanitize_url(url: str) -> str:
    """
    Sanitize URL by removing dangerous characters and encoding.
    
    Args:
        url: URL to sanitize
    
    Returns:
        Sanitized URL
    """
    if not isinstance(url, str):
        return ""
    
    # Remove control characters
    sanitized = ''.join(ch for ch in url if ord(ch) >= 32)
    
    # Remove javascript: and data: schemes
    if re.match(r'^(javascript|data):', sanitized, re.IGNORECASE):
        return ""
    
    return sanitized


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing dangerous characters.
    
    Args:
        filename: Filename to sanitize
    
    Returns:
        Sanitized filename
    """
    if not isinstance(filename, str):
        return "file"
    
    # Remove path traversal attempts
    filename = filename.replace("..", "")
    filename = filename.replace("/", "")
    filename = filename.replace("\\", "")
    
    # Keep only alphanumeric, dots, hyphens, underscores
    filename = re.sub(r'[^a-zA-Z0-9._-]', '', filename)
    
    # Ensure filename is not empty
    if not filename:
        filename = "file"
    
    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        name = name[:250 - len(ext)]
        filename = f"{name}.{ext}" if ext else name
    
    return filename


def sanitize_email(email: str) -> str:
    """
    Sanitize email by lowercasing and removing whitespace.
    
    Args:
        email: Email to sanitize
    
    Returns:
        Sanitized email
    """
    if not isinstance(email, str):
        return ""
    
    return email.strip().lower()


def sanitize_dict(data: dict, max_depth: int = 10) -> dict:
    """
    Recursively sanitize dictionary values.
    
    Args:
        data: Dictionary to sanitize
        max_depth: Maximum recursion depth
    
    Returns:
        Sanitized dictionary
    """
    if max_depth <= 0:
        return {}
    
    sanitized = {}
    
    for key, value in data.items():
        # Sanitize key
        if isinstance(key, str):
            key = sanitize_string(key, max_length=255)
        
        # Sanitize value
        if isinstance(value, str):
            sanitized[key] = sanitize_string(value)
        elif isinstance(value, dict):
            sanitized[key] = sanitize_dict(value, max_depth - 1)
        elif isinstance(value, list):
            sanitized[key] = sanitize_list(value, max_depth - 1)
        else:
            sanitized[key] = value
    
    return sanitized


def sanitize_list(data: list, max_depth: int = 10) -> list:
    """
    Recursively sanitize list values.
    
    Args:
        data: List to sanitize
        max_depth: Maximum recursion depth
    
    Returns:
        Sanitized list
    """
    if max_depth <= 0:
        return []
    
    sanitized = []
    
    for item in data:
        if isinstance(item, str):
            sanitized.append(sanitize_string(item))
        elif isinstance(item, dict):
            sanitized.append(sanitize_dict(item, max_depth - 1))
        elif isinstance(item, list):
            sanitized.append(sanitize_list(item, max_depth - 1))
        else:
            sanitized.append(item)
    
    return sanitized


def sanitize_json_string(json_str: str) -> str:
    """
    Sanitize JSON string.
    
    Args:
        json_str: JSON string to sanitize
    
    Returns:
        Sanitized JSON string
    """
    try:
        data = json.loads(json_str)
        if isinstance(data, dict):
            data = sanitize_dict(data)
        elif isinstance(data, list):
            data = sanitize_list(data)
        return json.dumps(data)
    except (json.JSONDecodeError, TypeError):
        return ""
