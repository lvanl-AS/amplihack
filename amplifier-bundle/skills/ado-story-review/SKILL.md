---
name: ado-story-review
description: |
  Five-dimension story audit with letter grades. Fetches an ADO User Story,
  grades it across template compliance, AC quality, writing clarity, business
  deliverable, and value clarity, then presents a grade card with actionable
  improvement suggestions.
version: 1.1.0
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
  - .claude/scenarios/az-devops-tools/get_templates.py
  - .claude/scenarios/az-devops-tools/fill_template.py
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

## Execution

Board selection is driven by Claude (no TTY needed).

```bash
# Step 1: Get known boards
BOARDS=$(python3 .claude/scenarios/az-devops-tools/select_board.py --list)
# Step 2: If one board → auto-select its alias as WORKSPACE
#         If multiple → present list to user, ask which one
#         If user wants a different board → --search "<term>", present results,
#           then --save --org <org> --project <project> --team <team> to persist
# Step 3: Resolve selection
WORKSPACE=$(python3 .claude/scenarios/az-devops-tools/select_board.py --select "<alias>")

amplihack recipe run amplifier-bundle/recipes/ado-story-review.yaml \
  -c selected_workspace="$WORKSPACE" \
  -c work_item_id="<story ID>"
```

## Recipe

This skill is driven by the `ado-story-review` recipe.

## Startup Behavior

No preamble. The user invoked this skill — they know what it does. On activation:

1. Extract the work item ID from the user's message (or ask once if missing)
2. Emit a header block and start fetching immediately
3. Do NOT search for files, probe for tools, or re-read context already loaded

## Workflow

1. **Fetch** (parallel) — Pull story data, comments, and revision history. Also fetch parent feature for context.
   - **Checkpoint**: Summarize what was found (title, state, counts) before grading. User's first control point.
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

## Interrupt Behavior

If the user cancels or interrupts, stop immediately. Do not continue to the next step. Checkpoints after fetch and after grading give the user natural control points.

## Key Behaviors

- Python wrappers used in bash steps for deterministic data fetching
- Tools require `ADO_ORG` env var (org slug) — project is auto-discovered
- Improve sub-recipe is internal only — requires review context, cannot run standalone
- Grade card uses letter grades A-F, not numeric scores
- Never blocks the user — soft warnings only, PM has final say

## Cross-References

- See `azure-devops` skill for general ADO operations
- See `ado-story-creation` skill to create new stories
- See `ado-feature-review` for feature-level audits
