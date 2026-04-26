# Evaluation notes

A living document for capturing lessons from skill runs.

## Format

```
## [Date] — [Skill or workflow tested]

### Input
Brief summary of what was tested.

### Output quality
What was good, what was weak.

### Lesson
What the skill or prompt should do differently.

### Fix
What was updated and in which files.
```

---

## 2025-01-15 — dev-copywriter on agent evals topic

### Input
Blog brief about agent evaluation harnesses.

### Output quality
The draft was technically accurate but opened with a generic paragraph about AI adoption. Developer fluency was strong in the middle sections.

### Lesson
The dev-copywriter tends to open with category context before getting to the reader's problem. This dilutes the opening.

### Fix
Added to failure modes in `skills/foundation/dev-copywriter/SKILL.md`: "Do not open with category context. Start with the reader's problem."

---

## 2025-01-22 — social-editor on blog repurpose

### Input
Blog post about trace inspection for debugging agents.

### Output quality
LinkedIn post sounded like a brand announcement instead of a founder POV. X posts were too long.

### Lesson
Social-editor needs stronger guidance on the difference between founder voice and company voice.

### Fix
Added to failure modes in `skills/specialization/social-editor/SKILL.md`: "Do not turn a technical founder post into a brand announcement."

---

## 2025-02-01 — claims-risk-reviewer on launch copy

### Input
Launch announcement for a new eval feature.

### Output quality
The reviewer correctly flagged two benchmark claims. Missed one implicit performance claim ("dramatically faster").

### Lesson
Implicit claims using adverbs like "dramatically" or "significantly" need explicit flagging.

### Fix
Added to failure modes: "Flag claims using comparative adverbs (dramatically, significantly, dramatically) that imply quantitative performance without a source."
