from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlmodel import Session, select
from database import get_session
from models import ScrapeItem, SearchInsight, KeywordCluster
from middleware.auth import get_current_user, AuthContext
from services.scraping import run_all_scrapers, DEFAULT_SUBREDDITS, GITHUB_TOPICS, ARXIV_FEEDS, DEFAULT_RSS_FEEDS
from services.scoring import score_items_batch, synthesize_items_batch
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class KeywordClusterInput(BaseModel):
    keyword: str
    region: str = "US"

class KeywordClusterUpdate(BaseModel):
    active: Optional[bool] = None
    keyword: Optional[str] = None

router = APIRouter(prefix="/api/intelligence", tags=["intelligence"])

@router.get("/feed")
def get_feed(
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    items = session.exec(
        select(ScrapeItem)
        .where(ScrapeItem.dismissed_at == None)  # noqa: E711
        .where(ScrapeItem.score >= 7)
        .where(ScrapeItem.organization_id == auth.org_id)
        .order_by(ScrapeItem.score.desc())
    ).all()
    return items

@router.get("/items")
def list_items(
    limit: int = 50,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    items = session.exec(
        select(ScrapeItem)
        .where(ScrapeItem.dismissed_at == None)  # noqa: E711
        .where(ScrapeItem.organization_id == auth.org_id)
        .order_by(ScrapeItem.created_at.desc())
        .limit(limit)
    ).all()
    return items

@router.post("/items/{item_id}/dismiss")
def dismiss_item(
    item_id: int,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    item = session.exec(
        select(ScrapeItem).where(
            (ScrapeItem.id == item_id) & (ScrapeItem.organization_id == auth.org_id)
        )
    ).first()
    if item:
        item.dismissed_at = datetime.utcnow()
        session.add(item)
        session.commit()
    return {"ok": True}

@router.post("/items/{item_id}/use-as-context")
def use_as_context(
    item_id: int,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    item = session.exec(
        select(ScrapeItem).where(
            (ScrapeItem.id == item_id) & (ScrapeItem.organization_id == auth.org_id)
        )
    ).first()
    if item:
        item.surfaced_to_user_at = datetime.utcnow()
        session.add(item)
        session.commit()
    return {"ok": True, "item_id": item_id}

@router.post("/scrape")
async def trigger_scrape(background_tasks: BackgroundTasks, session: Session = Depends(get_session)):
    session_bind = session.bind

    async def run():
        items = await run_all_scrapers()
        scored = score_items_batch(items)
        synthesized = synthesize_items_batch(scored)
        with Session(session_bind) as s:
            from models import Organization

            default_org = s.exec(select(Organization).order_by(Organization.created_at)).first()
            for item_data in synthesized:
                existing = s.exec(
                    select(ScrapeItem)
                    .where(ScrapeItem.organization_id == default_org.id)
                    .where(ScrapeItem.source_url == item_data.get("source_url", ""))
                ).first()
                if not existing and item_data.get("source_url"):
                    payload = {k: v for k, v in item_data.items() if k in ScrapeItem.__fields__}
                    payload.setdefault("organization_id", default_org.id)
                    item = ScrapeItem(**payload)
                    s.add(item)
            s.commit()

    background_tasks.add_task(run)
    return {"ok": True, "message": "Scrape started in background"}

@router.get("/config")
def get_config():
    return {
        "hn_keywords": ["LLM observability", "AI agents", "eval harness", "arize", "phoenix"],
        "hn_min_points": 50,
        "subreddits": ["MachineLearning", "LocalLLaMA", "programming", "LangChain", "AI_Agents"],
        "github_topics": ["ai", "llm", "agents", "observability", "llm-evaluation"],
        "rss_feeds": [
            "https://www.anthropic.com/rss.xml",
            "https://simonwillison.net/atom/everything/",
            "https://www.latent.space/feed",
            "https://arize.com/blog/feed/",
        ],
    }

@router.get("/search/insights")
def get_search_insights(
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get all search insights."""
    insights = session.exec(
        select(SearchInsight)
        .where(SearchInsight.organization_id == auth.org_id)
        .order_by(SearchInsight.generated_at.desc())
        .limit(100)
    ).all()
    return insights

@router.get("/search/keywords")
def get_keyword_clusters(
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get all active keyword clusters."""
    clusters = session.exec(
        select(KeywordCluster)
        .where(KeywordCluster.active == True)  # noqa: E712
        .where(KeywordCluster.organization_id == auth.org_id)
        .order_by(KeywordCluster.created_at.desc())
    ).all()
    return clusters

@router.post("/search/keywords")
def add_keyword_cluster(
    data: KeywordClusterInput,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Add a new keyword cluster."""
    existing = session.exec(
        select(KeywordCluster)
        .where(KeywordCluster.keyword == data.keyword)
        .where(KeywordCluster.region == data.region)
        .where(KeywordCluster.organization_id == auth.org_id)
    ).first()
    if existing:
        return {"error": f"Keyword '{data.keyword}' already exists for region {data.region}"}
    
    cluster = KeywordCluster(
        keyword=data.keyword,
        region=data.region,
        organization_id=auth.org_id,
        active=True
    )
    session.add(cluster)
    session.commit()
    session.refresh(cluster)
    return cluster

@router.put("/search/keywords/{cluster_id}")
def update_keyword_cluster(
    cluster_id: int,
    data: KeywordClusterUpdate,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Update a keyword cluster."""
    cluster = session.exec(
        select(KeywordCluster).where(
            (KeywordCluster.id == cluster_id) & (KeywordCluster.organization_id == auth.org_id)
        )
    ).first()
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    
    if data.active is not None:
        cluster.active = data.active
    if data.keyword is not None:
        cluster.keyword = data.keyword
    cluster.updated_at = datetime.utcnow()
    
    session.add(cluster)
    session.commit()
    session.refresh(cluster)
    return cluster

@router.delete("/search/keywords/{cluster_id}")
def delete_keyword_cluster(
    cluster_id: int,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Delete a keyword cluster."""
    cluster = session.exec(
        select(KeywordCluster).where(
            (KeywordCluster.id == cluster_id) & (KeywordCluster.organization_id == auth.org_id)
        )
    ).first()
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    
    session.delete(cluster)
    session.commit()
    return {"ok": True}

