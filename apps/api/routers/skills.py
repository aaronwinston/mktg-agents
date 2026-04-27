"""Multi-runtime skill execution."""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import get_session
from models import RuntimeCredential
from middleware.auth import get_current_user, AuthContext
from services.runtime_manager import RuntimeManager
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api/skills", tags=["skills"])

class SkillExecutionRequest(BaseModel):
    skill_name: str
    prompt: str
    runtime: Optional[str] = "anthropic"  # Default to Anthropic
    max_tokens: int = 2048

class SkillExecutionResponse(BaseModel):
    output: str
    tokens_input: int
    tokens_output: int
    cost_estimate_cents: int

@router.post("/execute")
async def execute_skill(
    req: SkillExecutionRequest,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Execute a skill using the specified runtime."""
    
    # Get the runtime credential
    credential = session.exec(
        select(RuntimeCredential).where(
            (RuntimeCredential.organization_id == auth.org_id) &
            (RuntimeCredential.runtime == req.runtime)
        )
    ).first()
    
    if not credential:
        raise HTTPException(
            status_code=400,
            detail=f"No {req.runtime} credential configured. Configure one in Settings → Runtimes."
        )
    
    if not credential.is_valid:
        raise HTTPException(
            status_code=400,
            detail=f"{req.runtime} credential is invalid. Please re-validate in Settings."
        )
    
    try:
        # Get the adapter
        adapter = RuntimeManager.get_adapter(req.runtime, credential.encrypted_api_key)
        
        # Execute
        output, input_tokens, output_tokens = await adapter.complete(req.prompt, req.max_tokens)
        
        # Estimate cost
        from services.usage import UsageTracker
        cost_cents = UsageTracker.estimate_token_cost(input_tokens, output_tokens, "claude-3-haiku")
        
        # Record usage
        UsageTracker.record_usage(
            session,
            auth.org_id,
            f"skill_{req.skill_name}",
            {"runtime": req.runtime, "tokens": input_tokens + output_tokens},
            cost_cents
        )
        
        return SkillExecutionResponse(
            output=output,
            tokens_input=input_tokens,
            tokens_output=output_tokens,
            cost_estimate_cents=cost_cents
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Skill execution failed: {str(e)}")

@router.get("/runtimes")
async def list_configured_runtimes(
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """List all configured runtimes for the organization."""
    
    credentials = session.exec(
        select(RuntimeCredential).where(
            RuntimeCredential.organization_id == auth.org_id
        )
    ).all()
    
    return [
        {
            "runtime": c.runtime,
            "is_valid": c.is_valid,
            "last_validated": str(c.last_validated_at) if c.last_validated_at else None,
        }
        for c in credentials
    ]

@router.get("/available")
async def list_available_runtimes():
    """List all available runtime types."""
    return {
        "available_runtimes": RuntimeManager.available_runtimes(),
        "descriptions": {
            "anthropic": "Claude models (Haiku, Sonnet, Opus)",
            "openai": "GPT models (4, 4-Mini, 3.5-Turbo)",
            "copilot": "GitHub Copilot (via SDK)"
        }
    }
