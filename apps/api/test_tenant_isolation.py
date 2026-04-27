import pytest
from fastapi.testclient import TestClient
from main import app
from database import engine
from models import Organization, Membership, Project
from sqlmodel import Session, select
import jwt
import uuid

client = TestClient(app)

def create_test_org(org_name: str) -> tuple[str, str]:
    """Create org + user, return (org_id, user_id)."""
    org_id = str(uuid.uuid4())
    user_id = f"user_{uuid.uuid4().hex[:8]}"
    
    with Session(engine) as session:
        org = Organization(id=org_id, name=org_name, slug=org_name.lower().replace(" ", "-"))
        membership = Membership(
            id=str(uuid.uuid4()),
            user_id=user_id,
            organization_id=org_id,
            role="owner"
        )
        session.add(org)
        session.add(membership)
        session.commit()
    
    return org_id, user_id

def make_token(user_id: str, org_id: str, role: str = "member") -> str:
    """Create a test JWT token."""
    payload = {
        "sub": user_id,
        "org_id": org_id,
        "role": role
    }
    return jwt.encode(payload, "test-secret", algorithm="HS256")

def test_tenant_isolation_project_list():
    """User from org1 cannot see projects from org2."""
    org1_id, user1_id = create_test_org("Org 1")
    org2_id, user2_id = create_test_org("Org 2")
    
    # Create project in org1
    with Session(engine) as session:
        project1 = Project(
            organization_id=org1_id,
            user_id=user1_id,
            name="Project 1"
        )
        project2 = Project(
            organization_id=org2_id,
            user_id=user2_id,
            name="Project 2"
        )
        session.add(project1)
        session.add(project2)
        session.commit()
    
    # User1 lists projects (should only see project1)
    token1 = make_token(user1_id, org1_id)
    response1 = client.get(
        "/api/projects",
        headers={"Authorization": f"Bearer {token1}"}
    )
    assert response1.status_code == 200
    projects1 = response1.json()
    assert len(projects1) == 1
    assert projects1[0]["name"] == "Project 1"
    
    # User2 lists projects (should only see project2)
    token2 = make_token(user2_id, org2_id)
    response2 = client.get(
        "/api/projects",
        headers={"Authorization": f"Bearer {token2}"}
    )
    assert response2.status_code == 200
    projects2 = response2.json()
    assert len(projects2) == 1
    assert projects2[0]["name"] == "Project 2"

def test_tenant_isolation_project_access():
    """User from org1 gets 404 when accessing org2's project."""
    org1_id, user1_id = create_test_org("Org 1")
    org2_id, user2_id = create_test_org("Org 2")
    
    # Create project in org2
    project_id = None
    with Session(engine) as session:
        project = Project(
            organization_id=org2_id,
            user_id=user2_id,
            name="Secret Project"
        )
        session.add(project)
        session.commit()
        session.refresh(project)
        project_id = project.id
    
    # User1 tries to access org2's project
    token1 = make_token(user1_id, org1_id)
    response = client.get(
        f"/api/projects/{project_id}",
        headers={"Authorization": f"Bearer {token1}"}
    )
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"

def test_auth_required():
    """Endpoint requires auth token."""
    response = client.get("/api/projects")
    assert response.status_code == 401 or response.status_code == 403

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
