from __future__ import annotations

import json
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from database import get_session
from middleware.auth import AuthContext, require_org_admin
from models import AuditLog


router = APIRouter(prefix="/api", tags=["audit"])


@router.get("/audit-log")
def list_audit_logs(
    auth: AuthContext = Depends(require_org_admin),
    session: Session = Depends(get_session),
    table_name: Optional[str] = None,
    record_id: Optional[str] = None,
    operation: Optional[str] = None,
    user_id: Optional[str] = None,
    since: Optional[datetime] = None,
    limit: int = 100,
    offset: int = 0,
):
    q = select(AuditLog).where(AuditLog.organization_id == auth.org_id)

    if table_name:
        q = q.where(AuditLog.table_name == table_name)
    if record_id:
        q = q.where(AuditLog.record_id == record_id)
    if operation:
        q = q.where(AuditLog.operation == operation)
    if user_id:
        q = q.where(AuditLog.user_id == user_id)
    if since:
        q = q.where(AuditLog.created_at >= since)

    rows = session.exec(
        q.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit)
    ).all()

    def decode(s: Optional[str]):
        if not s:
            return None
        try:
            return json.loads(s)
        except Exception:
            return None

    return [
        {
            "id": r.id,
            "created_at": str(r.created_at),
            "user_id": r.user_id,
            "org_id": r.organization_id,
            "operation": r.operation,
            "table_name": r.table_name,
            "record_id": r.record_id,
            "request_method": r.request_method,
            "request_path": r.request_path,
            "old": decode(r.old_values_json),
            "new": decode(r.new_values_json),
        }
        for r in rows
    ]
