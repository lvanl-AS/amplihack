---
name: ado-story-review
description: |
  Five-dimension story audit with letter grades. Fetches an ADO User Story,
  grades it across template compliance, AC quality, writing clarity, business
  deliverable, and value clarity, then presents a grade card with actionable
  improvement suggestions.
version: 1.0.0
type: skill
auto_activate_keywords:
  - review story
  - story review
  - audit story
  - grade story
tools_required:
  - .claude/scenarios/az-devops-tools/get_work_item.py
  - .claude/scenarios/az-devops-tools/get_comments.py
  - .claude/scenarios/az-devops-tools/get_revisions.py
  - .claude/scenarios/az-devops-tools/update_work_item.py
supporting_docs:
  - ../common/templates/reference_alaska_story_template.md
  - ../common/checklists/ado/ado-story-architect.md
  - ../common/checklists/ado/ado-metrics-coach.md
---

# ADO Story Review Skill

Five-dimension audit for ADO User Stories. Read-only by default — only writes to ADO when the user chooses to post the review or improve the story.

## When to Activate

Activate when the user:
- Asks to review, audit, or grade a user story
- Says "review story #12345" or "how good is this story?"
- Wants quality feedback on an existing ADO work item

## Recipe

This skill is driven by the `ado-story-review` recipe.

## Workflow

1. **Fetch** — Deterministic bash steps pull story data, comments, and revision history
2. **Grade** — Agent grades across five dimensions (A-F):
   - Template compliance (Alaska story template)
   - Acceptance criteria quality (testability, coverage, Gherkin)
   - Writing clarity (plain English, no jargon)
   - Business deliverable (actionable, estimable)
   - Value clarity (benefit articulated, metric traceable)
3. **Meta-findings** — Second agent reviews grading for gaps or contradictions
4. **Grade card** — Synthesized report with letter grades, justifications, improvements
5. **Actions** — User chooses:
   - **Post review** — Add grade card as ADO comment
   - **Improve story** — Apply fixes based on findings (internal sub-recipe, needs review context)
   - **Argue back** — Challenge specific grades with evidence
   - **Done** — End review
6. **Reflection** — Store discovery in Kuzu for cross-session pattern detection

## Key Behaviors

- MCP tools used by agents for wiki template comparison and parent feature context
- Python wrappers used in bash steps for deterministic data fetching
- Improve sub-recipe is internal only — requires review context, cannot run standalone
- Grade card uses letter grades A-F, not numeric scores
- Never blocks the user — soft warnings only, PM has final say

## Cross-References

- See `azure-devops` skill for general ADO operations
- See `ado-story-creation` skill to create new stories
- See `ado-feature-review` for feature-level audits
