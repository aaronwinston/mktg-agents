# Daily research workflow

## Frequency
Twice daily (automated via GitHub Actions).

## Automated steps
1. `scripts/ai_daily_briefing.py` fetches arXiv RSS feed.
2. Slack message posted with top papers and sources.

## Manual steps (when deeper research is needed)
1. Run `skills/foundation/ai-researcher/SKILL.md`.
2. Use sources: arXiv, Hugging Face Papers, Simon Willison's blog, lab blogs.
3. Produce a research brief.
4. Share with content team.

## Output
- Daily Slack briefing
- Research brief (when manually triggered)
