"""Usage tracking and billing calculations."""

from datetime import datetime, timedelta
from sqlmodel import Session, select, func
from models import UsageEvent, Organization
from typing import Optional, Dict

class UsageTracker:
    """Track API usage for billing purposes."""
    
    @staticmethod
    def record_usage(
        session: Session,
        organization_id: int,
        event_type: str,
        metadata: Dict = None,
        cost_cents: int = 0,
    ) -> UsageEvent:
        """Record a usage event."""
        event = UsageEvent(
            organization_id=organization_id,
            event_type=event_type,
            metadata=metadata or {},
            cost_cents=cost_cents,
            recorded_at=datetime.utcnow(),
        )
        session.add(event)
        session.commit()
        return event
    
    @staticmethod
    def get_current_month_usage(
        session: Session,
        organization_id: int,
    ) -> Dict:
        """Get usage stats for current calendar month."""
        now = datetime.utcnow()
        month_start = datetime(now.year, now.month, 1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
        
        events = session.exec(
            select(UsageEvent).where(
                (UsageEvent.organization_id == organization_id) &
                (UsageEvent.recorded_at >= month_start) &
                (UsageEvent.recorded_at <= month_end)
            )
        ).all()
        
        total_cost = sum(e.cost_cents for e in events)
        
        # Group by event type
        by_type = {}
        for event in events:
            if event.event_type not in by_type:
                by_type[event.event_type] = {"count": 0, "cost_cents": 0}
            by_type[event.event_type]["count"] += 1
            by_type[event.event_type]["cost_cents"] += event.cost_cents
        
        return {
            "period": f"{month_start.strftime('%Y-%m')}: month",
            "total_cost_cents": total_cost,
            "total_cost_usd": total_cost / 100.0,
            "events_by_type": by_type,
        }
    
    @staticmethod
    def estimate_token_cost(
        input_tokens: int,
        output_tokens: int,
        model: str = "claude-3-haiku",
    ) -> int:
        """
        Estimate cost in cents for token usage.
        Uses standard Claude pricing (can be overridden per runtime).
        """
        # Claude 3 pricing (as of April 2024)
        pricing = {
            "claude-3-opus": {"input": 0.015, "output": 0.075},      # $0.015/$0.075 per 1k
            "claude-3-sonnet": {"input": 0.003, "output": 0.015},    # $0.003/$0.015 per 1k
            "claude-3-haiku": {"input": 0.00025, "output": 0.00125}, # $0.00025/$0.00125 per 1k
        }
        
        model_pricing = pricing.get(model, pricing["claude-3-haiku"])
        
        input_cost = (input_tokens / 1000.0) * model_pricing["input"] * 100  # Convert to cents
        output_cost = (output_tokens / 1000.0) * model_pricing["output"] * 100
        
        return int(input_cost + output_cost)
