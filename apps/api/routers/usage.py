"""Usage tracking endpoints."""

from fastapi import APIRouter, Depends
from sqlmodel import Session
from database import get_session
from middleware.auth import get_current_user, AuthContext
from services.usage import UsageTracker

router = APIRouter(prefix="/api/usage", tags=["usage"])

@router.get("/current-month")
async def get_current_month_usage(
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get usage stats for current calendar month."""
    usage = UsageTracker.get_current_month_usage(session, auth.org_id)
    return usage

@router.get("/summary")
async def get_usage_summary(
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get brief usage summary."""
    usage = UsageTracker.get_current_month_usage(session, auth.org_id)
    return {
        "total_cost_usd": usage["total_cost_usd"],
        "event_count": sum(v.get("count", 0) for v in usage["events_by_type"].values()),
    }
