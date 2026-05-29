---
name: CAB_change-request-doc
description: |
  Generates a Change Request Summary document from ADO stories and their
  linked PRs. Story-level entry (not feature). Parent features fetched for
  context. Two expert agents (ADO Context, Code Changes) produce structured
  references that downstream section drafters consume instead of raw data.
  Independent section drafting with coherence check. Includes Risk Decision
  Tree classification, Proof of Testing collection, and .docx export.
  Offers unified Cherwell form pre-fill (21 fields) and CRAM scoring as
  optional sub-recipes after document generation.
version: 6.0.0
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

Generates a Change Request Summary document from ADO stories and their linked PRs. Automates the tedious parts of change management documentation. Grounded in the Alaska Airlines Change Management Process Guide, Risk Decision Tree v0.93, Change Record Style Guide, CR Manifest requirements, Cherwell form fields, and AAG IT Change Management Q&A.

Output matches the format used in real CR summary documents: styled Word document (.docx) with tables, hyperlinks, and section headers.

## When to Activate

Activate when the user:
- Wants to generate a change request document
- Says "fill CR template", "change request for story #X", or "release document"
- Needs to prepare change management documentation for a deployment

## Execution

Board selection is driven by Claude (no TTY needed).

```bash
# Step 1: Get known boards
BOARDS=$(python3 .claude/scenarios/az-devops-tools/select_board.py --list)
# Step 2: If one board -> auto-select its alias as WORKSPACE
#         If multiple -> present list to user, ask which one
#         If user wants a different board -> --search "<term>", present results,
#           then --save --org <org> --project <project> --team <team> to persist
# Step 3: Resolve selection
WORKSPACE=$(python3 .claude/scenarios/az-devops-tools/select_board.py --select "<alias>")

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

This skill is driven by the `CAB_change-request-doc` recipe (v6).

## Document Structure

The output document follows the format used in real Alaska Airlines CR summaries:

```
Change Request Summary for CR#[XXXXXX]
Deployment Overview for IT Teams and Change Managers

1. Deployment Details
   - Service / Component
   - Change Summary
   - Version
   - Change Request Link
   - ADO Items

2. Impacted Systems
   - Primary Systems
   - Downstream/Upstream Dependencies
   - Guest Flows / Touchpoints
   - Risk Level

3. Rollback Strategy
   - Rollback Method
   - Rollback Owner
   - Rollback Trigger
   - Estimated Rollback Time
   - Rollback Steps

4. Alerting and Monitoring
   - Dashboards
   - Alerts
   - On-Call Channel
   - Success Criteria

5. Documentation Links
   - RBX
   - MBX
   - Runbook
   - Testing Documentation

6. Proof of Testing
   - Per-change evidence (screenshots, pipeline runs, videos)
   - Brief narrative

Note: Replace bracketed placeholders before submitting...
```

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
15. **ADO Context Expert** — Stories + features -> structured "what and why" reference document. Includes: Style Guide title format, Ground Stop/shared service detection, blast radius assessment, guest flow/touchpoint identification, success criteria from AC.
16. **Code Changes Expert** — PRs + file changes -> structured "how and where" reference document. Includes: Ground Stop/shared service detection, feature flag change detection, Cherwell classify field signals, fail-forward flagging, Risk Decision Tree data.

### Phase 4: Risk Decision Tree Classification
17. **Risk Decision Tree** — Deterministic classification using the v0.93 algorithm:
    - Ground Stop/Customer Facing App -> HIGH
    - Shared Service -> HIGH
    - Blast radius All Users -> HIGH, Some Users -> MEDIUM
    - 100% mirror-tested -> LOW
    - Standard Change -> LOW
    - Otherwise -> MEDIUM
    Outputs: risk level, approval requirements, freeze implications.

### Phase 5: Section Drafting
18. **Draft auto sections** — `cr-auto-sections` drafts Deployment Details (sec 1), Impacted Systems (sec 2), Documentation Links (sec 5) using expert outputs. Includes: Version/build info, ADO Items, Guest Flows/Touchpoints, Risk Level, Cherwell classify fields.
19. **Draft rollback** — `cr-rollback-drafter` drafts Rollback Strategy (sec 3) using both expert outputs + raw deployment.yaml + pipeline data. Produces: Rollback Method, Owner, Trigger, Time, Steps format matching real CRs. Includes Fail-Forward Documentation when rollback not possible.
20. **Draft alerting** — `cr-alerting-drafter` drafts Alerting & Monitoring (sec 4) using both expert outputs. Produces: Dashboards, Alerts, On-Call Channel, Success Criteria format matching real CRs.

### Phase 6: Coherence Check
21. **Coherence check** — Review all sections together for contradictions, cross-check expert risk signals. Checks: systems coverage, rollback completeness, success criteria coverage, Ground Stop consistency, fail-forward completeness, CR Manifest completeness.

### Phase 7: Combine + User Review + Sub-Recipe Offers
22. **Combine sections** — Merge into single document with coherence notes
23. **Section-by-section review** — Walk through each section with user, collect Proof of Testing evidence
24. **Final approval** — Show complete document, user confirms (uses sentinel markers)
25. **Output** — Generate clean final document (strips all confidence markers)
26. **Export .docx** — Convert markdown to Word document with styled headers, bordered tables, and hyperlinks
27. **Cherwell form offer** — Ask if user wants to pre-fill ALL 21 Cherwell portal form fields (Classify, Questionnaire, Communication Plan)
28. **Cherwell form execution** — If yes, invoke `CAB_cherwell-form` recipe with shared expert context (no re-fetch)
29. **CRAM offer** — Ask if user wants CRAM risk assessment (data already collected)
30. **CRAM execution** — If yes, invoke CRAM recipe with shared expert context (no re-fetch). Passes risk_classification so CRAM scorer doesn't re-compute the tree.
31. **Reflection** — Store discovery including Risk Decision Tree result, Ground Stop detection, Cherwell form completeness, fail-forward usage, objective thresholds.

## Key Behaviors

- **Story-level, not feature-level** — CR documents are per-deployment, driven by story IDs. Features are context, not entry point.
- **Feature ID is optional convenience** — Expands to child stories. All stories have parent features, so features are always discovered.
- **Expert agents compress context** — Two experts produce focused reference documents. Downstream agents never see raw ADO JSON or PR data.
  - ADO Context Expert: requirements, acceptance criteria, business justification, Ground Stop flags, blast radius, guest flows/touchpoints, success criteria
  - Code Changes Expert: repo changes, systems affected, file paths, PR status, Ground Stop flags, feature flags, Cherwell fields, fail-forward signals
- **Document structure matches real CRs** — 6 sections matching the format actually used by teams: Deployment Details, Impacted Systems, Rollback Strategy, Alerting and Monitoring, Documentation Links, Proof of Testing.
- **Risk Decision Tree classification** — Deterministic risk level before any section drafting. Informs Change Type guidance and approval routing.
- **Style Guide enforcement** — Change Title follows `[Location]+[action]+[object]+[modifier]+[scope]` with standard vocabulary (for Cherwell form, not the document table)
- **Business partner audience** — Change Summary and all narrative written for non-technical readers
- **Cherwell form pre-fill via sub-recipe** — All 21 Cherwell portal fields (5 Classify, 12 Questionnaire, 4 Communication Plan) offered after document export via `CAB_cherwell-form` recipe with shared context
- **Proof of Testing section** — Collects pipeline screenshots, UI screenshots, videos, and narratives as evidence
- **CR Manifest completeness** — Prompts for mandatory attachments: Runbook, Diagrams, etc.
- **Fail-forward documentation** — When rollback isn't possible, captures: why, impact detection, stabilization plan, stop/go points
- **Checkpoint before template filling** — user confirms PR list before any section is drafted
- **Independent section drafting** — agents draft independently, then coherence check catches contradictions
- **Rollback grounded in real data** — deployment.yaml configs and actual pipeline run history, never guessed
- **Section-by-section review** — not a single "approve all" gate
- **Never guesses** — unknown fields surface as questions to the user
- **Expert agents are reusable** — same experts feed CRAM and Proof of Testing workflows
- **Word document output** — final document exported as .docx with styled tables and headers, matching how real CRs are distributed
- **Clean output** — final document has no confidence markers, suitable for SharePoint/change board
- **Only valid change types** — Standard, Normal, Emergency. Informational is no longer valid per AAG Q&A (March 2026).
- **Ground Stop app awareness** — Account, BTS, ABD, CSA Mobile are automatic HIGH risk
- **Freeze awareness** — Approval requirements change during soft/hard freeze periods
- **Friday 6PM PST deadline** — CRs must be submitted with approvals for Monday VP review and Thursday CAB

## Cross-References

- `CAB_cherwell-form` — Unified Cherwell portal form pre-fill (all 21 fields, offered after document export)
- `CAB_cram-scoring` — CRAM matrix scoring (reuses expert agents, offered after Cherwell form)
- `CAB_risk-classification` — Risk Decision Tree algorithm (invoked during CR workflow at Phase 4)
- Planned: `proof-of-testing` — standalone test documentation (will reuse expert agents)
- See `ado-task-planning` for the task decomposition workflow pattern
- See `ado-story-creation` for the story creation workflow pattern
