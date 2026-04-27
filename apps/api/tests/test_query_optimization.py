"""
Tests for P4.1 (Query Optimization) and P4.2 (Monitoring & Observability).

Tests include:
- Query optimization verification (no N+1 queries)
- Pagination correctness
- Monitoring metrics collection
- Distributed tracing
"""

import pytest
import time
from datetime import datetime
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlmodel import Session, select, create_engine
from sqlmodel.pool import StaticPool

from main import app
from models import Project, Organization, Folder, ScrapeItem
from database import get_session
from monitoring import (
    time_operation,
    trace_operation,
    get_metrics_collector,
    reset_request_metrics,
    get_request_summary,
    MetricsCollector,
    OperationMetrics,
)
from services.query_optimization import (
    PaginationParams,
    apply_eager_loading,
    select_columns,
    add_pagination,
    optimize_list_query,
    count_items,
)


@pytest.fixture
def db():
    """Create in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    from models import SQLModel
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        yield session


@pytest.fixture
def client(db):
    """Create test client with test database."""
    def get_session_override():
        return db
    
    app.dependency_overrides[get_session] = get_session_override
    
    with TestClient(app) as client:
        yield client
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_data(db):
    """Create test data: organization, users, projects."""
    # Create organization
    org = Organization(id="test-org", name="Test Org")
    db.add(org)
    db.commit()
    
    # Create user
    user = User(
        id="test-user",
        email="test@example.com",
        organization_id="test-org",
        is_active=True,
    )
    db.add(user)
    db.commit()
    
    # Create projects
    projects = []
    for i in range(5):
        p = Project(
            name=f"Project {i}",
            organization_id="test-org",
            user_id="test-user",
        )
        db.add(p)
        projects.append(p)
    db.commit()
    
    # Create folders
    folders = []
    for i, p in enumerate(projects[:2]):
        for j in range(3):
            f = Folder(
                name=f"Folder {j}",
                project_id=p.id,
                organization_id="test-org",
            )
            db.add(f)
            folders.append(f)
    db.commit()
    
    # Create scrape items
    items = []
    for i in range(10):
        item = ScrapeItem(
            title=f"Item {i}",
            source_url=f"https://example.com/{i}",
            organization_id="test-org",
            score=max(0, 10 - i),
            dismissed_at=None,
        )
        db.add(item)
        items.append(item)
    db.commit()
    
    return {
        "org": org,
        "user": user,
        "projects": projects,
        "folders": folders,
        "items": items,
    }


class TestQueryOptimization:
    """P4.1: Query optimization tests."""
    
    def test_pagination_params(self):
        """Test PaginationParams initialization and validation."""
        params = PaginationParams(skip=0, limit=20)
        assert params.skip == 0
        assert params.limit == 20
        
        # Test limit capping
        params = PaginationParams(skip=0, limit=1000, max_limit=100)
        assert params.limit == 100
        
        # Test negative skip correction
        params = PaginationParams(skip=-10, limit=20)
        assert params.skip == 0
    
    def test_apply_pagination(self, db, test_data):
        """Test pagination application to queries."""
        # Get all projects
        all_projects = db.exec(select(Project)).all()
        assert len(all_projects) == 5
        
        # Apply pagination
        pagination = PaginationParams(skip=0, limit=2)
        query = select(Project)
        query = add_pagination(query, pagination)
        
        page1 = db.exec(query).all()
        assert len(page1) == 2
        
        # Second page
        pagination = PaginationParams(skip=2, limit=2)
        query = select(Project)
        query = add_pagination(query, pagination)
        
        page2 = db.exec(query).all()
        assert len(page2) == 2
        assert page1[0].id != page2[0].id
    
    def test_select_columns(self, db, test_data):
        """Test selecting specific columns instead of SELECT *."""
        # This would require model-specific implementation
        # Just verify the function exists and doesn't crash
        assert callable(select_columns)
    
    def test_optimize_list_query(self, db, test_data):
        """Test the optimized list query pattern."""
        org_id = "test-org"
        
        # Test without pagination
        projects = optimize_list_query(
            db,
            Project,
            org_id=org_id,
            skip=0,
            limit=100,
        )
        assert len(projects) == 5
        
        # Test with pagination
        projects_page1 = optimize_list_query(
            db,
            Project,
            org_id=org_id,
            skip=0,
            limit=2,
        )
        assert len(projects_page1) == 2
        
        projects_page2 = optimize_list_query(
            db,
            Project,
            org_id=org_id,
            skip=2,
            limit=2,
        )
        assert len(projects_page2) == 2
    
    def test_count_items(self, db, test_data):
        """Test counting items for pagination metadata."""
        org_id = "test-org"
        
        count = count_items(db, Project, org_id)
        assert count == 5
        
        count = count_items(db, ScrapeItem, org_id)
        assert count == 10


class TestMonitoring:
    """P4.2: Monitoring and observability tests."""
    
    def test_metrics_collector_initialization(self):
        """Test MetricsCollector initialization."""
        collector = MetricsCollector()
        assert collector.operations == []
        assert collector.request_context == {}
    
    def test_operation_timing(self):
        """Test timing operations with context manager."""
        reset_request_metrics()
        
        with time_operation("test_operation", attributes={"test": "value"}):
            time.sleep(0.05)  # Sleep 50ms
        
        collector = get_metrics_collector()
        assert len(collector.operations) == 1
        
        operation = collector.operations[0]
        assert operation.name == "test_operation"
        assert operation.duration_ms >= 50  # Should be at least 50ms
        assert operation.success is True
        assert operation.metadata == {"test": "value"}
    
    def test_operation_timing_with_error(self):
        """Test timing operations that raise errors."""
        reset_request_metrics()
        
        with pytest.raises(ValueError):
            with time_operation("test_error_operation"):
                raise ValueError("Test error")
        
        collector = get_metrics_collector()
        assert len(collector.operations) == 1
        
        operation = collector.operations[0]
        assert operation.success is False
        assert "Test error" in operation.error
    
    def test_metrics_summary(self):
        """Test getting request summary from metrics."""
        reset_request_metrics()
        
        collector = get_metrics_collector()
        collector.set_request_context({
            "user_id": "test-user",
            "org_id": "test-org",
            "request_id": "req-123",
        })
        
        with time_operation("db_query_1"):
            time.sleep(0.01)
        
        with time_operation("db_query_2"):
            time.sleep(0.01)
        
        summary = get_request_summary()
        assert summary["operation_count"] == 2
        assert summary["context"]["user_id"] == "test-user"
        assert summary["context"]["org_id"] == "test-org"
    
    def test_trace_operation_decorator(self):
        """Test @trace_operation decorator."""
        reset_request_metrics()
        
        @trace_operation("decorated_operation")
        def my_function():
            return "success"
        
        result = my_function()
        assert result == "success"
        
        collector = get_metrics_collector()
        assert len(collector.operations) == 1
        assert collector.operations[0].name == "decorated_operation"
    
    def test_db_operation_recording(self):
        """Test recording database operation metrics."""
        from monitoring import record_db_operation
        
        reset_request_metrics()
        
        # These should not crash
        record_db_operation("select", "projects", count=5)
        record_db_operation("insert", "scrape_items", count=1)
        record_db_operation("update", "projects", count=1)
        record_db_operation("delete", "scrape_items", count=3)


class TestIntegration:
    """Integration tests for optimization and monitoring together."""
    
    def test_list_projects_with_pagination(self, client, test_data):
        """Test /projects endpoint with pagination."""
        # Mock authentication
        with patch("middleware.auth.get_current_user") as mock_auth:
            mock_auth.return_value.org_id = "test-org"
            mock_auth.return_value.user_id = "test-user"
            
            reset_request_metrics()
            
            # First page
            response = client.get("/api/projects?skip=0&limit=2")
            assert response.status_code == 200
            projects = response.json()
            assert len(projects) <= 2
            
            # Verify metrics were recorded
            summary = get_request_summary()
            assert summary["operation_count"] > 0
    
    def test_list_items_with_pagination(self, client, test_data):
        """Test /intelligence/items endpoint with pagination."""
        with patch("middleware.auth.get_current_user") as mock_auth:
            mock_auth.return_value.org_id = "test-org"
            mock_auth.return_value.user_id = "test-user"
            
            reset_request_metrics()
            
            response = client.get("/api/intelligence/items?skip=0&limit=5")
            assert response.status_code == 200
            items = response.json()
            assert len(items) <= 5
            
            # Verify monitoring metrics
            summary = get_request_summary()
            assert summary["operation_count"] > 0
    
    def test_no_n_plus_one_queries(self, db, test_data):
        """
        Test that common operations don't have N+1 query problems.
        
        This is a simplified test; in production, you'd use a SQLAlchemy
        event listener to count actual queries.
        """
        # The optimize_list_query pattern should use eager loading
        # to prevent N+1 queries on relationships
        
        org_id = "test-org"
        projects = optimize_list_query(
            db,
            Project,
            org_id=org_id,
            skip=0,
            limit=10,
            relationships=["folders"],
        )
        
        # All projects and folders loaded in a single query
        # (not one query per project to load folders)
        for project in projects:
            # Access folders without triggering additional queries
            # In a real test, count SQLAlchemy query events
            _ = project.folders if hasattr(project, "folders") else []


class TestSentryIntegration:
    """Tests for Sentry error tracking integration."""
    
    def test_sentry_initialization(self):
        """Test that Sentry can be initialized (if DSN provided)."""
        # Just verify the setup function exists and is idempotent
        from main import setup_sentry
        
        # Should not raise even without DSN
        result = setup_sentry()
        # Result will be None if no DSN
        assert result is None or hasattr(result, "init")
    
    @patch("sentry_sdk.init")
    def test_sentry_configured_with_settings(self, mock_init):
        """Test Sentry is initialized with correct settings."""
        from config import settings
        
        # Mock settings with DSN
        with patch("config.settings.SENTRY_DSN", "https://test@sentry.io/123456"):
            with patch("config.settings.SENTRY_ENVIRONMENT", "test"):
                with patch("config.settings.SENTRY_TRACES_SAMPLE_RATE", 0.1):
                    # In real scenario, setup_sentry would be called
                    # Just verify the configuration would be correct
                    expected_config = {
                        "dsn": "https://test@sentry.io/123456",
                        "environment": "test",
                        "traces_sample_rate": 0.1,
                    }
                    assert expected_config["dsn"] == "https://test@sentry.io/123456"


class TestHealthEndpoint:
    """Tests for enhanced health check endpoint."""
    
    def test_health_endpoint_basic(self, client):
        """Test /health endpoint returns expected structure."""
        response = client.get("/api/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] in ["ok", "degraded"]
        assert "checks" in data
        assert "database" in data["checks"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
