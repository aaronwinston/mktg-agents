import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timezone

from sqlmodel import Session, select

from database import engine, create_db_and_tables
from models import Brief, Deliverable, Folder, Organization, PipelineRun, Project


def seed():
    create_db_and_tables()

    with Session(engine) as session:
        org = session.exec(select(Organization).where(Organization.slug == "demo")).first()
        if not org:
            org = Organization(name="Demo Org", slug="demo", plan="free")
            session.add(org)
            session.commit()
            session.refresh(org)

        user_id = "demo-user"

        project = session.exec(
            select(Project).where(
                (Project.organization_id == org.id) & (Project.user_id == user_id)
            )
        ).first()
        if not project:
            project = Project(organization_id=org.id, user_id=user_id, name="Demo Project")
            session.add(project)
            session.commit()
            session.refresh(project)

        folder = session.exec(
            select(Folder).where(
                (Folder.organization_id == org.id) & (Folder.project_id == project.id)
            )
        ).first()
        if not folder:
            folder = Folder(organization_id=org.id, project_id=project.id, name="Deliverables")
            session.add(folder)
            session.commit()
            session.refresh(folder)

        # Clear old demo pipeline runs
        for s in session.exec(
            select(PipelineRun).where(PipelineRun.organization_id == org.id)
        ).all():
            session.delete(s)
        session.commit()

        # Create a single brief/deliverable anchor used by the sessions
        brief = Brief(
            organization_id=org.id,
            user_id=user_id,
            project_id=project.id,
            title="Demo Brief",
            brief_md="Demo brief",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        session.add(brief)
        session.commit()
        session.refresh(brief)

        deliverable = Deliverable(
            organization_id=org.id,
            folder_id=folder.id,
            content_type="blog",
            title="Demo Deliverable",
            status="draft",
        )
        session.add(deliverable)
        session.commit()
        session.refresh(deliverable)

        sessions = [
            PipelineRun(
                organization_id=org.id,
                brief_id=brief.id,
                deliverable_id=deliverable.id,
                title="Phoenix 5.0 launch blog",
                type="blog",
                audience="developers",
                description="Launch post for Phoenix 5.0 major release",
                status="active",
                current_agent="dev-copywriter",
                progress=65,
            ),
            PipelineRun(
                organization_id=org.id,
                brief_id=brief.id,
                deliverable_id=deliverable.id,
                title="AI observability explainer",
                type="blog",
                audience="practitioners",
                description="Deep dive on AI observability for ML teams",
                status="complete",
                current_agent="content-ops-manager",
                progress=100,
            ),
            PipelineRun(
                organization_id=org.id,
                brief_id=brief.id,
                deliverable_id=deliverable.id,
                title="Q2 newsletter",
                type="email",
                audience="subscribers",
                description="Quarterly newsletter for Q2 2025",
                status="pending",
                current_agent=None,
                progress=0,
            ),
        ]
        for s in sessions:
            session.add(s)
        session.commit()

        print("Seeded 3 demo sessions.")


if __name__ == "__main__":
    seed()
