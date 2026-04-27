"""Google Search Console integration service."""

import logging
from datetime import datetime, timedelta
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from sqlmodel import Session, select

from config import settings
from database import engine
from models import CalendarIntegration, GscQuery, Organization

logger = logging.getLogger(__name__)

GSC_SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]


def _default_org_id(session: Session) -> str:
    org = session.exec(select(Organization).order_by(Organization.created_at)).first()
    return org.id


class GSCService:
    """Google Search Console API client with automatic token refresh."""

    def __init__(self, access_token: str, refresh_token: str, gsc_property: str):
        self.gsc_property = gsc_property
        self.refresh_token = refresh_token
        self.credentials = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_OAUTH_CLIENT_ID,
            client_secret=settings.GOOGLE_OAUTH_CLIENT_SECRET,
            scopes=GSC_SCOPES,
        )
        if self.credentials.expired and self.refresh_token:
            request = Request()
            self.credentials.refresh(request)
            logger.info("GSC credentials refreshed")

        self.service = build("webmasters", "v3", credentials=self.credentials)

    def get_performance_data(self, days_back: int = 28) -> list[dict]:
        try:
            if self.credentials.expired and self.refresh_token:
                request = Request()
                self.credentials.refresh(request)

            end_date = datetime.utcnow().date()
            start_date = end_date - timedelta(days=days_back)

            request_body = {
                "startDate": start_date.isoformat(),
                "endDate": end_date.isoformat(),
                "dimensions": ["query", "page"],
                "rowLimit": 25000,
            }

            response = self.service.searchanalytics().query(
                siteUrl=self.gsc_property, body=request_body
            ).execute()

            rows = response.get("rows", [])
            logger.info(f"Fetched {len(rows)} GSC rows for {self.gsc_property}")

            results = []
            for row in rows:
                results.append(
                    {
                        "query": row["keys"][0],
                        "page": row["keys"][1],
                        "clicks": int(row.get("clicks", 0)),
                        "impressions": int(row.get("impressions", 0)),
                        "ctr": float(row.get("ctr", 0)),
                        "position": float(row.get("position", 0)),
                        "date_range_start": start_date.isoformat(),
                        "date_range_end": end_date.isoformat(),
                    }
                )

            return results

        except Exception as e:
            logger.error(f"GSC API error for {self.gsc_property}: {str(e)}")
            return []


async def pull_gsc_data(
    user_id: str = "system",
    gsc_property: Optional[str] = None,
    organization_id: Optional[str] = None,
) -> dict:
    """Pull GSC data and store in database."""
    with Session(engine) as session:
        org_id = organization_id or _default_org_id(session)
        oauth = session.exec(
            select(CalendarIntegration).where(CalendarIntegration.organization_id == org_id)
        ).first()

        if not oauth:
            logger.warning(f"No OAuth token found for org {org_id}; skipping GSC pull")
            return {"status": "skipped", "reason": "No OAuth token"}

        if oauth.is_token_expired():
            logger.info(f"OAuth token expired for org {org_id}, refreshing...")
            if not oauth.refresh_if_needed():
                logger.error(f"Failed to refresh OAuth token for org {org_id}")
                return {"status": "skipped", "reason": "Token refresh failed"}
            session.add(oauth)
            session.commit()

        access_token = oauth.access_token
        refresh_token = oauth.refresh_token

        if not access_token or not refresh_token:
            logger.warning(f"OAuth token incomplete for org {org_id}")
            return {"status": "skipped", "reason": "Token incomplete"}

        property_url = gsc_property or oauth.calendar_id or "sc-domain:arize.com"

    try:
        logger.info(f"Pulling GSC data for property: {property_url}")
        gsc = GSCService(access_token, refresh_token, property_url)
        rows = gsc.get_performance_data(days_back=28)

        if not rows:
            return {"status": "success", "rows_fetched": 0}

        inserted_count = 0
        updated_count = 0

        with Session(engine) as session:
            org_id = organization_id or _default_org_id(session)
            try:
                for row_data in rows:
                    existing = session.exec(
                        select(GscQuery).where(
                            (GscQuery.organization_id == org_id)
                            & (GscQuery.user_id == user_id)
                            & (GscQuery.query == row_data["query"])
                            & (GscQuery.page == row_data["page"])
                            & (GscQuery.date_range_start == row_data["date_range_start"])
                        )
                    ).first()

                    row_data["user_id"] = user_id
                    row_data["organization_id"] = org_id

                    if existing:
                        for key, value in row_data.items():
                            if key != "user_id":
                                setattr(existing, key, value)
                        session.add(existing)
                        updated_count += 1
                    else:
                        session.add(GscQuery(**row_data))
                        inserted_count += 1

                session.commit()
            except Exception as db_err:
                session.rollback()
                logger.error(
                    f"Database error during GSC upsert: {str(db_err)}", exc_info=True
                )
                return {"status": "error", "error": f"Database error: {str(db_err)}"}

        return {
            "status": "success",
            "rows_fetched": len(rows),
            "inserted": inserted_count,
            "updated": updated_count,
        }

    except Exception as e:
        logger.error(f"GSC pull failed: {str(e)}", exc_info=True)
        return {"status": "error", "error": str(e)}
