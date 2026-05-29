---
name: CAB_cram-scoring
description: |
  Generates a CRAM (Change Risk Assessment Matrix) scoring document using the
  Alaska Airlines CRAM template. 3 weighted categories, 11 subcriteria, 1-3
  scale, total 6-18. Reuses the same expert agents as the CR workflow. Can be
  invoked standalone or from the CR recipe with pre-computed expert context.
version: 2.0.0
type: skill
auto_activate_keywords:
  - CRAM
  - risk assessment
  - risk matrix
  - change risk
  - CRAM scoring
  - risk score
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
agents:
  - amplifier-bundle/agents/specialized/ado-context-expert.md
  - amplifier-bundle/agents/specialized/code-changes-expert.md
  - amplifier-bundle/agents/specialized/cram-scorer.md
supporting_docs:
  - ../common/templates/reference_cram_template.md
---

# CRAM Scoring Skill

Generates a Change Risk Assessment Matrix (CRAM) scoring document using the Alaska Airlines CRAM template. Scores a change across 3 weighted categories (Business Impact, Execution Risk, Operational Risk) with 11 subcriteria on a 1-3 scale. Weighted total (6-18) maps to Low/Medium/High risk. Each score is grounded in specific data points from expert analysis, never guessed.

## When to Activate

Activate when the user:
- Wants a risk assessment for a change or deployment
- Says "CRAM score", "risk matrix", "risk assessment for story #X"
- Has completed a CR document and wants the risk score
- Needs to assess change risk for a change advisory board

## Execution

### Standalone (full data fetch)
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

# Primary: provide story IDs directly
amplihack recipe run amplifier-bundle/recipes/CAB_cram-scoring.yaml \
  -c selected_workspace="$WORKSPACE" \
  -c story_ids="12345,12346"

# Alternative: provide feature ID to expand to its child stories
amplihack recipe run amplifier-bundle/recipes/CAB_cram-scoring.yaml \
  -c selected_workspace="$WORKSPACE" \
  -c feature_id="99999"
```

### From CR workflow (shared context)
When invoked from the CR recipe, expert context is already computed. The recipe detects non-empty `ado_context` and `code_changes` and skips Phase 1-3 entirely.

```bash
amplihack recipe run amplifier-bundle/recipes/CAB_cram-scoring.yaml \
  -c selected_workspace="$WORKSPACE" \
  -c ado_context="$ADO_CONTEXT" \
  -c code_changes="$CODE_CHANGES" \
  -c pipeline_data="$PIPELINE_DATA" \
  -c deployment_configs="$DEPLOYMENT_CONFIGS" \
  -c final_cr="$FINAL_CR"
```

## Recipe

This skill is driven by the `CAB_cram-scoring` recipe.

## Workflow

### Phase 1a: Story & Feature Fetch (bash) -- SKIPPED if context provided
1. **Auth check** -- Verify auth via `auth_check.py`
2. **Expand feature** -- If feature_id provided, extract child story IDs
3. **Combine story IDs** -- Deduplicate story_ids + expanded IDs
4. **Fetch stories** -- Fetch all stories with relations
5. **Extract parent features** -- Find parent feature IDs from story relations
6. **Fetch features** -- Fetch parent features for context
7. **Fetch linked PRs** -- Get all PRs linked to stories

### Phase 1b: PR Checkpoint -- SKIPPED if context provided
8. **PR checkpoint** -- Present stories + features + PRs found, ask for additional PRs
9. **Parse additional PRs** -- Extract PR IDs from checkpoint
10. **Fetch additional PRs** -- Fetch standalone PRs by ID

### Phase 2: Deployment Data Fetch (bash) -- SKIPPED if context provided
11. **Extract repo names** -- Unique repos from all PR sources
12. **Fetch deployment configs** -- Read `deployment.yaml` from each repo
13. **Fetch pipeline data** -- Pipeline definitions and recent runs
14. **Load CRAM template** -- Template reference into context

### Phase 3: Expert Understanding -- SKIPPED if context provided
15. **ADO Context Expert** -- Stories + features -> structured "what and why" reference
16. **Code Changes Expert** -- PRs + file changes -> structured "how and where" reference

### Phase 4: CRAM Scoring
17. **Load CRAM template** -- Always loaded (even with shared context)
18. **CRAM Scorer** -- Score all 4 dimensions using expert outputs, pipeline data, deployment configs, and optional final CR

### Phase 5: User Review
19. **Present scores** -- Walk through each category with scores and justifications
20. **Data gap prompts** -- Proactively ask about Secure Coding (SonarQube), System Criticality (ORBIS tier), Resilience & Recovery (RR testing), Change Window — only for flagged gaps
21. **User adjustments** -- User confirms or adjusts scores, recalculate totals
22. **Parse approved scores** -- Extract final JSON from sentinel block
23. **Generate CRAM Excel** -- Produce .xlsx with color-coded scores matching the official template

### Phase 6: Reflection
24. **Reflection** -- Store discovery about scoring patterns

## Key Behaviors

- **Context-aware entry** -- If `ado_context` and `code_changes` are non-empty, skip directly to Phase 4. This enables efficient chaining from the CR workflow.
- **Same experts, different consumer** -- Reuses the same ADO Context Expert and Code Changes Expert as the CR workflow, but feeds their output to the CRAM Scorer instead of section drafters.
- **Alaska Airlines CRAM template** -- 3 categories, 11 subcriteria, 1-3 scale, weighted scoring (6-18 total). Not a generic risk matrix.
- **Weighted scoring** -- Business Impact uses highest subcriterion x 3. Execution Risk uses average x 2. Operational Risk uses average x 1.
- **Risk Decision Tree integration** -- Scorer also runs the deterministic Risk Decision Tree v0.93 and includes the classification in output. Ground Stop apps (Account, BTS, ABD, CSA Mobile) = automatic score 3 for System Criticality. Shared services (multi-consumer APIs) = minimum score 2.
- **Objective thresholds** -- Maintenance window: 10:30 PM - 4:00 AM. SonarQube Alaska Standard: 70% coverage. PCI changes: ALL vulnerabilities resolved. Soft freeze: Fri-Sun. These are not subjective — they are deterministic.
- **Conservative on gaps** -- Missing data scores higher (more conservative). Every gap is flagged explicitly.
- **CR cross-reference** -- When a final CR is provided, the scorer uses deployment window, rollback strategy, and monitoring sections to ground Operational Risk scores.
- **Pipeline data grounds execution risk** -- Rollback time and RR estimates use actual pipeline run durations, not guesses.
- **Never inflates risk** -- Equally dangerous to overstate as understate. Score what the data supports.
- **CRAM → approval routing** -- Score maps to approval requirements: Low (6-10) = Peer only, Medium (11-15) = Peer + CAB, High (16-18) = Peer + CAB + Director. Additional approvals during freeze periods.
- **Cherwell alignment** -- CRAM score should align with Cherwell Risk Assessment Questionnaire result. If they disagree, the scorer flags the discrepancy.
- **Only valid change types** -- Standard, Normal, Emergency. Informational is no longer valid.
- **Excel output** -- Final output is an .xlsx workbook with color-coded scores (green/yellow/red) matching the official CRAM template. Users can tweak in Excel and export as needed.

## Cross-References

- `CAB_change-request-doc` -- CR workflow that can invoke CRAM at the end with shared context
- Planned: `proof-of-testing` -- test documentation (will reuse expert agents)
- See `reference_cram_template.md` for the scoring rubric
- See `cram-scorer.md` agent for scoring logic
