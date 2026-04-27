from fastapi import APIRouter, UploadFile, File
from services.file_engine import list_skills, list_context_layers, list_core_docs, REPO_ROOT
import shutil
import subprocess

router = APIRouter(prefix="/api/settings", tags=["settings"])

@router.get("/context")
def get_context_files():
    return list_context_layers()

@router.get("/skills")
def get_skill_files():
    return list_skills()

@router.get("/core")
def get_core_files():
    return list_core_docs()

@router.get("/references")
def get_references(path: str):
    """Get count of skills and playbooks that reference a given file"""
    skills_count = 0
    playbooks_count = 0
    
    try:
        # Search for references in skills
        result = subprocess.run(
            ["grep", "-r", "--", path],
            cwd=str(REPO_ROOT / "skills"),
            capture_output=True,
            text=True
        )
        if result.stdout:
            skills_count = len(set(l.split(":")[0] for l in result.stdout.strip().split("\n") if l))
        
        # Search for references in playbooks
        result = subprocess.run(
            ["grep", "-r", "--", path],
            cwd=str(REPO_ROOT / "playbooks"),
            capture_output=True,
            text=True
        )
        if result.stdout:
            playbooks_count = len(set(l.split(":")[0] for l in result.stdout.strip().split("\n") if l))
    except Exception:
        pass
    
    return {"skills": skills_count, "playbooks": playbooks_count}

@router.get("/api-keys")
def get_api_keys():
    """Get masked API keys from environment"""
    import os
    keys = []
    key_names = ["ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GITHUB_TOKEN"]
    
    for key_name in key_names:
        value = os.getenv(key_name, "")
        if value:
            masked = value[:3] + "*" * max(0, len(value) - 6) + value[-3:] if len(value) > 6 else "*" * len(value)
            keys.append({
                "name": key_name,
                "value": value,
                "masked": masked
            })
    
    return keys

@router.get("/scrape-config")
def get_scrape_config():
    """Get scrape configuration"""
    return [
        {
            "id": "hackernews",
            "name": "Hacker News",
            "enabled": True,
            "params": {"daily_limit": "30"}
        },
        {
            "id": "github",
            "name": "GitHub",
            "enabled": True,
            "params": {"topics": "ai, machine-learning", "stars_min": "100"}
        },
        {
            "id": "arxiv",
            "name": "ArXiv",
            "enabled": True,
            "params": {"categories": "cs.AI, cs.LG"}
        },
        {
            "id": "reddit",
            "name": "Reddit",
            "enabled": False,
            "params": {"subreddits": "MachineLearning, artificial"}
        },
        {
            "id": "rss",
            "name": "RSS Feeds",
            "enabled": False,
            "params": {}
        }
    ]

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    staging_dir = REPO_ROOT / "_uploads"
    staging_dir.mkdir(exist_ok=True)
    dest = staging_dir / file.filename
    with dest.open("wb") as f:
        shutil.copyfileobj(file.file, f)
    content = dest.read_text(errors="ignore")
    return {
        "filename": file.filename,
        "size": dest.stat().st_size,
        "preview": content[:500],
        "suggested_layer": _suggest_layer(file.filename, content),
    }

def _suggest_layer(filename: str, content: str) -> str:
    fn = filename.lower()
    if "messaging" in fn or "positioning" in fn:
        return "context/02_narrative/"
    if "strategy" in fn or "blueprint" in fn:
        return "context/03_strategy/"
    if "analyst" in fn or "ar-" in fn:
        return "context/06_influence/"
    if "research" in fn:
        return "context/07_research/"
    if "philosophy" in fn or "manifesto" in fn:
        return "context/01_philosophy/"
    return "context/05_patterns/"
