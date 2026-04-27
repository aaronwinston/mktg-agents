"""Validation utilities for ForgeOS API."""

import re
from typing import Any, Optional
from pydantic import ValidationError, BaseModel


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password(password: str, min_length: int = 8) -> tuple[bool, Optional[str]]:
    """
    Validate password strength.
    
    Returns:
        (is_valid, error_message)
    """
    if len(password) < min_length:
        return False, f"Password must be at least {min_length} characters"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one digit"
    
    return True, None


def validate_url(url: str) -> bool:
    """Validate URL format."""
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return bool(re.match(pattern, url, re.IGNORECASE))


def validate_org_slug(slug: str) -> tuple[bool, Optional[str]]:
    """
    Validate organization slug format.
    
    Returns:
        (is_valid, error_message)
    """
    if not slug:
        return False, "Slug cannot be empty"
    
    if len(slug) < 3:
        return False, "Slug must be at least 3 characters"
    
    if len(slug) > 50:
        return False, "Slug cannot exceed 50 characters"
    
    if not re.match(r'^[a-z0-9-]+$', slug):
        return False, "Slug can only contain lowercase letters, numbers, and hyphens"
    
    if slug.startswith('-') or slug.endswith('-'):
        return False, "Slug cannot start or end with a hyphen"
    
    return True, None


def validate_project_name(name: str) -> tuple[bool, Optional[str]]:
    """
    Validate project name.
    
    Returns:
        (is_valid, error_message)
    """
    if not name:
        return False, "Project name cannot be empty"
    
    if len(name) < 1:
        return False, "Project name must be at least 1 character"
    
    if len(name) > 255:
        return False, "Project name cannot exceed 255 characters"
    
    return True, None


def validate_object_id(obj_id: Any) -> bool:
    """Validate object ID (string format)."""
    if not isinstance(obj_id, str):
        return False
    
    return len(obj_id) > 0 and len(obj_id) <= 255


def validate_pagination(skip: int, limit: int) -> tuple[bool, Optional[str]]:
    """
    Validate pagination parameters.
    
    Returns:
        (is_valid, error_message)
    """
    if skip < 0:
        return False, "Skip must be non-negative"
    
    if limit < 1:
        return False, "Limit must be at least 1"
    
    if limit > 1000:
        return False, "Limit cannot exceed 1000"
    
    return True, None


def validate_json_field(data: Any) -> bool:
    """Validate that data is JSON-serializable."""
    try:
        import json
        json.dumps(data)
        return True
    except (TypeError, ValueError):
        return False
