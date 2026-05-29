---
name: ado-story-creation
description: |
  Conversational work item creation with dynamic template drafting, coherence
  testing, and flexible type selection. Establishes context first (understand,
  parent feature, work item type), then loads the right template, drafts
  sections in parallel, and runs quality gates before user review.
version: 2.0.0
type: skill
auto_activate_keywords:
  - create story
  - new story
  - write story
  - add story
  - create bug
  - new bug
tools_required:
  - .claude/scenarios/az-devops-tools/auth_check.py
  - .claude/scenarios/az-devops-tools/get_work_item.py
  - .claude/scenarios/az-devops-tools/create_work_item.py
  - .claude/scenarios/az-devops-tools/query_wiql.py
  - .claude/scenarios/az-devops-tools/link_parent.py
  - .claude/scenarios/az-devops-tools/get_templates.py
  - .claude/scenarios/az-devops-tools/fill_template.py
supporting_docs:
  - ../common/templates/reference_alaska_story_template.md
  - ../common/templates/reference_pm_canonical_frameworks.md
  - ../common/checklists/ado/ado-story-architect.md
  - ../common/checklists/ado/ado-metrics-coach.md
  - ../../recipes/ado-story-section-profiles.yaml
---

# ADO Story Creation Skill

Conversational work item creation partner for PMs. Produces ADO work items (User Story, Bug, Non-Audit, etc.) matching the team template.

## When to Activate

Activate when the user:
- Wants to create a new user story, bug, or work item
- Says "create story", "new story", "create bug", or "I need a story for..."
- Has an idea they want to turn into a structured ADO work item

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

amplihack recipe run amplifier-bundle/recipes/ado-story-creation.yaml \
  -c selected_workspace="$WORKSPACE" \
  -c user_input="<user's story idea>"
```

## Recipe

This skill is driven by the `ado-story-creation` recipe (v2).

## Workflow

### Phase 1: Context (foundational decisions)
1. **Auth check** — Silent workspace verification
2. **Understand story** — Conversational exploration. Not drafting yet.
3. **Resolve parent feature** — Explicit ask: "Do you know what parent feature this goes under? If not, we can try to find it for you." Fetches full feature context.
4. **Select work item type** — Story, Bug, Non-Audit, etc. Informed by the understanding — if user described a defect, suggest Bug.

### Phase 2: Template + Deeper Understanding
5. **Load template** — Fetch template for the selected type (not hardcoded)
6. **Discover sections** — Parse template to find section headers dynamically
7. **Identify persona** — Explicit ask: "Who is the user performing this action?" Feeds into Connextra.
8. **Seed done criteria** — "What does done look like? Just the gist."
9. **Map sections to agents** — Profile lookup + fuzzy match. Marks team checklists (DoR, DoD, Release Readiness) as preserved.

### Phase 3: Parallel Drafting
10. **Draft all sections** — All sections drafted from the same inputs (story brief + persona + done criteria + parent context). Preserved sections copied from template. Connextra preamble assembled from persona + story brief.
11. **OKR alignment** — Quick check, runs alongside drafting. Never blocks.

### Phase 4: Quality Gates
12. **Technical prescription guard** — Strip code-level solutions. Work items say WHAT and HOW WE KNOW WE'RE DONE, not HOW TO BUILD IT.
13. **Coherence test** — All sections reviewed together. Persona consistent, AC traces to description, scope fits under parent.
14. **Metrics research** — One quantifiable outcome metric (lighter than feature-level). Traces to specific AC.
15. **Analyst lenses** — Select 1-3 relevant perspectives, dispatch, compile advisory.

### Phase 5: User Review + Late Checks
16. **Present draft** — Full work item with analyst advisory. Multi-round iteration.
17. **Generate title** — Derived from approved body, follows template convention.
18. **Duplicate check** — WIQL search with full definition (better results than early search). Uses selected work item type.
19. **Figma check** — Conditional on frontend signals.

### Phase 6: Save
20. **Pre-commit review** — Final quality gate. Soft warnings. Save / fix / cancel.
21. **Template fill** — Deterministic HTML assembly via fill_template.py
22. **Create in ADO** — Work item creation using selected type, parent linking, warnings as comments
23. **Reflection** — Store discovery including type selected and fuzzy-match signals

## Key Behaviors

- Sound like a PM, not a CLI — plain English, no framework jargon
- PM has final say — never hard-refuse to save. Raise concerns, respect the call
- Work item type is a choice, not assumed — user picks Story, Bug, Non-Audit, etc.
- Parent feature asked early and explicitly — shapes the entire work item
- No technical prescriptions — work items don't name repos or prescribe implementation
- Sections drafted independently, coherence verified explicitly
- Template sections discovered dynamically — handles any work item type's template
- Team checklists (DoR, DoD, Release Readiness) preserved verbatim from template
- Back claims with research — metrics grounded in past work, OKRs, industry data

## Section Profiles

Section-to-agent mappings live in `amplifier-bundle/recipes/ado-story-section-profiles.yaml`. Profiles are written for User Story templates but the dynamic dispatch handles other types via fuzzy matching and generic fallback. Add type-specific profiles as patterns emerge.

## Cross-References

- See `ado-feature-creation` to create the parent feature first
- See `ado-story-review` to audit an existing work item
- See `ado-task-planning` to decompose a story into tasks
