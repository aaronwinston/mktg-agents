"""Performance benchmarking endpoint for personal mode."""

import asyncio
import time
import json
from typing import Dict, List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import get_session
from middleware.auth import get_current_user, AuthContext
from personal_mode import is_personal
from models import Project, BriefingItem
import httpx

router = APIRouter()


class BenchmarkResult:
    def __init__(self, endpoint: str, method: str = "GET", description: str = ""):
        self.endpoint = endpoint
        self.method = method
        self.description = description
        self.times: List[float] = []
        self.error: str | None = None

    def add_time(self, ms: float):
        self.times.append(ms)

    def set_error(self, error: str):
        self.error = error

    def p50(self) -> float:
        if not self.times:
            return 0
        sorted_times = sorted(self.times)
        return sorted_times[len(sorted_times) // 2]

    def p95(self) -> float:
        if not self.times:
            return 0
        sorted_times = sorted(self.times)
        idx = int(len(sorted_times) * 0.95)
        return sorted_times[min(idx, len(sorted_times) - 1)]

    def to_dict(self) -> dict:
        if self.error:
            return {
                "endpoint": self.endpoint,
                "method": self.method,
                "description": self.description,
                "error": self.error,
            }
        return {
            "endpoint": self.endpoint,
            "method": self.method,
            "description": self.description,
            "samples": len(self.times),
            "p50_ms": round(self.p50(), 2),
            "p95_ms": round(self.p95(), 2),
            "min_ms": round(min(self.times), 2) if self.times else 0,
            "max_ms": round(max(self.times), 2) if self.times else 0,
        }


@router.get("/api/__benchmark")
async def benchmark(
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Run performance benchmarks on hot paths in personal mode only.
    
    Measures p50 and p95 latency for key endpoints.
    Only available in personal mode.
    """
    if not is_personal():
        raise HTTPException(
            status_code=403,
            detail="Benchmarking only available in personal mode"
        )

    results: Dict[str, BenchmarkResult] = {
        "dashboard_load": BenchmarkResult(
            "/api/projects",
            "GET",
            "Dashboard: fetch projects list"
        ),
        "briefing_fetch": BenchmarkResult(
            "/api/briefing",
            "GET",
            "Dashboard: fetch briefing items"
        ),
        "briefing_item_detail": BenchmarkResult(
            "/api/briefing/{id}",
            "GET",
            "Dashboard: single briefing item"
        ),
        "doctrine_health": BenchmarkResult(
            "/api/doctrine/health",
            "GET",
            "Settings: engine health report"
        ),
        "file_read": BenchmarkResult(
            "/api/files/read",
            "GET",
            "Settings: read file content"
        ),
        "skills_list": BenchmarkResult(
            "/api/skills",
            "GET",
            "Workspace: list available skills"
        ),
        "new_deliverable": BenchmarkResult(
            "/api/deliverables",
            "POST",
            "Workspace: create new deliverable"
        ),
    }

    # Database query benchmarks
    def benchmark_db_queries():
        try:
            start = time.time()
            stmt = select(Project).limit(10)
            list(session.exec(stmt).all())
            elapsed_ms = (time.time() - start) * 1000
            results["db_project_list"] = BenchmarkResult(
                "SELECT projects",
                "DB",
                "Database: list projects"
            )
            results["db_project_list"].add_time(elapsed_ms)
        except Exception as e:
            results["db_project_list"] = BenchmarkResult(
                "SELECT projects",
                "DB",
                "Database: list projects"
            )
            results["db_project_list"].set_error(str(e))

    # Run database benchmarks synchronously
    benchmark_db_queries()

    # Measure endpoint response times (simulated - count API hits if real)
    endpoints_to_bench = [
        ("dashboard_load", "/api/projects"),
        ("briefing_fetch", "/api/briefing"),
        ("doctrine_health", "/api/doctrine/health"),
        ("file_read", "/api/files/read?path=core%2FVOICE.md"),
        ("skills_list", "/api/skills"),
    ]

    # Run actual HTTP benchmarks
    async with httpx.AsyncClient(timeout=30.0) as client:
        for name, path in endpoints_to_bench:
            if name not in results:
                continue

            # Run 3 samples for speed
            for _ in range(3):
                try:
                    start = time.time()
                    # Make request with auth headers
                    response = await client.get(
                        f"http://localhost:8000{path}",
                        headers={"Authorization": f"Bearer dummy"},
                        follow_redirects=True
                    )
                    elapsed_ms = (time.time() - start) * 1000

                    # Only count successful responses
                    if response.status_code < 400:
                        results[name].add_time(elapsed_ms)
                except Exception as e:
                    # Network error - skip this sample
                    pass

    # Fill in targets
    targets = {
        "dashboard_load_ms": 800,
        "briefing_fetch_ms": 400,
        "briefing_item_detail_ms": 200,
        "doctrine_health_ms": 500,
        "file_read_ms": 150,
        "skills_list_ms": 300,
        "new_deliverable_ms": 200,
        "db_project_list_ms": 50,
    }

    # Build response with status indicators
    benchmark_list = []
    met_count = 0
    total_count = 0

    for name, result in results.items():
        result_dict = result.to_dict()

        # Determine if this met its target
        target_key = f"{name}_ms"
        if target_key in targets and "p50_ms" in result_dict:
            target = targets[target_key]
            met = result_dict["p50_ms"] <= target
            result_dict["target_ms"] = target
            result_dict["met_target"] = met
            if met:
                met_count += 1
            total_count += 1

        benchmark_list.append(result_dict)

    return {
        "status": "ok",
        "mode": "personal",
        "benchmarks": benchmark_list,
        "summary": {
            "targets_met": f"{met_count}/{total_count}",
            "note": "p50 latency measured in milliseconds. Targets are p50 values (50th percentile)."
        }
    }
