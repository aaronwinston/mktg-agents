import asyncio
import re
import json
import time
from fastapi import APIRouter
import httpx
import feedparser
from bs4 import BeautifulSoup
from anthropic import Anthropic
from cache import briefing_cache
from config import settings

router = APIRouter(prefix="/api/briefing", tags=["briefing"])
client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

async def scrape_hackernews(limit=15):
    async with httpx.AsyncClient(timeout=10) as c:
        ids_resp = await c.get("https://hacker-news.firebaseio.com/v0/topstories.json")
        ids = ids_resp.json()[:limit]
        stories = []
        for id_ in ids:
            try:
                item = (await c.get(f"https://hacker-news.firebaseio.com/v0/item/{id_}.json")).json()
                if item and item.get("score", 0) > 50 and item.get("title"):
                    stories.append({
                        "title": item.get("title", ""),
                        "url": item.get("url", f"https://news.ycombinator.com/item?id={id_}"),
                        "score": item.get("score", 0),
                        "source": "HackerNews"
                    })
            except:
                pass
        return stories[:10]

async def scrape_github_trending():
    try:
        async with httpx.AsyncClient(timeout=10, headers={"User-Agent": "Mozilla/5.0"}) as c:
            resp = await c.get("https://github.com/trending")
            soup = BeautifulSoup(resp.text, "lxml")
            repos = []
            for article in soup.select("article.Box-row")[:10]:
                name_el = article.select_one("h2 a")
                desc_el = article.select_one("p")
                stars_el = article.select_one("a[href*='/stargazers']")
                if name_el:
                    href = name_el.get("href", "").strip("/")
                    repos.append({
                        "title": href.replace("/", " / "),
                        "url": f"https://github.com/{href}",
                        "score": stars_el.get_text(strip=True) if stars_el else "N/A",
                        "description": desc_el.get_text(strip=True) if desc_el else "",
                        "source": "GitHub"
                    })
            return repos
    except:
        return []

async def scrape_arxiv():
    try:
        feed = feedparser.parse("http://export.arxiv.org/rss/cs.AI")
        entries = []
        for entry in feed.entries[:10]:
            title = re.sub(r'<[^>]+>', '', entry.get("title", ""))
            summary = re.sub(r'<[^>]+>', '', entry.get("summary", ""))[:200]
            entries.append({
                "title": title,
                "url": entry.get("link", ""),
                "score": "ArXiv preprint",
                "description": summary,
                "source": "ArXiv"
            })
        return entries
    except:
        return []

SOURCE_COLORS = {
    "HackerNews": "#FF6600",
    "GitHub": "#24292e",
    "ArXiv": "#B31B1B",
}
SOURCE_ICONS = {
    "HackerNews": "🔶",
    "GitHub": "🐙",
    "ArXiv": "📄",
}

async def fetch_and_synthesize():
    hn, gh, ax = await asyncio.gather(
        scrape_hackernews(),
        scrape_github_trending(),
        scrape_arxiv()
    )
    
    all_raw = []
    for item in hn:
        all_raw.append(f"[HackerNews] {item['title']} (score: {item['score']}) — {item['url']}")
    for item in gh:
        all_raw.append(f"[GitHub] {item['title']} (stars: {item['score']}) — {item['description'][:100]} — {item['url']}")
    for item in ax:
        all_raw.append(f"[ArXiv] {item['title']} — {item['description'][:100]} — {item['url']}")
    
    raw_text = "\n".join(all_raw)
    
    prompt = f"""You are the editorial director for an AI company's marketing team.
Review these stories from Hacker News, GitHub trending, and ArXiv.
Select the 8 most relevant and interesting stories for a marketing team building content about AI observability, agent evaluation, and developer tools. For each, provide:
- title (cleaned up if needed)
- source (HackerNews/GitHub/ArXiv)
- why_relevant (1 sentence, sharp and specific)
- engagement_signal (the raw score/stars/views number as a string)
- content_angle (one content idea this story could power)
- url (the original URL)
Return as JSON array only, no preamble.

Stories:
{raw_text}"""
    
    response = client.messages.create(
        model=settings.MODEL_GENERATION,
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    raw_json = response.content[0].text.strip()
    raw_json = re.sub(r'^```json\s*', '', raw_json)
    raw_json = re.sub(r'\s*```$', '', raw_json)
    
    stories_raw = json.loads(raw_json)
    
    stories = []
    for i, s in enumerate(stories_raw):
        source = s.get("source", "HackerNews")
        stories.append({
            "id": str(i),
            "title": s.get("title", ""),
            "source": source,
            "sourceColor": SOURCE_COLORS.get(source, "#666"),
            "icon": SOURCE_ICONS.get(source, "📰"),
            "why_relevant": s.get("why_relevant", ""),
            "engagement_signal": str(s.get("engagement_signal", "")),
            "content_angle": s.get("content_angle", ""),
            "url": s.get("url", ""),
            "trending": i < 3,
        })
    
    return stories

@router.get("")
async def get_briefing():
    cached = briefing_cache.get("briefing")
    if cached:
        return cached
    try:
        stories = await fetch_and_synthesize()
        result = {"stories": stories, "refreshed_at": time.time()}
        briefing_cache.set("briefing", result, ttl_seconds=1800)
        return result
    except Exception as e:
        return {"stories": [], "error": str(e), "refreshed_at": None}

@router.post("/refresh")
async def refresh_briefing():
    briefing_cache.clear("briefing")
    try:
        stories = await fetch_and_synthesize()
        result = {"stories": stories, "refreshed_at": time.time()}
        briefing_cache.set("briefing", result, ttl_seconds=1800)
        return result
    except Exception as e:
        return {"stories": [], "error": str(e), "refreshed_at": None}
