import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import Session, select
from database import engine, create_db_and_tables
from models import PipelineRun
from datetime import datetime

def seed():
    create_db_and_tables()
    with Session(engine) as session:
        existing = session.exec(select(PipelineRun)).all()
        for s in existing:
            session.delete(s)
        session.commit()

        sessions = [
            PipelineRun(
                brief_id=1,
                deliverable_id=None,
                title="Phoenix 5.0 launch blog",
                type="blog",
                audience="developers",
                description="Launch post for Phoenix 5.0 major release",
                status="active",
                current_agent="dev-copywriter",
                progress=65,
            ),
            PipelineRun(
                brief_id=1,
                deliverable_id=None,
                title="AI observability explainer",
                type="blog",
                audience="practitioners",
                description="Deep dive on AI observability for ML teams",
                status="complete",
                current_agent="content-ops-manager",
                progress=100,
            ),
            PipelineRun(
                brief_id=1,
                deliverable_id=None,
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
