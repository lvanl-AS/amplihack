---
name: CAB_cherwell-form
description: |
  Pre-fills all 21 Cherwell portal form fields from available data:
  5 Classify/New Screen fields, 12 Risk Assessment Questionnaire answers,
  and 4 Communication Plan fields. Can be invoked standalone or receive
  pre-computed context from the CR workflow (same dual-mode pattern as CRAM).
  Includes Risk Decision Tree v0.93 classification and consistency checks.
version: 1.0.0
type: skill
auto_activate_keywords:
  - cherwell form
  - fill cherwell
  - cherwell fields
  - cherwell portal
  - fill all cherwell fields
  - cherwell classify
  - cherwell new screen
agents:
  - amplifier-bundle/agents/specialized/ado-context-expert.md
  - amplifier-bundle/agents/specialized/code-changes-expert.md
tools_required:
  - .claude/scenarios/az-devops-tools/select_board.py
  - .claude/scenarios/az-devops-tools/auth_check.py
  - .claude/scenarios/az-devops-tools/extract_child_ids.py
  - .claude/scenarios/az-devops-tools/combine_ids.py
  - .claude/scenarios/az-devops-tools/fetch_child_stories.py
  - .claude/scenarios/az-devops-tools/extract_parent_ids.py
  - .claude/scenarios/az-devops-tools/get_linked_prs.py
  - .claude/scenarios/az-devops-tools/fetch_prs_by_ids.py
  - .claude/scenarios/az-devops-tools/parse_checkpoint.py
  - .claude/scenarios/az-devops-tools/extract_repo_names.py
  - .claude/scenarios/az-devops-tools/get_repo_file.py
  - .claude/scenarios/az-devops-tools/get_pipeline_runs.py
supporting_docs:
  - ../common/templates/reference_cr_template.md
recipe: amplifier-bundle/recipes/CAB_cherwell-form.yaml
---

# Cherwell Form Skill

Pre-fills all 21 Cherwell portal form fields from ADO stories and linked PRs. Covers the three Cherwell form areas: Classify/New Screen, Risk Assessment Questionnaire, and Communication Plan tab. Can run standalone or receive pre-computed context from the CR workflow (same dual-mode pattern as CRAM).

## When to Activate

Activate when the user:
- Wants to pre-fill Cherwell portal form fields for a change
- Says "fill cherwell form", "cherwell fields", "cherwell portal data"
- Has a CR document and wants to fill the Cherwell portal from it
- Needs all Cherwell data in one place for copy/paste

## The 21 Fields

### Group 1: Classify/New Screen (5 fields)

| Field | Options | Auto-Fill Source |
|-------|---------|-----------------|
| **Change Title** | Style Guide format: [Location]+[action]+[object]+[modifier]+[scope] | ADO Context (story/feature titles) |
| **What Are You Changing?** | Application Code, Server, Database, Network, etc. | Code Changes (file types, repo names) |
| **Where Is It Changing?** | MyGate DC, Sealand DC, Cloud, etc. | Deployment configs (often needs user input) |
| **How Is It Changing?** | New, Patch, Update/Maintenance, Decommission | ADO Context + Code Changes |
| **Primary Impacted System** | System name (Cherwell dropdown) | Code Changes (primary repo/service) |

### Group 2: Risk Assessment Questionnaire (12 questions)

| # | Question | Auto-Fill Source |
|---|----------|-----------------|
| Q1 | How Complex Is This Change? | Code Changes (repo/team count) |
| Q2 | Using Automation Tools? | Pipeline data |
| Q3 | How Difficult to Verify? | ADO Context (AC clarity) |
| Q4 | Has a Back Out Plan? | CR Section 3 / deployment configs |
| Q5 | How Long to Back Out? | Pipeline history / CR Section 3 |
| Q6 | Require an Outage? | Deployment configs |
| Q7 | Recoverable Within Outage Window? | Rollback time vs outage window |
| Q8 | Within 10:30PM-4:00AM Window? | Deployment time (often needs input) |
| Q9 | How Many Successful Runs? | Pipeline history |
| Q10 | Has This Been Tested? | Code Changes (test files in diffs) |
| Q11 | Documented Proof of Testing? | Cannot auto-fill — ask user |
| Q12 | Testing Concerns? | Expert testing gaps |

### Group 3: Communication Plan Tab (4 fields)

| Field | Auto-Fill Source |
|-------|-----------------|
| **Pre-Change Communication** | ADO Context (stakeholder mentions, coordination) |
| **During-Change Communication** | CR Section 4 On-Call Channel |
| **Post-Change Communication** | ADO Context (success criteria) |
| **Failure Communication** | CR Section 4 + Section 2 (all impacted systems) |

## Execution

Board selection is driven by Claude (no TTY needed).

```bash
# Standalone: provide story IDs
amplihack recipe run amplifier-bundle/recipes/CAB_cherwell-form.yaml \
  -c selected_workspace="$WORKSPACE" \
  -c story_ids="12345,12346"

# Standalone: provide feature ID
amplihack recipe run amplifier-bundle/recipes/CAB_cherwell-form.yaml \
  -c selected_workspace="$WORKSPACE" \
  -c feature_id="99999"

# Integrated: from CR workflow (all context pre-provided)
# Invoked automatically when user accepts the offer after CR generation
```

## Workflow

### Phase 1-3: Data Fetch + Expert Context (SKIPPED when context provided)
Steps 1-15: Auth, story fetch, PR checkpoint, deployment data, expert agents. Same dual-mode skip pattern as CRAM — when `ado_context` AND `code_changes` are both non-empty, all data-fetch phases are skipped.

### Phase 4: Risk Classification (SKIPPED when `risk_classification` provided)
Step 16: Deterministic Risk Decision Tree v0.93 classification.

### Phase 5: Cherwell Form Fields (ALWAYS RUNS)
Step 17: Classify/New Screen fields (5) — extracts from reviewed CR if available, otherwise computes fresh.
Step 18: Risk Assessment Questionnaire (12 questions) — auto-fills with evidence and confidence levels.
Step 19: Communication Plan (4 fields) — pre-fills from ADO context and CR sections.

### Phase 6: Summary (ALWAYS RUNS)
Step 20: Combines all 21 fields into a unified copy-paste-ready summary.

### Phase 7: Reflect (ALWAYS RUNS)
Step 21: Stores discovery with auto-fill rates, data gaps, and patterns.

## Key Behaviors

- **Context-aware entry** — Skips all data fetch when expert context is pre-provided (integrated mode)
- **Extract from reviewed CR** — In integrated mode, Classify Fields are extracted from the approved CR Section 1 rather than recomputed, ensuring consistency
- **Pre-fill, don't auto-submit** — Every field presented with evidence and confidence level. User confirms or adjusts.
- **Conservative on unknowns** — Mark as `[needs-input]` rather than guessing
- **Risk Decision Tree consistency** — Questionnaire answers must align with tree classification. Discrepancies are flagged.
- **Style Guide enforcement** — Change Title must follow `[Location]+[action]+[object]+[modifier]+[scope]` format
- **Failure communication completeness** — Must cover ALL impacted systems from Section 2
- **Standard Change checks** — Q9 needs 4+ successes, Q1 must be Simple/Moderate, no Ground Stop app

## Output Format

```
## Cherwell Form Summary — All Fields

### 1. Classify/New Screen
| Field | Value |
|-------|-------|
| Change Title | ... |
| What Are You Changing? | ... |
| Where Is It Changing? | ... |
| How Is It Changing? | ... |
| Primary Impacted System | ... |

### 2. Risk Assessment Questionnaire
1. How Complex Is This Change? → [answer]
... (all 12 questions)

**Estimated Cherwell Risk Level**: [Low/Medium/High]
**Risk Decision Tree Classification**: [LOW/MEDIUM/HIGH]
**Alignment**: [consistent / DISCREPANCY]

### 3. Communication Plan
| Field | Value |
|-------|-------|
| Pre-Change Communication | ... |
| During-Change Communication | ... |
| Post-Change Communication | ... |
| Failure Communication | ... |

**Total**: 21 fields | Auto-filled: X | User-provided: Y
```

## Cross-References

- `CAB_change-request-doc` — CR workflow offers this after document export
- `CAB_cram-scoring` — CRAM scoring offered after Cherwell form (both reuse same expert context)
- `CAB_risk-classification` — Standalone risk classification (coexists)
- `CAB_cherwell-risk-questionnaire` — Focused standalone questionnaire (coexists, subset of this recipe)
- `CAB_cherwell-communication-plan` — Focused standalone comm plan (coexists, subset of this recipe)
- See `reference_cr_template.md` Appendix C (Communication Plan), Appendix D (Questionnaire), Section 1 (Classify Fields)
