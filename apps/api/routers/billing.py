"""Billing and Stripe webhook handlers."""

from fastapi import APIRouter, Request, HTTPException, Depends
from sqlmodel import Session, select
from database import get_session
from models import Organization
from config import settings
from datetime import datetime
import stripe
import json

router = APIRouter(prefix="/api/billing", tags=["billing"])

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY if hasattr(settings, 'STRIPE_SECRET_KEY') else None

@router.post("/webhook")
async def stripe_webhook(request: Request, session: Session = Depends(get_session)):
    """Handle Stripe webhook events."""
    
    if not stripe.api_key:
        raise HTTPException(status_code=500, detail="Stripe not configured")
    
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET if hasattr(settings, 'STRIPE_WEBHOOK_SECRET') else None
    if not webhook_secret:
        raise HTTPException(status_code=500, detail="Webhook secret not configured")
    
    # Get raw body
    body = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    if not sig_header:
        raise HTTPException(status_code=400, detail="Missing stripe-signature header")
    
    try:
        event = stripe.Webhook.construct_event(body, sig_header, webhook_secret)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    event_type = event.get('type')
    data = event.get('data', {}).get('object', {})
    
    # Handle subscription events
    if event_type == 'customer.subscription.created':
        stripe_customer_id = data.get('customer')
        stripe_subscription_id = data.get('id')
        
        org = session.exec(
            select(Organization).where(
                Organization.stripe_customer_id == stripe_customer_id
            )
        ).first()
        
        if org:
            org.stripe_subscription_id = stripe_subscription_id
            org.subscription_status = 'active'
            org.current_period_end = datetime.fromtimestamp(data.get('current_period_end', 0))
            session.add(org)
            session.commit()
    
    elif event_type == 'customer.subscription.updated':
        stripe_subscription_id = data.get('id')
        
        org = session.exec(
            select(Organization).where(
                Organization.stripe_subscription_id == stripe_subscription_id
            )
        ).first()
        
        if org:
            status = data.get('status')
            org.subscription_status = status
            org.current_period_end = datetime.fromtimestamp(data.get('current_period_end', 0))
            session.add(org)
            session.commit()
    
    elif event_type == 'customer.subscription.deleted':
        stripe_subscription_id = data.get('id')
        
        org = session.exec(
            select(Organization).where(
                Organization.stripe_subscription_id == stripe_subscription_id
            )
        ).first()
        
        if org:
            org.plan = 'free'
            org.subscription_status = 'canceled'
            org.stripe_subscription_id = None
            session.add(org)
            session.commit()
    
    elif event_type == 'invoice.payment_failed':
        stripe_subscription_id = data.get('subscription')
        
        org = session.exec(
            select(Organization).where(
                Organization.stripe_subscription_id == stripe_subscription_id
            )
        ).first()
        
        if org:
            org.subscription_status = 'past_due'
            session.add(org)
            session.commit()
    
    return {"status": "received"}

@router.get("/checkout-session/{session_id}")
async def get_checkout_session(session_id: str):
    """Get Stripe checkout session status."""
    
    if not stripe.api_key:
        raise HTTPException(status_code=500, detail="Stripe not configured")
    
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        return {
            "id": session.id,
            "status": session.payment_status,
            "customer_id": session.customer,
        }
    except stripe.error.InvalidRequestError:
        raise HTTPException(status_code=404, detail="Session not found")
