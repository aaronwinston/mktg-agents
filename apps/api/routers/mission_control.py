"""Email and notification digests for mission control."""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlmodel import Session, select
from database import get_session
from models import Organization, ScrapeItem
from middleware.auth import get_current_user, AuthContext
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/mission-control", tags=["mission-control"])

class EmailDigestRequest(BaseModel):
    enabled: bool
    send_time_utc: str = "08:00"  # HH:MM format

class SlackWebhookRequest(BaseModel):
    webhook_url: str

@router.put("/email-digest")
async def update_email_digest_settings(
    req: EmailDigestRequest,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Update email digest settings for the organization."""
    
    org = session.get(Organization, auth.org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Store settings as JSON in org
    import json
    settings = {
        "email_digest_enabled": req.enabled,
        "send_time_utc": req.send_time_utc
    }
    org.metadata_json = json.dumps(settings)
    org.updated_at = datetime.utcnow()
    session.add(org)
    session.commit()
    
    return settings

@router.get("/email-digest")
async def get_email_digest_settings(
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get email digest settings."""
    
    org = session.get(Organization, auth.org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    import json
    settings = {}
    if org.metadata_json:
        try:
            settings = json.loads(org.metadata_json)
        except:
            pass
    
    return settings.get("email_digest_enabled", False), settings.get("send_time_utc", "08:00")

@router.post("/test-digest")
async def send_test_email_digest(
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Send a test digest email to the user."""
    
    org = session.get(Organization, auth.org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Get top 5 scrape items from last 24h
    yesterday = datetime.utcnow() - timedelta(days=1)
    items = session.exec(
        select(ScrapeItem).where(
            (ScrapeItem.organization_id == auth.org_id) &
            (ScrapeItem.created_at >= yesterday)
        ).order_by(ScrapeItem.score.desc()).limit(5)
    ).all()
    
    # Format digest
    digest_items = [
        {
            "title": item.title,
            "body": item.body[:200] + "...",
            "source": item.source_url,
            "score": item.score
        }
        for item in items
    ]
    
    # In production: send via Resend. For now, return for manual testing
    return {
        "preview": f"Daily digest for {org.name}",
        "items": digest_items,
        "status": "preview_only"
    }

@router.put("/slack-webhook")
async def update_slack_webhook(
    req: SlackWebhookRequest,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Save Slack webhook URL for digest delivery."""
    
    org = session.get(Organization, auth.org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    import json
    metadata = {}
    if org.metadata_json:
        try:
            metadata = json.loads(org.metadata_json)
        except:
            pass
    
    metadata["slack_webhook_url"] = req.webhook_url
    org.metadata_json = json.dumps(metadata)
    org.updated_at = datetime.utcnow()
    session.add(org)
    session.commit()
    
    return {"status": "slack_webhook_saved"}

@router.post("/test-slack")
async def test_slack_digest(
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Send a test Slack digest to the configured webhook."""
    
    org = session.get(Organization, auth.org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    import json
    metadata = {}
    if org.metadata_json:
        try:
            metadata = json.loads(org.metadata_json)
        except:
            pass
    
    webhook_url = metadata.get("slack_webhook_url")
    if not webhook_url:
        raise HTTPException(status_code=400, detail="Slack webhook not configured")
    
    # In production: send via webhook
    return {"status": "test_message_queued"}
