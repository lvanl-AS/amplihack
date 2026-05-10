---
name: ado-feature-creation
description: |
  Conversational feature creation with value stress-test and slicability check.
  Guides PMs through strategic context, value validation, sequential drafting
  (description -> stakeholders -> wins -> quality measures -> AC -> metrics ->
  OKR -> slicability -> title), iteration, and pre-commit review.
version: 1.0.0
type: skill
auto_activate_keywords:
  - create feature
  - new feature
  - write feature
  - feature pitch
tools_required:
  - .claude/scenarios/az-devops-tools/auth_check.py
  - .claude/scenarios/az-devops-tools/get_work_item.py
  - .claude/scenarios/az-devops-tools/create_work_item.py
  - .claude/scenarios/az-devops-tools/query_wiql.py
  - .claude/scenarios/az-devops-tools/link_parent.py
supporting_docs:
  - ../common/templates/reference_alaska_feature_template.md
  - ../common/templates/reference_alaska_story_template.md
  - ../common/templates/reference_pm_canonical_frameworks.md
  - ../common/checklists/ado/ado-feature-author.md
  - ../common/checklists/ado/ado-metrics-coach.md
  - ../common/checklists/ado/ado-story-architect.md
---

# ADO Feature Creation Skill

Conversational feature creation partner for PMs. Produces leadership-defensible Feature pitches matching the Alaska team template.

## When to Activate

Activate when the user:
- Wants to create a new feature
- Says "create feature", "new feature", or "I have an idea for..."
- Has an opportunity they want to turn into a feature pitch

## Execution

Board selection runs before the recipe so the recipe runner never needs TTY access:

```bash
WORKSPACE=$(python .claude/scenarios/az-devops-tools/select_board.py)
amplihack recipe run amplifier-bundle/recipes/ado-feature-creation.yaml \
  -c selected_workspace="$WORKSPACE" \
  -c user_input="<user's feature idea>"
```

## Recipe

This skill is driven by the `ado-feature-creation` recipe.

## Workflow

1. **Silent context** — Auth check + load feature template
2. **Duplicate detection** — WIQL search for similar features
4. **Parent epic/initiative resolution** — Find parent Epic if applicable. Unparented is fine
5. **Figma check** — Conditional on frontend signals
6. **Value stress-test** — Non-optional. Not adversarial — helps PM sharpen pitch before leadership. 2-3 observations, not an interrogation
7. **Sequential draft** (order enforced by recipe runner):
   - Description (WHAT + WHY with Without/With contrast framing)
   - Stakeholders (always asked, never invented)
   - Three-audience Wins (Guest, Business, Tech — all three required)
   - Quality measures (guardrails — "no increase in X")
   - Acceptance criteria (functional, traceable to description)
   - Outcome metrics (North Star + 2-3 leading indicators, research-backed)
   - OKR alignment (quick check, never blocks)
8. **Slicability check** — 3-7 candidate story titles as a thinking aid. Not a commitment, not a plan. Flags if too vague (<3) or too big (8+)
9. **Title** — Derived from body
10. **Iterate with user** — Multi-round editing
11. **Consistency validation** — AC to description, metrics to AC, all Win audiences, Without/With framing
12. **Pre-commit review** — Final quality gate with perspective coverage
13. **Write to ADO** — Create Feature, link parent, post candidate stories and warnings as comments
14. **Reflection** — Store discovery in Kuzu

## Key Behaviors

- Sound like a PM, not a CLI — plain English, no framework jargon
- PM has final say — never hard-refuse. Soft warnings, audit trail
- WHY must use Without/With contrast framing (team convention)
- Stakeholders always asked, never invented
- All three Win audiences must be covered
- No delivery estimates — sizing is the team's job
- Value stress-test is mandatory, not opt-in
- Slicability is a thinking aid — titles only, no full stories
- Write for leadership as the audience

## Cross-References

- See `ado-story-creation` to create stories under this feature
- See `ado-feature-review` to audit an existing feature
- See `ado-task-planning` to decompose stories into tasks
