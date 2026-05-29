---
name: CAB_change-request-doc
description: |
  Generates a Change Request Summary document from ADO stories and their
  linked PRs. Story-level entry (not feature). Parent features fetched for
  context. Two expert agents (ADO Context, Code Changes) produce structured
  references that downstream section drafters consume instead of raw data.
  Independent section drafting with coherence check.
version: 4.0.0
type: skill
auto_activate_keywords:
  - change request
  - CR document
  - release document
  - fill CR template
  - change request summary
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
  - amplifier-bundle/agents/specialized/cr-auto-sections.md
  - amplifier-bundle/agents/specialized/cr-rollback-drafter.md
  - amplifier-bundle/agents/specialized/cr-alerting-drafter.md
  - amplifier-bundle/agents/specialized/cr-coherence-checker.md
supporting_docs:
  - ../common/templates/reference_cr_template.md
---

# Change Request Document Skill

Generates a Change Request Summary document from ADO stories and their linked PRs. Automates the tedious parts of change management documentation.

## When to Activate

Activate when the user:
- Wants to generate a change request document
- Says "fill CR template", "change request for story #X", or "release document"
- Needs to prepare change management documentation for a deployment

## Execution

Board selection runs before the recipe so the recipe runner never needs TTY access.

```bash
WORKSPACE=$(python3 .claude/scenarios/az-devops-tools/select_board.py)

# Primary: provide story IDs directly
amplihack recipe run amplifier-bundle/recipes/CAB_change-request-doc.yaml \
  -c selected_workspace="$WORKSPACE" \
  -c story_ids="12345,12346"

# Alternative: provide feature ID to expand to its child stories
amplihack recipe run amplifier-bundle/recipes/CAB_change-request-doc.yaml \
  -c selected_workspace="$WORKSPACE" \
  -c feature_id="99999"

# Both: stories + feature expansion, deduplicated
amplihack recipe run amplifier-bundle/recipes/CAB_change-request-doc.yaml \
  -c selected_workspace="$WORKSPACE" \
  -c story_ids="12345" \
  -c feature_id="99999"
```

## Recipe

This skill is driven by the `change-request-doc` recipe (v4).

## Workflow

### Phase 1a: Story & Feature Fetch (bash)
1. **Auth check** — Verify auth via `auth_check.py`
2. **Expand feature** — If feature_id provided, extract child story IDs via `extract_child_ids.py`
3. **Combine story IDs** — Deduplicate story_ids + expanded IDs via `combine_ids.py`
4. **Fetch stories** — Fetch all stories with relations via `fetch_child_stories.py`
5. **Extract parent features** — Find parent feature IDs from story relations via `extract_parent_ids.py`
6. **Fetch features** — Fetch parent features for context (reuses `fetch_child_stories.py` which accepts any work item IDs)
7. **Fetch linked PRs** — Get all PRs linked to stories via `get_linked_prs.py --detail`

### Phase 1b: PR Checkpoint
8. **PR checkpoint** — Present stories + features + PRs found, ask for additional PRs
9. **Parse additional PRs** — Extract PR IDs from checkpoint via `parse_checkpoint.py`
10. **Fetch additional PRs** — Fetch standalone PRs by ID via `fetch_prs_by_ids.py`

### Phase 2: Deployment Data Fetch (bash)
11. **Extract repo names** — Unique repos from all PR sources via `extract_repo_names.py`
12. **Fetch deployment configs** — Read `deployment.yaml` from each repo via `get_repo_file.py`
13. **Fetch pipeline data** — Pipeline definitions and recent runs via `get_pipeline_runs.py`
14. **Load CR template** — Template reference into context

### Phase 3: Expert Understanding
15. **ADO Context Expert** — Stories + features → structured "what and why" reference document
16. **Code Changes Expert** — PRs + file changes → structured "how and where" reference document

### Phase 4: Section Drafting
17. **Draft auto sections** — `cr-auto-sections` drafts Deployment Details (sec 1), Impacted Systems (sec 2), Documentation Links (sec 5) using expert outputs
18. **Draft rollback** — `cr-rollback-drafter` drafts Rollback Strategy (sec 3) using both expert outputs + raw deployment.yaml + pipeline data
19. **Draft alerting** — `cr-alerting-drafter` drafts Alerting & Monitoring (sec 4) using both expert outputs

### Phase 5: Coherence Check
20. **Coherence check** — Review all sections together for contradictions, cross-check expert risk signals

### Phase 6: Combine + User Review
21. **Combine sections** — Merge into single document with coherence notes
22. **Section-by-section review** — Walk through each section with user
23. **Final approval** — Show complete document, user confirms (uses sentinel markers)
24. **Output** — Generate clean final document (strips all confidence markers)
25. **Reflection** — Store discovery

## Key Behaviors

- **Story-level, not feature-level** — CR documents are per-deployment, driven by story IDs. Features are context, not entry point.
- **Feature ID is optional convenience** — Expands to child stories. All stories have parent features, so features are always discovered.
- **Expert agents compress context** — Two experts produce focused reference documents. Downstream agents never see raw ADO JSON or PR data.
  - ADO Context Expert: requirements, acceptance criteria, business justification
  - Code Changes Expert: repo changes, systems affected, file paths, PR status
- **Checkpoint before template filling** — user confirms PR list before any section is drafted
- **Independent section drafting** — 3 agents draft independently, then coherence check catches contradictions
- **Rollback grounded in real data** — deployment.yaml configs and actual pipeline run history, never guessed
- **Section-by-section review** — not a single "approve all" gate
- **Never guesses** — unknown fields surface as questions to the user
- **Expert agents are reusable** — same experts feed CRAM and Proof of Testing workflows
- **Clean output** — final document has no confidence markers, suitable for SharePoint/change board

## Cross-References

- Planned: `cram-scoring` — CRAM matrix scoring (will reuse expert agents)
- Planned: `proof-of-testing` — test documentation (will reuse expert agents)
- See `ado-task-planning` for the task decomposition workflow pattern
- See `ado-story-creation` for the story creation workflow pattern
