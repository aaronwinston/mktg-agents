from __future__ import annotations

import json
import uuid
from contextvars import ContextVar
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import event, inspect
from sqlalchemy.orm import Session as OrmSession

from models import AuditLog


_current_user_id: ContextVar[Optional[str]] = ContextVar("audit_user_id", default=None)
_current_org_id: ContextVar[Optional[str]] = ContextVar("audit_org_id", default=None)
_current_request_method: ContextVar[Optional[str]] = ContextVar(
    "audit_request_method", default=None
)
_current_request_path: ContextVar[Optional[str]] = ContextVar(
    "audit_request_path", default=None
)


def set_audit_context(
    *,
    user_id: Optional[str],
    org_id: Optional[str],
    request_method: Optional[str] = None,
    request_path: Optional[str] = None,
) -> None:
    _current_user_id.set(user_id)
    _current_org_id.set(org_id)
    _current_request_method.set(request_method)
    _current_request_path.set(request_path)


def clear_audit_context() -> None:
    set_audit_context(user_id=None, org_id=None, request_method=None, request_path=None)


def audit_context() -> dict[str, Optional[str]]:
    return {
        "user_id": _current_user_id.get(),
        "org_id": _current_org_id.get(),
        "request_method": _current_request_method.get(),
        "request_path": _current_request_path.get(),
    }


def _primary_key_as_str(obj: Any) -> Optional[str]:
    try:
        mapper = inspect(obj).mapper
        values = [getattr(obj, col.key, None) for col in mapper.primary_key]
        if not values or all(v is None for v in values):
            return None
        if len(values) == 1:
            return str(values[0])
        return json.dumps([str(v) for v in values])
    except Exception:
        return None


def _safe_json(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def _snapshot_all_columns(obj: Any) -> dict[str, Any]:
    state = inspect(obj)
    out: dict[str, Any] = {}
    for attr in state.mapper.column_attrs:
        key = attr.key
        try:
            out[key] = _safe_json(getattr(obj, key))
        except Exception:
            out[key] = None
    return out


def _diff_changed_columns(obj: Any) -> tuple[dict[str, Any], dict[str, Any]]:
    state = inspect(obj)
    old: dict[str, Any] = {}
    new: dict[str, Any] = {}

    for attr in state.mapper.column_attrs:
        key = attr.key
        hist = state.attrs[key].history
        if not hist.has_changes():
            continue

        old_val = hist.deleted[0] if hist.deleted else None
        new_val = hist.added[0] if hist.added else getattr(obj, key, None)
        old[key] = _safe_json(old_val)
        new[key] = _safe_json(new_val)

    return old, new


@event.listens_for(OrmSession, "before_flush")
def _collect_audit_entries(session: OrmSession, flush_context, instances) -> None:  # noqa: ANN001
    ctx = audit_context()
    org_id = ctx["org_id"]
    if not org_id:
        return

    entries: list[dict[str, Any]] = []

    def add_entry(operation: str, obj: Any, old_values: Any, new_values: Any):
        table_name = getattr(obj, "__tablename__", obj.__class__.__name__.lower())
        if table_name == AuditLog.__tablename__:
            return

        record_id = _primary_key_as_str(obj)

        entries.append(
            {
                "id": str(uuid.uuid4()),
                "organization_id": org_id,
                "user_id": ctx["user_id"],
                "operation": operation,
                "table_name": table_name,
                "record_id": record_id,
                "old_values_json": json.dumps(old_values) if old_values is not None else None,
                "new_values_json": json.dumps(new_values) if new_values is not None else None,
                "request_method": ctx["request_method"],
                "request_path": ctx["request_path"],
                "created_at": datetime.utcnow(),
            }
        )

    for obj in session.new:
        add_entry("CREATE", obj, old_values=None, new_values=_snapshot_all_columns(obj))

    for obj in session.dirty:
        if session.is_modified(obj, include_collections=False):
            old, new = _diff_changed_columns(obj)
            if old or new:
                add_entry("UPDATE", obj, old_values=old, new_values=new)

    for obj in session.deleted:
        add_entry("DELETE", obj, old_values=_snapshot_all_columns(obj), new_values=None)

    if entries:
        session.info.setdefault("_audit_entries", []).extend(entries)


@event.listens_for(OrmSession, "after_flush_postexec")
def _persist_audit_entries(session: OrmSession, flush_context) -> None:  # noqa: ANN001
    entries = session.info.pop("_audit_entries", None)
    if not entries:
        return

    session.connection().execute(AuditLog.__table__.insert(), entries)


def log_change(
    *,
    session: OrmSession,
    organization_id: str,
    user_id: Optional[str],
    operation: str,
    table_name: str,
    record_id: Optional[str] = None,
    old_values: Optional[dict[str, Any]] = None,
    new_values: Optional[dict[str, Any]] = None,
    request_method: Optional[str] = None,
    request_path: Optional[str] = None,
) -> AuditLog:
    """Helper for routers/services to explicitly write an audit log entry."""

    entry = AuditLog(
        organization_id=organization_id,
        user_id=user_id,
        operation=operation,
        table_name=table_name,
        record_id=record_id,
        old_values_json=json.dumps(old_values) if old_values is not None else None,
        new_values_json=json.dumps(new_values) if new_values is not None else None,
        request_method=request_method,
        request_path=request_path,
    )
    session.add(entry)
    return entry
