"""Google Trends polling service using pytrends."""

import json
import logging
from datetime import datetime
from typing import Optional
import asyncio

from pytrends.request import TrendReq
from sqlmodel import Session, select

from database import engine
from models import KeywordCluster, Organization, TrendsData

logger = logging.getLogger(__name__)

# Default keyword clusters if none configured
DEFAULT_KEYWORDS = [
    "agent observability",
    "LLM evaluation",
    "AI tracing",
    "agent harness",
    "Phoenix Arize",
    "production AI agents",
]


def _default_org_id(session: Session) -> str:
    org = session.exec(select(Organization).order_by(Organization.created_at)).first()
    # schema migration guarantees at least one org exists
    return org.id


async def poll_trends(
    keywords: Optional[list[str]] = None,
    region: str = "US",
    organization_id: Optional[str] = None,
):
    """Poll Google Trends for keyword clusters."""
    if keywords is None:
        keywords = DEFAULT_KEYWORDS

    results = []
    errors = []
    pytrends = TrendReq(hl="en-US", tz=360)

    for keyword in keywords:
        try:
            logger.info(f"Polling trends for: {keyword}")

            pytrends.build_payload([keyword], timeframe="today 1-m", geo="")
            interest_over_time = pytrends.interest_over_time()
            related_queries = pytrends.related_queries()

            interest_json = (
                interest_over_time.to_json()
                if interest_over_time is not None and len(interest_over_time) > 0
                else "{}"
            )
            related_json = json.dumps(related_queries) if related_queries else "{}"

            with Session(engine) as session:
                try:
                    org_id = organization_id or _default_org_id(session)
                    existing = session.exec(
                        select(TrendsData).where(
                            (TrendsData.organization_id == org_id)
                            & (TrendsData.keyword == keyword)
                            & (TrendsData.region == region)
                        )
                    ).first()

                    if existing:
                        existing.interest_over_time_json = interest_json
                        existing.related_queries_json = related_json
                        existing.fetched_at = datetime.utcnow()
                        session.add(existing)
                        logger.debug(f"Updated trends data for {keyword}")
                    else:
                        trends_data = TrendsData(
                            organization_id=org_id,
                            keyword=keyword,
                            region=region,
                            interest_over_time_json=interest_json,
                            related_queries_json=related_json,
                        )
                        session.add(trends_data)
                        logger.debug(f"Created new trends data for {keyword}")

                    session.commit()
                    results.append(keyword)
                except Exception as db_err:
                    session.rollback()
                    logger.error(f"Database error for '{keyword}': {str(db_err)}")
                    errors.append((keyword, str(db_err)))

            await asyncio.sleep(1)

        except Exception as e:
            logger.error(f"Failed to poll trends for '{keyword}': {str(e)}", exc_info=True)
            errors.append((keyword, str(e)))

    logger.info(
        f"Trends poll complete: {len(results)} keywords processed, {len(errors)} errors"
    )
    if errors:
        logger.warning(f"Trends poll errors: {errors}")
    return results


async def get_configured_keywords(
    organization_id: Optional[str] = None,
) -> list[str]:
    """Fetch configured keywords from KeywordCluster table."""
    with Session(engine) as session:
        org_id = organization_id or _default_org_id(session)
        clusters = session.exec(
            select(KeywordCluster)
            .where((KeywordCluster.organization_id == org_id) & (KeywordCluster.active == True))  # noqa: E712
            .order_by(KeywordCluster.created_at.desc())
        ).all()
        return [c.keyword for c in clusters] if clusters else DEFAULT_KEYWORDS
