# Blog production playbook

## Use this playbook for
- Developer blog posts
- Technical explainers
- SEO-driven educational content
- Product education
- Category education

## Input

Use `briefs/blog-brief-template.md`.

## Skill chain

```
blog brief
→ editorial-director
→ ai-researcher
→ dev-copywriter
→ dev-reviewer
→ technical-fact-checker
→ seo-strategist
→ copy-chief
→ claims-risk-reviewer
→ final-publish-reviewer
→ social-editor
→ content-ops-manager
```

## Steps

### 1. Editorial direction
Use `skills/editorial/editorial-director/SKILL.md`.
Output must include: audience, reader problem, core narrative, recommended angle, suggested structure, proof points needed, risks.

### 2. Research
Use `skills/foundation/ai-researcher/SKILL.md`.
Output must include: research summary, developer pain points, content angles, claims requiring verification.

### 3. Draft
Use `skills/foundation/dev-copywriter/SKILL.md`.
Output must include: suggested title, draft, claims to verify, suggested visuals.

### 4. Developer review
Use `skills/foundation/dev-reviewer/SKILL.md`.
Output must include: developer fluency issues, hype or vagueness flags, recommended rewrites, redline edits.

### 5. Technical fact-check
Use `skills/specialization/technical-fact-checker/SKILL.md`.
Output must include a claims table with status for every technical claim.

### 6. SEO review
Use `skills/specialization/seo-strategist/SKILL.md`.
Output must include: search intent, title options, slug, meta description, internal links, FAQ opportunities.

### 7. Copy edit
Use `skills/editorial/copy-chief/SKILL.md`.
Output must include final revised copy and notes on key changes.

### 8. Claims review
Use `skills/quality/claims-risk-reviewer/SKILL.md`.
Output must include: claims by risk level, approval checklist, safer language for flagged claims.

### 9. Final publish review
Use `skills/quality/final-publish-reviewer/SKILL.md`.
Output must include a clear publish decision: Ready / Ready after minor edits / Blocked.

### 10. Distribution
Use `skills/specialization/social-editor/SKILL.md`.
Output must include: LinkedIn variants, X variants, founder version, company version.

### 11. Operations
Use `skills/editorial/content-ops-manager/SKILL.md`.
Output must include: publishing checklist, calendar recommendation, next action.

## Required rubrics
- `rubrics/editorial-quality.md`
- `rubrics/technical-accuracy.md`
- `rubrics/developer-fluency.md`
- `rubrics/seo-quality.md`
- `rubrics/brand-fit.md`
- `rubrics/distribution-readiness.md`

## Done means
- Draft is technically reviewed and claims are categorized
- SEO metadata is ready
- Copy is polished
- Final publish decision is clear
- Social distribution is prepared
- Owner and next action are identified
