import asyncio
from anthropic import Anthropic
from config import settings

client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

AGENT_CHAIN = [
    "editorial-director",
    "ai-researcher", 
    "dev-copywriter",
    "dev-reviewer",
    "technical-fact-checker",
    "seo-strategist",
    "copy-chief",
    "claims-risk-reviewer",
    "final-publish-reviewer",
    "social-editor",
    "content-ops-manager",
]

SKILL_CATEGORIES = ["editorial", "foundation", "specialization", "quality"]

def load_skill(agent_name: str) -> str:
    for category in SKILL_CATEGORIES:
        skill_path = settings.REPO_ROOT / settings.SKILLS_DIR / category / agent_name / "SKILL.md"
        if skill_path.exists():
            return skill_path.read_text()
    return f"You are the {agent_name}. Apply your expertise to improve the content."

def load_context_files() -> str:
    ctx_parts = []
    files_to_load = [
        settings.REPO_ROOT / settings.CONTEXT_DIR / "00_orchestration" / "forgeos-context-orchestrator.md",
        settings.REPO_ROOT / settings.CORE_DIR / "VOICE.md",
        settings.REPO_ROOT / settings.CORE_DIR / "STYLE_GUIDE.md",
        settings.REPO_ROOT / settings.CORE_DIR / "CLAIMS_POLICY.md",
    ]
    for f in files_to_load:
        if f.exists():
            ctx_parts.append(f"--- {f.name} ---\n{f.read_text()}")
    return "\n\n".join(ctx_parts)

async def run_agent_chain(
    session_id: int,
    brief: str,
    on_update: callable,
) -> str:
    context = load_context_files()
    accumulated = brief
    total = len(AGENT_CHAIN)
    
    for i, agent_name in enumerate(AGENT_CHAIN):
        skill = load_skill(agent_name)
        progress = int(((i) / total) * 100)
        
        await on_update({
            "type": "agent_update",
            "agent": agent_name,
            "status": "active",
            "progress": progress,
            "output": ""
        })
        
        system_prompt = f"{context}\n\n---\n\nYour role: {agent_name}\n\n{skill}"
        messages = [{"role": "user", "content": f"Here is the current content draft:\n\n{accumulated}\n\nApply your expertise as {agent_name}. Return your improved version."}]
        
        agent_output = ""
        with client.messages.stream(
            model="claude-sonnet-4-5",
            max_tokens=4000,
            system=system_prompt,
            messages=messages,
        ) as stream:
            for text in stream.text_stream:
                agent_output += text
                await on_update({
                    "type": "agent_update",
                    "agent": agent_name,
                    "status": "active",
                    "progress": progress,
                    "output": agent_output
                })
        
        accumulated = agent_output
        await on_update({
            "type": "agent_complete",
            "agent": agent_name,
            "status": "complete",
            "progress": int(((i + 1) / total) * 100),
            "output": agent_output
        })
    
    return accumulated
