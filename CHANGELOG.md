# Changelog

## v1.0.0

Initial release of the mktg-agents editorial operating system.

### Added

**Core system**
- `core/VOICE.md` — Voice and style guide for Aaron Winston and the Arize AI brand
- `core/STYLE_GUIDE.md` — Sentence, paragraph, heading, and structure guidance
- `core/BRAND_VOICE.md` — Brand voice attributes and tone by channel
- `core/CONTENT_STRATEGY.md` — Audience segments, content pillars, editorial series
- `core/GOVERNANCE.md` — Review requirements by content type and escalation triggers
- `core/CLAIMS_POLICY.md` — Claim categories and safer language patterns
- `core/DEVELOPER_FLUENCY.md` — Principles and vocabulary for developer-fluent writing
- `core/DISTRIBUTION_STRATEGY.md` — Channel strategy and repurposing model
- `core/EDITORIAL_PRINCIPLES.md` — Ten editorial principles

**Skills**
- Foundation: `ai-researcher`, `dev-copywriter`, `dev-reviewer`, `founder-x-recap`
- Editorial: `editorial-director`, `managing-editor`, `copy-chief`, `content-ops-manager`
- Specialization: `technical-fact-checker`, `seo-strategist`, `launch-comms-writer`, `social-editor`, `customer-story-producer`, `analyst-relations-writer`, `executive-comms-writer`, `lifecycle-email-writer`, `content-repurposer`
- Quality: `claims-risk-reviewer`, `narrative-consistency-reviewer`, `final-publish-reviewer`

**Workflows**
- 10 playbooks covering all major content types
- 8 brief templates
- 9 reusable prompts
- 8 scoring rubrics
- 6 workflow execution guides

**Automation**
- `scripts/validate_repo_structure.py`
- `scripts/lint_skill_files.py`
- `scripts/generate_skill_index.py`
- `scripts/create_content_brief.py`
- `scripts/run_editorial_check.py`
- `.github/workflows/repo-validation.yml`
- `.github/workflows/weekly-editorial-digest.yml`

**Tests and examples**
- 4 sample briefs
- 3 expected output examples
- 4 excellent content examples
- `tests/evaluation-notes.md`
