---
name: CAB_cherwell-risk-questionnaire
description: |
  Pre-fills answers to the 12 Cherwell Risk Assessment Questionnaire questions
  from available data (expert context, pipeline data, deployment configs).
  User confirms/adjusts each answer. The questionnaire drives Cherwell's
  system-calculated risk level (Low/Medium/High) which determines approval routing.
  Can be invoked standalone or as part of the CR workflow.
version: 1.0.0
type: skill
auto_activate_keywords:
  - cherwell risk questions
  - risk questionnaire
  - cherwell risk assessment
  - fill risk questions
  - risk assessment questionnaire
agents:
  - amplifier-bundle/agents/specialized/ado-context-expert.md
  - amplifier-bundle/agents/specialized/code-changes-expert.md
tools_required:
  - .claude/scenarios/az-devops-tools/select_board.py
  - .claude/scenarios/az-devops-tools/auth_check.py
  - .claude/scenarios/az-devops-tools/fetch_child_stories.py
  - .claude/scenarios/az-devops-tools/get_linked_prs.py
  - .claude/scenarios/az-devops-tools/get_pipeline_runs.py
recipe: amplifier-bundle/recipes/CAB_cherwell-risk-questionnaire.yaml
---

# Cherwell Risk Assessment Questionnaire Skill

Pre-fills answers to the 12 questions on the Cherwell Risk Assessment Questionnaire using data from expert agents, pipeline runs, and deployment configs. These questions are answered directly in the Cherwell form and drive the system-calculated risk level (Low/Medium/High).

**Important**: This questionnaire is SEPARATE from CRAM. CRAM is a deeper weighted analysis. The Cherwell questionnaire is the built-in risk calculator in the change management system. Both should be consistent.

## When to Activate

Activate when the user:
- Needs to fill out the Cherwell risk assessment
- Says "fill risk questions", "help with Cherwell risk assessment"
- Is creating a CR in Cherwell and wants pre-computed answers
- Has completed a CR document and needs to transfer data to Cherwell

## The 12 Questions

### Q1: How Complex Is This Change?
**Options**: Simple, Moderate, Complex, Very Complex
**Auto-fill logic**: Count repos, teams, integration points from Code Changes Expert:
- 1-2 repos, single team, no cross-service changes → Simple
- 3-4 repos, 2-3 teams, minor integration → Moderate
- 5+ repos, 4+ teams, deep integration → Complex or Very Complex
**Note**: Selecting Complex or Very Complex raises the calculated risk.

### Q2: Is This Change Using Automation Tools To Reduce Manual Steps?
**Options**: Yes / No
**Auto-fill logic**: From pipeline data — if deployment pipeline exists → Yes. Manual deployment → No.

### Q3: How Difficult Is It To Verify The Change Completed Successfully?
**Options**: Easy, Moderate, Difficult
**Auto-fill logic**: From ADO Context Expert → Testing & Verification:
- Clear AC with specific, measurable checks → Easy
- Vague AC or compound criteria → Moderate
- No AC or untestable requirements → Difficult

### Q4: Does This Change Have a Back Out Plan?
**Options**: Yes / No
**Auto-fill logic**: From CR Section 3 — if rollback steps exist → Yes. If fail-forward only → No (but must have mitigation documented).

### Q5: How Long to Back Out of This Change?
**Options**: Dropdown (time ranges)
**Auto-fill logic**: From pipeline run history → rollback duration. Convert to minutes. Round up.

### Q6: Will This Change Require an Outage?
**Options**: Yes / No
**Auto-fill logic**: From deployment configs — outage window mentioned? Service restart required? If no evidence either way, ask user.

### Q7: If the Change Fails, Is the System Recoverable Within the Outage Window?
**Options**: Yes / No
**Auto-fill logic**: Compare rollback time estimate vs planned outage window. If rollback < outage → Yes.

### Q8: Does This Change Fall Within the 10:30pm - 4:00am Maintenance Window?
**Options**: Yes / No
**Auto-fill logic**: If deployment time is known, check against 10:30 PM - 4:00 AM window. If unknown, ask user.

### Q9: How Many Times Has This Change Been Successful?
**Options**: Dropdown (count ranges)
**Auto-fill logic**: From pipeline run history — count successful runs against main branch. For Standard Change eligibility, need 4+ successful error-free runs.

### Q10: Has This Change Been Tested?
**Options**: Yes / No
**Auto-fill logic**: From Code Changes Expert → Testing & Verification — test files in diffs? Test descriptions in PRs? If yes → Yes. If no test evidence, ask user (testing may happen outside PR workflow).

### Q11: Have You Documented and Archived Proof of Testing?
**Options**: Yes / No
**Auto-fill logic**: CANNOT auto-fill. Ask user directly: "Have you documented and archived proof of testing? This maps to the Cherwell requirement and CR Manifest 'Test plan and validated results' attachment."

### Q12: List any remaining concerns regarding testing this change
**Options**: Free text
**Auto-fill logic**: From expert Testing gaps + coherence flags about testing. Draft concerns from:
- Repos with code changes but no test file changes
- Stories with no AC (nothing to test against)
- Compound AC that should be split
- Any coherence flags about testing coverage

## Key Behaviors

- **Pre-fill, don't auto-submit** — Present each answer with evidence and confidence level. User confirms or adjusts.
- **Consistency with Risk Decision Tree** — Answers should be consistent with the Risk Decision Tree classification. If they diverge, flag it.
- **Consistency with CRAM** — If CRAM scoring was also done, cross-reference for consistency.
- **Conservative on unknowns** — If data is insufficient, say so and ask rather than guessing optimistically.
- **Standard Change checks** — If user indicates Standard Change type, verify: Q9 shows 4+ successes, Q1 is Simple or Moderate (not Complex), and no Ground Stop app involvement.

## Execution

### From CR workflow (integrated)
Invoked after section review with pre-computed expert context, pipeline data, and CR draft. No additional data fetch needed.

### Standalone
Provide story IDs or change description. The skill fetches data, runs experts, then pre-fills questionnaire answers.

## Output Format

Present as a numbered checklist:

```
## Cherwell Risk Assessment Questionnaire — Pre-filled Answers

1. **How Complex Is This Change?** → [answer] [confidence]
   Evidence: [what drove this answer]

2. **Is This Change Using Automation Tools?** → [answer] [confidence]
   Evidence: [what drove this answer]

... (all 12 questions)

**Estimated Cherwell Risk Level**: [Low/Medium/High based on answers]
**Risk Decision Tree Classification**: [LOW/MEDIUM/HIGH]
**Alignment check**: [consistent / DISCREPANCY — explain]

Please confirm each answer or tell me which to adjust.
```

## Cross-References

- `CAB_change-request-doc` — CR workflow invokes this after section review (Phase 7, Step 24)
- `CAB_risk-classification` — Risk Decision Tree classification should align with questionnaire answers
- `CAB_cram-scoring` — CRAM scores should be consistent with questionnaire answers
- See `reference_cr_template.md` Section 7 for the question mapping table
