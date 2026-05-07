---
name: ado-task-planning
description: |
  Decomposes an existing ADO User Story into actionable sprint tasks. Maps each
  task to acceptance criteria, flags gaps in testing/observability/rollout, and
  creates all tasks in ADO with parent links.
version: 1.0.0
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
  - .claude/scenarios/az-devops-tools/create_work_item.py
  - .claude/scenarios/az-devops-tools/link_parent.py
supporting_docs:
  - ../common/templates/reference_alaska_story_template.md
  - ../common/checklists/ado/ado-story-architect.md
---

# ADO Task Planning Skill

Decomposes an existing User Story into actionable sprint tasks. Tasks always have a parent story.

## When to Activate

Activate when the user:
- Wants to break a story into tasks
- Says "plan tasks for #12345" or "decompose this story"
- Needs to create implementation tasks for a story

## Recipe

This skill is driven by the `ado-task-planning` recipe.

## Workflow

1. **Auth + fetch** — Verify auth, fetch parent story with relations
2. **Validate parent type** — Must be a User Story. If Feature/Bug/Epic, redirect: "Tasks live under stories. Want to find a story under this, or create one with ado-story-creation?"
3. **Intro** — Shared greeting sub-recipe
4. **Decompose** — 4-8 tasks, each with action-oriented title, 1-3 line description, AC mapping
5. **Anti-pattern critique** — Flags missing testing/observability/rollout tasks. High-level only, advisory
6. **Iterate with user** — Split, merge, add, drop, retitle tasks
7. **Sprint placement** — Agent uses MCP `work_list_team_iterations` for iteration options. Defaults to parent story's iteration
8. **Approval gate** — "Ready to create N tasks under story #X?"
9. **Write to ADO** — Create each task, link to parent, set iteration. Post summary comment on parent story as audit trail
10. **Reflection** — Store discovery in Kuzu

## Key Behaviors

- Tasks always have a parent story — never free-floating
- No sizing ever — no points, T-shirts, or hours. Sizing is the team's job
- High-level decomposition only — describe the WHAT, never the HOW
- No code references, no file paths, no implementation prescriptions
- Every task maps to at least one AC — unmapped = scope creep flag
- Anti-pattern flags are advisory only: missing testing, observability, rollout tasks
- Multi-write — creates multiple work items in one go
- Post summary comment on parent story with all task IDs as audit trail

## Cross-References

- See `ado-story-creation` to create the parent story first
- See `ado-story-review` to review the parent story before planning
- See `azure-devops` skill for general ADO operations
