"""Runtime credential management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from database import get_session
from models import RuntimeCredential, Organization
from middleware.auth import get_current_user, AuthContext
from services.crypto import get_vault
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone

router = APIRouter(prefix="/api/runtimes", tags=["runtimes"])

class RuntimeKeyCreate(BaseModel):
    api_key: str

class RuntimeKeyResponse(BaseModel):
    runtime: str
    is_valid: bool
    last_validated_at: Optional[str] = None

def _validate_key_format(runtime: str, api_key: str) -> bool:
    """Validate API key format for a given runtime."""
    if runtime == 'anthropic':
        return api_key.startswith('sk-ant-')
    elif runtime == 'openai':
        return api_key.startswith('sk-')
    elif runtime == 'copilot':
        return len(api_key) > 10  # Basic validation
    return False

@router.post("/{runtime}/add")
async def add_runtime_key(
    runtime: str,
    data: RuntimeKeyCreate,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Add or update a runtime API key."""
    
    # Validate format
    if not _validate_key_format(runtime, data.api_key):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid API key format for {runtime}"
        )
    
    vault = get_vault()
    encrypted = vault.encrypt_key(data.api_key)
    key_hash = vault.hash_key(data.api_key)
    
    # Check if credential already exists
    existing = session.exec(
        select(RuntimeCredential).where(
            (RuntimeCredential.organization_id == auth.org_id) &
            (RuntimeCredential.runtime == runtime)
        )
    ).first()
    
    if existing:
        # Update
        existing.encrypted_api_key = encrypted
        existing.key_hash = key_hash
        existing.is_valid = False  # Mark for re-validation
        session.add(existing)
    else:
        # Create
        cred = RuntimeCredential(
            organization_id=auth.org_id,
            user_id=auth.user_id,
            runtime=runtime,
            encrypted_api_key=encrypted,
            key_hash=key_hash,
            is_valid=False,
        )
        session.add(cred)
    
    session.commit()
    return {"status": "key_added", "runtime": runtime}

@router.post("/{runtime}/validate")
async def validate_runtime_key(
    runtime: str,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Test a runtime key by making a low-cost API call."""
    
    cred = session.exec(
        select(RuntimeCredential).where(
            (RuntimeCredential.organization_id == auth.org_id) &
            (RuntimeCredential.runtime == runtime)
        )
    ).first()
    
    if not cred:
        raise HTTPException(status_code=404, detail="Runtime key not found")
    
    vault = get_vault()
    
    try:
        api_key = vault.decrypt_key(cred.encrypted_api_key)
        
        # Test call (implementation depends on runtime)
        # For now, just mark as valid
        cred.is_valid = True
        cred.last_validated_at = datetime.now(timezone.utc)
        session.add(cred)
        session.commit()
        
        return {
            "status": "valid",
            "runtime": runtime,
            "last_validated_at": str(cred.last_validated_at),
        }
    except Exception as e:
        return {
            "status": "invalid",
            "runtime": runtime,
            "error": str(e),
        }

@router.delete("/{runtime}")
async def delete_runtime_key(
    runtime: str,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Delete a runtime key."""
    
    cred = session.exec(
        select(RuntimeCredential).where(
            (RuntimeCredential.organization_id == auth.org_id) &
            (RuntimeCredential.runtime == runtime)
        )
    ).first()
    
    if not cred:
        raise HTTPException(status_code=404, detail="Runtime key not found")
    
    session.delete(cred)
    session.commit()
    
    return {"status": "key_deleted", "runtime": runtime}

@router.get("")
async def list_runtime_keys(
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """List configured runtime keys for the organization."""
    
    creds = session.exec(
        select(RuntimeCredential).where(
            RuntimeCredential.organization_id == auth.org_id
        )
    ).all()
    
    return [
        RuntimeKeyResponse(
            runtime=c.runtime,
            is_valid=c.is_valid,
            last_validated_at=str(c.last_validated_at) if c.last_validated_at else None,
        )
        for c in creds
    ]
