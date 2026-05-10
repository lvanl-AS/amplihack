---
name: ado-feature-review
description: |
  Six-dimension feature audit for strategic investment readiness. Fetches an ADO
  Feature, grades it across strategic clarity, discovery/validation, pitch quality,
  outcome metrics, slicability, and delivery feasibility, then presents a grade card.
version: 1.0.0
type: skill
auto_activate_keywords:
  - review feature
  - feature review
  - audit feature
  - grade feature
tools_required:
  - .claude/scenarios/az-devops-tools/get_work_item.py
  - .claude/scenarios/az-devops-tools/get_comments.py
  - .claude/scenarios/az-devops-tools/get_revisions.py
  - .claude/scenarios/az-devops-tools/query_wiql.py
  - .claude/scenarios/az-devops-tools/update_work_item.py
supporting_docs:
  - ../common/templates/reference_alaska_feature_template.md
  - ../common/checklists/ado/ado-feature-author.md
  - ../common/checklists/ado/ado-metrics-coach.md
  - ../common/checklists/ado/ado-story-architect.md
  - ../common/checklists/ado/ado-product-strategist.md
---

# ADO Feature Review Skill

Six-dimension audit for ADO Features to assess strategic investment readiness.

## When to Activate

Activate when the user:
- Asks to review, audit, or grade a feature
- Says "review feature #12345" or "is this feature ready?"
- Wants quality feedback on a feature pitch

## Execution

Board selection runs before the recipe so the recipe runner never needs TTY access:

```bash
WORKSPACE=$(python .claude/scenarios/az-devops-tools/select_board.py)
amplihack recipe run amplifier-bundle/recipes/ado-feature-review.yaml \
  -c selected_workspace="$WORKSPACE" \
  -c work_item_id="<feature ID>"
```

## Recipe

This skill is driven by the `ado-feature-review` recipe.

## Workflow

1. **Fetch** — Bash steps pull feature data, comments, revisions, and child stories
2. **Grade** — Agent grades across six dimensions (A-F):
   - Strategic clarity (problem-first, OKR alignment)
   - Discovery/validation (assumptions tested, evidence cited)
   - Pitch quality (Alaska template, Without/With framing, all three Win audiences)
   - Outcome metrics (North Star + leading indicators, baseline + target)
   - Slicability (can it decompose into 3-7 stories? proposes candidate titles)
   - Delivery feasibility (past team velocity comparison)
3. **Meta-findings** — Reviews grading for gaps or contradictions
4. **Grade card** — Overall = lowest dimension + one letter up if others strong
5. **Actions** — User chooses:
   - **Post review** — Add grade card as ADO comment
   - **Improve feature** — Apply fixes (internal sub-recipe, needs review context)
   - **Argue back** — Challenge specific grades
   - **Done**
6. **Recommendations** — Dialogue-out only (no cross-recipe calls):
   - "Use `ado-story-creation` for missing stories"
   - "Run `ado-story-review` on existing children #123, #456"
7. **Reflection** — Store discovery in Kuzu

## Key Behaviors

- Child stories are evidence of decomposition, not the review subject
- A feature with no children is fine — slicability grades on decomposability
- Slicability is 1 of 6 dimensions, doesn't dominate the assessment
- MCP for wiki templates, OKR searches, past comparables (agent enrichment)
- Never calls story-creation or story-review — recommends them in dialogue only
- Improve sub-recipe is internal only — requires review context

## Cross-References

- See `ado-story-review` for story-level audits
- See `ado-feature-creation` to create new features
- See `ado-story-creation` to create stories under a feature
