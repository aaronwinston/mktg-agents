# Contributing

## How to add a new skill

1. Create a directory under the appropriate category:
   - `skills/foundation/` for core research, writing, and review skills
   - `skills/editorial/` for editorial process skills
   - `skills/specialization/` for channel and function-specific skills
   - `skills/quality/` for quality review skills

2. Create a `SKILL.md` file in the directory using the standard template.

3. The template requires these sections (checked by `scripts/lint_skill_files.py`):
   - Frontmatter with `name:` and `description:`
   - `# Role`
   - `# Use this skill when`
   - `# Do not use this skill when`
   - `# Inputs expected`
   - `# Source hierarchy`
   - `# Process`
   - `# Output format`
   - `# Quality bar`
   - `# Failure modes to avoid`
   - `# Related skills`

4. Run validation before submitting:
   ```bash
   python scripts/validate_repo_structure.py
   python scripts/lint_skill_files.py
   python scripts/generate_skill_index.py
   ```

## How to update core guidance

Core files in `core/` affect all skills. Update them carefully.

When updating `core/VOICE.md` or `core/STYLE_GUIDE.md`, review all skills that reference them.

## How to add examples

- Add excellent examples to `examples/excellent/` with a note on what makes them strong.
- Add weak examples to `examples/needs-work/` with a note on the failure mode.

## How to update rubrics

Rubrics define the quality bar. When the standard changes, update the relevant rubric and note the change in `CHANGELOG.md`.

## How to add a playbook

1. Create a file in `playbooks/` following the existing format.
2. Include: use cases, inputs, skill chain, steps, required rubrics, done definition.
3. Add the playbook to `playbooks/README.md`.

## Submitting changes

1. Make your changes on a branch.
2. Run all validation scripts.
3. Submit a pull request with a clear description of what changed and why.
