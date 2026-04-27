"""
Query optimization utilities for SQLModel/SQLAlchemy (P4.1).

Provides helpers for:
- Eager loading relationships with selectinload/joinedload
- Selecting specific columns instead of SELECT *
- Cursor-based and offset/limit pagination
- Query result caching (Redis)
"""

import json
import hashlib
import logging
from typing import Optional, List, Any, Type, TypeVar
from functools import wraps

from sqlmodel import Session, select, SQLModel
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.sql import Select

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=SQLModel)


class PaginationParams:
    """Pagination parameters for list endpoints."""
    
    def __init__(self, skip: int = 0, limit: int = 20, max_limit: int = 100):
        """
        Initialize pagination.
        
        Args:
            skip: Number of items to skip (offset)
            limit: Number of items to return
            max_limit: Maximum allowed limit (capped at this value)
        """
        self.skip = max(0, skip)
        self.limit = min(max(1, limit), max_limit)
        self.max_limit = max_limit
    
    def apply(self, query: Select) -> Select:
        """Apply pagination to a SQLAlchemy select statement."""
        return query.offset(self.skip).limit(self.limit)


class CursorPaginationParams:
    """Cursor-based pagination for efficient scrolling."""
    
    def __init__(self, cursor: Optional[str] = None, limit: int = 20, max_limit: int = 100):
        """
        Initialize cursor pagination.
        
        Args:
            cursor: Base64-encoded cursor (typically an ID or timestamp)
            limit: Number of items to return
            max_limit: Maximum allowed limit
        """
        self.cursor = cursor
        self.limit = min(max(1, limit), max_limit)
        self.max_limit = max_limit
    
    def decode_cursor(self) -> Optional[Any]:
        """Decode cursor value. Override in subclasses for custom decoding."""
        if not self.cursor:
            return None
        try:
            import base64
            return base64.b64decode(self.cursor.encode()).decode()
        except Exception as e:
            logger.warning(f"Failed to decode cursor: {e}")
            return None
    
    def encode_cursor(self, value: Any) -> str:
        """Encode cursor value."""
        import base64
        return base64.b64encode(str(value).encode()).decode()


def apply_eager_loading(
    query: Select,
    model: Type[T],
    relationships: List[str],
) -> Select:
    """
    Apply eager loading to a query for specified relationships.
    
    This prevents N+1 queries by loading related objects in the same query.
    
    Args:
        query: SQLAlchemy select statement
        model: SQLModel class
        relationships: List of relationship attribute names to eager load
    
    Returns:
        Modified select statement with eager loading applied
    
    Example:
        query = select(Project)
        query = apply_eager_loading(query, Project, ["folders", "briefs"])
    """
    for rel in relationships:
        if hasattr(model, rel):
            # Use selectinload for better performance with many-to-many
            query = query.options(selectinload(getattr(model, rel)))
    
    return query


def select_columns(
    model: Type[T],
    columns: List[str],
) -> Select:
    """
    Create a select statement that only fetches specific columns.
    
    This reduces memory usage and network overhead for list endpoints.
    
    Args:
        model: SQLModel class
        columns: List of column names to select
    
    Returns:
        SQLAlchemy select statement
    
    Example:
        query = select_columns(Project, ["id", "name", "created_at"])
        projects = session.exec(query).all()
    """
    # Get model's column objects
    selected_cols = [getattr(model, col) for col in columns if hasattr(model, col)]
    
    if not selected_cols:
        logger.warning(f"No valid columns found for {model.__name__}: {columns}")
        return select(model)
    
    return select(*selected_cols)


def add_pagination(
    query: Select,
    pagination: PaginationParams,
) -> Select:
    """
    Apply offset/limit pagination to a query.
    
    Args:
        query: SQLAlchemy select statement
        pagination: PaginationParams instance
    
    Returns:
        Modified select statement with pagination applied
    """
    return pagination.apply(query)


def cache_key_for_query(
    endpoint: str,
    user_id: str,
    org_id: str,
    filters: Optional[dict] = None,
) -> str:
    """
    Generate a cache key for a query based on endpoint, user, org, and filters.
    
    Args:
        endpoint: API endpoint name (e.g., "list_projects")
        user_id: User ID
        org_id: Organization ID
        filters: Optional dictionary of filter parameters
    
    Returns:
        SHA256 hash suitable for use as a Redis key
    """
    key_data = {
        "endpoint": endpoint,
        "user_id": user_id,
        "org_id": org_id,
        "filters": filters or {},
    }
    key_str = json.dumps(key_data, sort_keys=True)
    return hashlib.sha256(key_str.encode()).hexdigest()


def cached_query(
    cache_ttl_seconds: int = 3600,
    cache_enabled: bool = True,
):
    """
    Decorator to cache query results in Redis.
    
    Usage:
        @cached_query(cache_ttl_seconds=3600)
        def get_user_projects(user_id: str, session: Session):
            return session.exec(select(Project).where(...)).all()
    
    Args:
        cache_ttl_seconds: Time-to-live for cached results
        cache_enabled: Whether caching is enabled
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not cache_enabled:
                return func(*args, **kwargs)
            
            try:
                import redis
                from config import settings
                
                # Generate cache key from function name and args
                cache_key = f"query:{func.__name__}:{hash(str(args) + str(kwargs))}"
                
                # Try to get from cache
                client = redis.from_url(settings.REDIS_URL)
                cached = client.get(cache_key)
                
                if cached:
                    logger.debug(f"Cache hit: {cache_key}")
                    return json.loads(cached)
                
                # Execute function and cache result
                result = func(*args, **kwargs)
                
                # Serialize result (convert SQLModel instances to dicts)
                try:
                    serialized = json.dumps(result, default=str)
                    client.setex(cache_key, cache_ttl_seconds, serialized)
                    logger.debug(f"Cache miss: {cache_key} - cached for {cache_ttl_seconds}s")
                except Exception as e:
                    logger.warning(f"Failed to cache query result: {e}")
                
                return result
            
            except Exception as e:
                logger.warning(f"Query caching failed (non-fatal): {e}")
                return func(*args, **kwargs)
        
        return wrapper
    return decorator


def optimize_list_query(
    session: Session,
    model: Type[T],
    org_id: str,
    skip: int = 0,
    limit: int = 20,
    relationships: Optional[List[str]] = None,
    order_by_field: Optional[Any] = None,
) -> List[T]:
    """
    Optimized list query with pagination, eager loading, and ordering.
    
    This is the recommended pattern for list endpoints.
    
    Args:
        session: SQLModel session
        model: SQLModel class
        org_id: Organization ID for filtering
        skip: Pagination offset
        limit: Pagination limit
        relationships: List of relationship attributes to eager load
        order_by_field: Field to order by (e.g., Project.created_at)
    
    Returns:
        List of model instances
    
    Example:
        projects = optimize_list_query(
            session,
            Project,
            auth.org_id,
            skip=0,
            limit=20,
            relationships=["folders"],
            order_by_field=Project.created_at.desc()
        )
    """
    # Start with base query filtered by org
    query = select(model).where(model.organization_id == org_id)
    
    # Apply eager loading for relationships
    if relationships:
        query = apply_eager_loading(query, model, relationships)
    
    # Apply ordering
    if order_by_field is not None:
        query = query.order_by(order_by_field)
    
    # Apply pagination
    pagination = PaginationParams(skip=skip, limit=limit)
    query = add_pagination(query, pagination)
    
    return session.exec(query).all()


def count_items(
    session: Session,
    model: Type[T],
    org_id: str,
) -> int:
    """
    Count total items for pagination metadata.
    
    Args:
        session: SQLModel session
        model: SQLModel class
        org_id: Organization ID
    
    Returns:
        Total count
    """
    from sqlalchemy import func
    
    query = select(func.count(model.id)).where(model.organization_id == org_id)
    return session.exec(query).scalar() or 0
