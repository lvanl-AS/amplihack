---
name: ado-story-creation
description: |
  Conversational user story creation with sequential drafting and quality gates.
  Guides PMs through duplicate detection, parent feature resolution, sequential
  drafting (description -> AC -> metrics -> OKR -> title), iteration, and
  pre-commit review before saving to ADO.
version: 1.0.0
type: skill
auto_activate_keywords:
  - create story
  - new story
  - write story
  - add story
tools_required:
  - .claude/scenarios/az-devops-tools/auth_check.py
  - .claude/scenarios/az-devops-tools/get_work_item.py
  - .claude/scenarios/az-devops-tools/create_work_item.py
  - .claude/scenarios/az-devops-tools/query_wiql.py
  - .claude/scenarios/az-devops-tools/link_parent.py
supporting_docs:
  - ../common/templates/reference_alaska_story_template.md
  - ../common/templates/reference_pm_canonical_frameworks.md
  - ../common/checklists/ado/ado-story-architect.md
  - ../common/checklists/ado/ado-metrics-coach.md
---

# ADO Story Creation Skill

Conversational story creation partner for PMs. Produces ADO User Stories matching the Alaska team template.

## When to Activate

Activate when the user:
- Wants to create a new user story
- Says "create story", "new story", or "I need a story for..."
- Has an idea they want to turn into a structured ADO work item

## Execution

Board selection runs before the recipe so the recipe runner never needs TTY access:

```bash
WORKSPACE=$(python .claude/scenarios/az-devops-tools/select_board.py)
amplihack recipe run amplifier-bundle/recipes/ado-story-creation.yaml \
  -c selected_workspace="$WORKSPACE" \
  -c user_input="<user's story idea>"
```

## Recipe

This skill is driven by the `ado-story-creation` recipe.

## Workflow

1. **Silent context** — Auth check + load story template
2. **Duplicate detection** — WIQL search for similar stories, present if >70% match
4. **Parent feature resolution** — Find and understand the parent Feature. Unparented is fine. Attaching at save time without prior review requires explicit user override + audit comment
5. **Figma check** — Conditional on frontend signals. Simple ask, sets flag for pre-save summary
6. **Sequential draft** (order enforced by recipe runner):
   - Description (Connextra format, informed by parent feature context)
   - Acceptance criteria (3-5 testable, trace to description)
   - Outcome metric (research-backed via MCP)
   - OKR alignment (quick check, never blocks)
   - Title (derived from body, not the other way around)
7. **Iterate with user** — Multi-round editing, flag cross-section impacts
8. **Consistency validation** — AC traces to description, metric to AC, title to body
9. **Pre-commit review** — Final quality gate, soft warnings only. Pre-save summary shows parent/Figma/duplicate status
10. **Write to ADO** — Create work item, link parent, attach Figma, post warnings as comments
11. **Reflection** — Store discovery in Kuzu

## Key Behaviors

- Sound like a PM, not a CLI — plain English, no framework jargon
- PM has final say — never hard-refuse to save. Raise concerns, respect the call
- Sequential drafting enforced — each step builds on previous output
- Stories describe the WHAT, not the HOW — no code references, no implementation details
- Parent feature enforcement: unparented is fine, but attaching without review needs override
- Back claims with research — metrics grounded in past work, OKRs, industry data

## Cross-References

- See `ado-feature-creation` to create the parent feature first
- See `ado-story-review` to audit an existing story
- See `ado-task-planning` to decompose a story into tasks
