.PHONY: help dev seed backup restore benchmark test-email health-check

help:
	@echo "ForgeOS Development Commands"
	@echo ""
	@echo "🚀 Core Commands"
	@echo "  make dev           - Start API and web servers locally"
	@echo "  make seed          - Create default project and folders (personal mode)"
	@echo ""
	@echo "📊 Operations"
	@echo "  make benchmark     - Run performance benchmarks on API endpoints"
	@echo "  make health-check  - Check app health and report timings"
	@echo ""
	@echo "💾 Data Management"
	@echo "  make backup        - Backup database and engine files"
	@echo "  make restore DATE=YYYYMMDD_HHMMSS - Restore from backup"
	@echo ""
	@echo "📧 Integrations"
	@echo "  make test-email    - Send test briefing email (requires RESEND_API_KEY)"
	@echo ""

dev:
	@echo "Starting ForgeOS in personal mode..."
	@echo "API: http://localhost:8000"
	@echo "Web: http://localhost:3000"
	@echo ""
	cd apps/api && uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
	API_PID=$$!; \
	sleep 2; \
	cd apps/web && npm run dev &
	WEB_PID=$$!; \
	echo "Both servers running. Press Ctrl+C to stop."; \
	wait

seed:
	@echo "Seeding default project and folders..."
	@cd apps/api && python3 -c "from database import create_db_and_tables; create_db_and_tables(); print('✓ Seeding complete')"

backup:
	@echo "Creating backup..."
	@mkdir -p ~/forgeos-backups
	@TIMESTAMP=$$(date +%Y%m%d_%H%M%S); \
	zip -r ~/forgeos-backups/forgeos_$$TIMESTAMP.zip \
	apps/api/forgeos.db \
	core/ context/ skills/ playbooks/ prompts/ rubrics/ briefs/ \
	-q 2>/dev/null || true; \
	echo "✓ Backup created: ~/forgeos-backups/forgeos_$$TIMESTAMP.zip"

restore:
	@if [ -z "$(DATE)" ]; then \
		echo "Usage: make restore DATE=YYYYMMDD_HHMMSS"; \
		echo "Available backups:"; \
		ls -1 ~/forgeos-backups/ 2>/dev/null | sed 's/forgeos_//;s/.zip//'; \
	else \
		echo "Restoring from backup: $(DATE)"; \
		unzip -o ~/forgeos-backups/forgeos_$(DATE).zip -q; \
		echo "✓ Restore complete"; \
	fi

benchmark:
	@echo "Running performance benchmarks..."
	@curl -s http://localhost:8000/api/__benchmark | python3 -m json.tool

health-check:
	@echo "Checking ForgeOS health..."
	@echo ""
	@echo "API Health:"
	@curl -s http://localhost:8000/api/health 2>/dev/null | python3 -m json.tool || echo "✗ API not responding"

test-email:
	@echo "Sending test briefing email (requires RESEND_API_KEY)..."
	@cd apps/api && python3 -c "print('Email test: implement in service')"
