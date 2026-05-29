---
name: ado-task-planning
description: |
  Decomposes an existing ADO User Story into actionable sprint tasks. Uses
  story-architect and metrics-coach for understanding, task-planner for
  AC-covering decomposition, and technical-advisor for implicit work areas.
  Tasks inherit parent story fields (iteration, area). 50-char title limit.
version: 2.0.0
type: skill
auto_activate_keywords:
  - plan tasks
  - task breakdown
  - decompose story
  - break down story
  - create tasks
tools_required:
  - .claude/scenarios/az-devops-tools/auth_check.py
  - .claude/scenarios/az-devops-tools/get_work_item.py
  - .claude/scenarios/az-devops-tools/create_template_tasks.py
  - .claude/scenarios/az-devops-tools/create_work_item.py
agents:
  - amplifier-bundle/agents/specialized/ado-story-architect.md
  - amplifier-bundle/agents/specialized/ado-metrics-coach.md
  - amplifier-bundle/agents/specialized/ado-task-planner.md
  - amplifier-bundle/agents/specialized/ado-technical-advisor.md
supporting_docs:
  - ../common/templates/reference_alaska_story_template.md
  - ../common/checklists/ado/ado-story-architect.md
---

# ADO Task Planning Skill

Decomposes an existing User Story into actionable sprint tasks. Tasks always have a parent story and inherit its iteration and area path.

## When to Activate

Activate when the user:
- Wants to break a story into tasks
- Says "plan tasks for #12345" or "decompose this story"
- Needs to create implementation tasks for a story

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

amplihack recipe run amplifier-bundle/recipes/ado-task-planning.yaml \
  -c selected_workspace="$WORKSPACE" \
  -c work_item_id="<story ID>"
```

## Recipe

This skill is driven by the `ado-task-planning` recipe.

## Workflow

1. **Auth + fetch** — Verify auth, fetch parent story with relations
2. **Validate + create template tasks** — Validate parent is a User Story, then create mandatory template tasks (CR, PR, Documentation, DOD, RFA) in ADO immediately with inherited iteration/area
3. **Understand** — `ado-story-architect` (structure, AC quality, gaps) and `ado-metrics-coach` (observability/metrics gaps)
4. **Decompose (AC tasks)** — `ado-task-planner` produces story-specific work-area tasks covering all acceptance criteria. Titles ≤50 chars.
5. **Technical discussion** — `ado-technical-advisor` surfaces implicit technical work areas not covered by AC tasks. Discusses with user — user decides what gets added.
6. **Anti-pattern critique** — Reviews full task list for: too-specific tasks, tasks that are actually stories, tasks too broad, titles over 50 chars. Advisory only.
7. **Iterate with user** — Split, merge, add, drop, retitle tasks. 50-char title limit enforced.
8. **Approval gate** — "Ready to create N tasks under story #X?"
9. **Write to ADO** — Create each task, inherit parent iteration/area, link to parent. Post summary comment on parent story as audit trail.
10. **Reflection** — Store discovery

## Key Behaviors

- Tasks always have a parent story — never free-floating
- Tasks inherit iteration path and area path from parent story
- Template tasks (CR, PR, Documentation, DOD, RFA) are created in ADO immediately — before any agent work
- No sizing ever — no points, T-shirts, or hours. Sizing is the team's job
- Tasks are work areas, not implementation specs — general enough for a PM to read
- Title limit: 50 characters or less, no exceptions
- AC coverage: every acceptance criterion must have at least one task covering it
- Technical work areas surfaced as a discussion, not added automatically
- Anti-pattern flags are advisory only
- Post summary comment on parent story with all task IDs as audit trail

## Cross-References

- See `ado-story-creation` to create the parent story first
- See `ado-story-review` to review the parent story before planning
- See `azure-devops` skill for general ADO operations
