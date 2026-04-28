"""Helper utilities for ForgeOS API."""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, TypeVar, Generic, List
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


def generate_id(prefix: Optional[str] = None) -> str:
    """Generate a unique ID with optional prefix."""
    unique_id = str(uuid.uuid4()).replace('-', '')[:12]
    if prefix:
        return f"{prefix}_{unique_id}"
    return unique_id


def generate_org_id() -> str:
    """Generate a unique organization ID."""
    return generate_id("org")


def generate_project_id() -> str:
    """Generate a unique project ID."""
    return generate_id("proj")


def generate_user_id() -> str:
    """Generate a unique user ID."""
    return generate_id("user")


def truncate_string(text: str, length: int, suffix: str = "...") -> str:
    """
    Truncate string to specified length.
    
    Args:
        text: Text to truncate
        length: Maximum length
        suffix: Suffix to append if truncated
    
    Returns:
        Truncated text
    """
    if len(text) <= length:
        return text
    
    return text[:length - len(suffix)] + suffix


def chunk_list(items: List[T], chunk_size: int) -> List[List[T]]:
    """
    Split list into chunks of specified size.
    
    Args:
        items: List to chunk
        chunk_size: Size of each chunk
    
    Returns:
        List of chunks
    """
    chunks = []
    for i in range(0, len(items), chunk_size):
        chunks.append(items[i:i + chunk_size])
    return chunks


def paginate_list(items: List[T], skip: int = 0, limit: int = 20) -> tuple[List[T], int]:
    """
    Paginate a list of items.
    
    Args:
        items: List to paginate
        skip: Number of items to skip
        limit: Maximum number of items to return
    
    Returns:
        Tuple of (paginated items, total count)
    """
    total = len(items)
    paginated = items[skip:skip + limit]
    return paginated, total


def merge_dicts(*dicts) -> dict:
    """
    Merge multiple dictionaries (later values override earlier ones).
    
    Args:
        *dicts: Dictionaries to merge
    
    Returns:
        Merged dictionary
    """
    result = {}
    for d in dicts:
        if isinstance(d, dict):
            result.update(d)
    return result


def flatten_dict(d: dict, parent_key: str = '', sep: str = '_') -> dict:
    """
    Flatten nested dictionary.
    
    Args:
        d: Dictionary to flatten
        parent_key: Parent key prefix
        sep: Separator for nested keys
    
    Returns:
        Flattened dictionary
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime object to string."""
    if not isinstance(dt, datetime):
        return ""
    return dt.strftime(format_str)


def parse_datetime(date_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
    """Parse datetime string to datetime object."""
    try:
        return datetime.strptime(date_str, format_str)
    except (ValueError, TypeError):
        return None


def get_time_delta_seconds(minutes: int = 0, hours: int = 0, days: int = 0) -> int:
    """
    Calculate total seconds for a time delta.
    
    Args:
        minutes: Number of minutes
        hours: Number of hours
        days: Number of days
    
    Returns:
        Total seconds
    """
    delta = timedelta(minutes=minutes, hours=hours, days=days)
    return int(delta.total_seconds())


def is_expired(created_at: datetime, ttl_seconds: int) -> bool:
    """
    Check if a datetime has expired based on TTL.
    
    Args:
        created_at: Creation time
        ttl_seconds: Time-to-live in seconds
    
    Returns:
        True if expired, False otherwise
    """
    if not isinstance(created_at, datetime):
        return True
    
    elapsed = (datetime.now(timezone.utc) - created_at).total_seconds()
    return elapsed > ttl_seconds


def safe_get(data: dict, key: str, default=None, type_=None):
    """
    Safely get value from dictionary with type conversion.
    
    Args:
        data: Dictionary to get from
        key: Key to retrieve
        default: Default value if key not found
        type_: Optional type to convert to
    
    Returns:
        Value from dictionary or default
    """
    if not isinstance(data, dict):
        return default
    
    value = data.get(key, default)
    
    if type_ and value is not None:
        try:
            return type_(value)
        except (ValueError, TypeError):
            return default
    
    return value


def log_error(error: Exception, context: Optional[str] = None) -> None:
    """Log error with optional context."""
    if context:
        logger.error(f"{context}: {str(error)}", exc_info=True)
    else:
        logger.error(f"Error: {str(error)}", exc_info=True)


def log_info(message: str, **kwargs) -> None:
    """Log info message with optional keyword arguments."""
    if kwargs:
        message = f"{message} | {kwargs}"
    logger.info(message)
