---
name: ado-feature-creation
description: |
  Conversational feature creation with dynamic template drafting, coherence
  testing, and business outcome qualification. Understands the feature first,
  drafts sections in parallel from the live ADO template, then runs quality
  gates (technical prescription guard, coherence test, business outcomes,
  analyst lenses) before user review.
version: 2.0.0
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
  - .claude/scenarios/az-devops-tools/get_templates.py
  - .claude/scenarios/az-devops-tools/fill_template.py
supporting_docs:
  - ../common/templates/reference_alaska_feature_template.md
  - ../common/templates/reference_alaska_story_template.md
  - ../common/templates/reference_pm_canonical_frameworks.md
  - ../common/checklists/ado/ado-feature-author.md
  - ../common/checklists/ado/ado-metrics-coach.md
  - ../common/checklists/ado/ado-story-architect.md
  - ../../recipes/ado-feature-section-profiles.yaml
---

# ADO Feature Creation Skill

Conversational feature creation partner for PMs. Produces leadership-defensible Feature pitches matching the Alaska team template.

## When to Activate

Activate when the user:
- Wants to create a new feature
- Says "create feature", "new feature", or "I have an idea for..."
- Has an opportunity they want to turn into a feature pitch

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

amplihack recipe run amplifier-bundle/recipes/ado-feature-creation.yaml \
  -c selected_workspace="$WORKSPACE" \
  -c user_input="<user's feature idea>"
```

## Recipe

This skill is driven by the `ado-feature-creation` recipe (v2).

## Workflow

### Phase 1: Understand
1. **Auth check** — Silent workspace verification
2. **Understand feature** — Conversational exploration of the idea. Not drafting yet.
3. **Identify stakeholders** — Explicit ask. Never invented. Shapes all downstream drafting.
4. **Seed business outcome** — Lightweight ask: "What outcome are you hoping for?" 1-2 sentences, refined later.
5. **Resolve parent** — Epic/Initiative lookup if applicable. Standalone is fine.

### Phase 2: Template Discovery
6. **Load template** — Fetch live Feature template from ADO
7. **Discover sections** — Parse template to find section headers dynamically
8. **Map sections to agents** — Match sections to profiles (exact, fuzzy, or generic fallback). See `ado-feature-section-profiles.yaml`

### Phase 3: Parallel Drafting
9. **Draft all sections** — All sections drafted from the same inputs (feature brief + stakeholders + seed outcome + parent context). Sections are independent.
10. **OKR alignment** — Quick check, runs alongside drafting. Never blocks.

### Phase 4: Quality Gates
11. **Technical prescription guard** — Strip code-level solutions, specific repos, implementation details. Features say WHAT and HOW WE KNOW WE'RE DONE, not HOW TO BUILD IT.
12. **Coherence test** — All sections reviewed together. Do they tell one consistent story? Conflicts presented to user.
13. **Business outcomes & metrics** — Refine seed outcome, quantify where possible, propose North Star + leading indicators.
14. **Analyst lenses** — Select 1-3 relevant perspectives (lawyer, economist, anthropologist, psychologist), dispatch, compile advisory.

### Phase 5: User Review + Late Checks
15. **Present draft** — Full feature with analyst advisory. Multi-round iteration until "looks good."
16. **Generate title** — Derived from approved body, follows template convention.
17. **Slicability check** — 3-7 candidate story titles as a thinking aid. Flags too vague (<3) or too big (8+).
18. **Duplicate check** — WIQL search with full ticket context (better results than early search).
19. **Figma check** — Conditional on frontend signals.

### Phase 6: Save
20. **Pre-commit review** — Final quality gate. Soft warnings. Save / fix / cancel.
21. **Template fill** — Deterministic HTML assembly via fill_template.py
22. **Create in ADO** — Feature creation, parent linking, candidate stories + warnings as comments
23. **Reflection** — Store discovery including fuzzy-match signals (template drift detection)

## Key Behaviors

- Sound like a PM, not a CLI — plain English, no framework jargon
- PM has final say — never hard-refuse. Soft warnings, audit trail
- WHY must use Without/With contrast framing (team convention)
- Stakeholders always asked, never invented
- All Win audiences must be covered
- No delivery estimates — sizing is the team's job
- No technical prescriptions — features don't name repos or prescribe implementation
- Sections drafted independently, coherence verified explicitly
- Template sections discovered dynamically — new sections get drafted via fuzzy-matched or generic prompts
- Write for leadership as the audience

## Section Profiles

Section-to-agent mappings live in `amplifier-bundle/recipes/ado-feature-section-profiles.yaml`. When the ADO template changes:
- New sections: auto-drafted via fuzzy match to nearest known profile, or generic fallback
- Removed sections: silently skipped (no breakage)
- Renamed sections: fuzzy-matched if similar enough, otherwise generic. Add a profile entry for best results.

## Cross-References

- See `ado-story-creation` to create stories under this feature
- See `ado-feature-review` to audit an existing feature
- See `ado-task-planning` to decompose stories into tasks
