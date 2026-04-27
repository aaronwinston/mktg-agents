"""Cross-reference LLM pass: extract keywords from top scrape items and join with GSC/Trends data."""

import json
import logging
from datetime import datetime, timedelta
from typing import Optional

from anthropic import Anthropic
from sqlmodel import Session, select

from config import settings
from database import engine
from models import GscQuery, Organization, ScrapeItem, SearchInsight, TrendsData

logger = logging.getLogger(__name__)

client = Anthropic()


def _default_org_id(session: Session) -> str:
    org = session.exec(select(Organization).order_by(Organization.created_at)).first()
    return org.id


async def cross_reference_lm_pass(
    user_id: str = "system",
    organization_id: Optional[str] = None,
) -> dict:
    """Daily job that generates SearchInsight rows."""
    try:
        with Session(engine) as session:
            org_id = organization_id or _default_org_id(session)
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            top_items = session.exec(
                select(ScrapeItem)
                .where(
                    (ScrapeItem.organization_id == org_id)
                    & (ScrapeItem.score >= 7)
                    & (ScrapeItem.fetched_at >= cutoff_time)
                )
                .order_by(ScrapeItem.score.desc())
                .limit(30)
            ).all()

            if not top_items:
                logger.info("No high-scored items in last 24h for cross-reference pass")
                return {"status": "success", "insights_created": 0}

            insights_created = 0
            errors = []

            for item in top_items:
                try:
                    keywords = _extract_keywords(item)
                    if not keywords:
                        continue

                    for keyword in keywords:
                        try:
                            insight = _build_insight(
                                item=item,
                                keyword=keyword,
                                session=session,
                                user_id=user_id,
                                organization_id=org_id,
                            )
                            if insight:
                                session.add(insight)
                                insights_created += 1
                        except Exception as keyword_err:
                            logger.warning(
                                f"Failed to build insight for item {item.id}, keyword '{keyword}': {str(keyword_err)}"
                            )
                            errors.append((item.id, keyword, str(keyword_err)))

                except Exception as e:
                    logger.error(
                        f"Failed to process item {item.id}: {str(e)}", exc_info=True
                    )
                    errors.append((item.id, None, str(e)))

            session.commit()
            return {
                "status": "success",
                "insights_created": insights_created,
                "errors": len(errors),
            }

    except Exception as e:
        logger.error(f"Cross-reference pass failed: {str(e)}", exc_info=True)
        return {"status": "error", "error": str(e)}


def _extract_keywords(item: ScrapeItem) -> list[str]:
    """Use Claude to extract 1-3 keyword phrases from item title/body."""
    try:
        text = f"{item.title}\n\n{item.body[:500] if item.body else ''}"

        response = client.messages.create(
            model=settings.MODEL_GENERATION,
            max_tokens=200,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Extract 1-3 key search phrases from this content that could be used in Google Search or Trends queries.\n"
                        "Return as a JSON array of strings, e.g. [\"phrase1\", \"phrase2\"].\n"
                        "Be concise and specific. Phrases should be 2-5 words.\n\n"
                        f"Content:\n{text}"
                    ),
                }
            ],
        )

        result_text = response.content[0].text
        import re

        match = re.search(r"\[.*?\]", result_text, re.DOTALL)
        if match:
            keywords = json.loads(match.group())
            return keywords[:3]
    except Exception as e:
        logger.warning(f"Keyword extraction failed: {str(e)}")

    return []


def _build_insight(
    item: ScrapeItem,
    keyword: str,
    session: Session,
    user_id: str,
    organization_id: str,
) -> Optional[SearchInsight]:
    try:
        gsc_row = session.exec(
            select(GscQuery)
            .where(
                (GscQuery.organization_id == organization_id)
                & (GscQuery.query.ilike(f"%{keyword}%"))
            )
            .order_by(GscQuery.position)
            .limit(1)
        ).first()

        our_position = gsc_row.position if gsc_row else None
        our_clicks = gsc_row.clicks if gsc_row else None

        trends_row = session.exec(
            select(TrendsData)
            .where(
                (TrendsData.organization_id == organization_id)
                & (TrendsData.keyword.ilike(keyword))
            )
            .order_by(TrendsData.fetched_at.desc())
            .limit(1)
        ).first()

        trends_momentum = _assess_trends_momentum(trends_row) if trends_row else "no_data"

        insight_text = _build_insight_text(
            item=item,
            keyword=keyword,
            our_position=our_position,
            our_clicks=our_clicks,
            trends_momentum=trends_momentum,
        )

        return SearchInsight(
            organization_id=organization_id,
            user_id=user_id,
            topic=keyword,
            source_item_ids=str(item.id),
            our_gsc_position=our_position,
            our_gsc_clicks=our_clicks,
            trends_momentum=trends_momentum,
            insight_text=insight_text,
        )

    except Exception as e:
        logger.warning(f"Failed to build insight for {keyword}: {str(e)}")
        return None


def _assess_trends_momentum(trends_row: TrendsData) -> str:
    """Assess if trends data shows rising/steady/falling interest."""
    try:
        if not trends_row or not trends_row.interest_over_time_json:
            return "no_data"

        data = json.loads(trends_row.interest_over_time_json)
        if not data:
            return "no_data"

        values = None
        for key, val in data.items():
            if key != "isPartial" and isinstance(val, dict):
                values = list(val.values())
                break

        if not values or len(values) < 2:
            return "steady"

        values = [float(v) for v in values if isinstance(v, (int, float))]
        if len(values) < 2:
            return "steady"

        third_size = max(1, len(values) // 3)
        first_third = sum(values[:third_size]) / third_size
        last_third = sum(values[-third_size:]) / third_size

        if last_third > first_third * 1.1:
            return "rising"
        if last_third < first_third * 0.9:
            return "falling"
        return "steady"
    except Exception as e:
        logger.warning(f"Trends momentum assessment failed: {str(e)}")
        return "no_data"


def _build_insight_text(
    item: ScrapeItem,
    keyword: str,
    our_position: Optional[float],
    our_clicks: Optional[int],
    trends_momentum: str,
) -> str:
    parts = [f"Content about '{keyword}' from {item.source}."]

    if our_position:
        parts.append(f"We rank at position {int(our_position)} for related queries.")
        if our_clicks:
            parts.append(f"Getting ~{our_clicks} clicks/month.")
    else:
        parts.append("We don't currently rank for this keyword.")

    if trends_momentum == "rising":
        parts.append(f"Interest in '{keyword}' is rising.")
    elif trends_momentum == "falling":
        parts.append(f"Interest in '{keyword}' is declining.")
    elif trends_momentum == "steady":
        parts.append(f"Interest in '{keyword}' is stable.")

    return " ".join(parts)
