# Tests

This directory contains sample briefs and expected outputs for evaluating skill quality.

## Purpose
- Test skill behavior with realistic inputs
- Compare output quality against examples
- Improve prompts and skill definitions
- Prevent quality regression

## Process
1. Pick a sample brief from `tests/sample-briefs/`.
2. Run the relevant playbook.
3. Compare output to `tests/expected-outputs/`.
4. Score with rubrics.
5. Update `tests/evaluation-notes.md` with lessons.

## Files
- `sample-briefs/` — Realistic briefs for testing
- `expected-outputs/` — Examples of strong outputs
- `evaluation-notes.md` — Lessons from past runs
