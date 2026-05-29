---
name: CAB_cherwell-communication-plan
description: |
  Pre-fills the 4 Cherwell Communication Plan tab fields from available data.
  Communication Plan is filled directly in the Cherwell form, not as a section
  in the CR summary document. Required for ALL change types.
version: 1.0.0
type: skill
auto_activate_keywords:
  - communication plan
  - cherwell communication
  - fill communication plan
  - who to notify
agents:
  - amplifier-bundle/agents/specialized/ado-context-expert.md
tools_required:
  - .claude/scenarios/az-devops-tools/select_board.py
  - .claude/scenarios/az-devops-tools/auth_check.py
  - .claude/scenarios/az-devops-tools/fetch_child_stories.py
  - .claude/scenarios/az-devops-tools/get_linked_prs.py
---

# Cherwell Communication Plan Skill

Pre-fills the 4 fields on the Cherwell "Communications Plan" tab using data from ADO stories and expert analysis. This is a Cherwell form activity, NOT a section in the CR summary document.

## When to Activate

Activate when the user:
- Needs to fill in the Communication Plan tab in Cherwell
- Says "fill communication plan", "who to notify for this change"
- Is completing Cherwell form fields after generating a CR document
- Has completed a CR document and needs to transfer data to Cherwell

## The 4 Fields

### 1. Pre-Change Communication
Who needs to know before the change, and what to tell them.
**Auto-fill logic**: From ADO Context Expert -> Communication Signals: stakeholder mentions, team coordination notes, go/no-go calls mentioned in stories.

### 2. During-Change Communication
How status updates will be shared during implementation.
**Auto-fill logic**: From CR Section 4 On-Call Channel (if available). Suggest Teams channel for status updates at key deployment milestones.

### 3. Post-Change Communication
Who to notify of completion, and how to verify.
**Auto-fill logic**: From ADO Context Expert -> Success Criteria: who confirms success. Standard format: "Notify [team] via [channel] once verified against success criteria."

### 4. Failure Communication
Who to notify if rollback is triggered.
**Auto-fill logic**: From CR Section 4 On-Call Channel + Section 2 Impacted Systems. Must cover ALL impacted teams/systems.

## Key Behaviors

- **Pre-fill, don't auto-submit** — Present each field with evidence and confidence. User confirms or adjusts.
- **Conservative on unknowns** — If no communication signals found in ADO data, say so and ask rather than guessing.
- **Failure communication must be comprehensive** — Every impacted system from Section 2 must have a corresponding notification path.

## Execution

### From CR workflow (integrated)
Invoked after the Cherwell Risk Questionnaire with pre-computed expert context. No additional data fetch needed.

### Standalone
Provide story IDs or CR document. The skill fetches data, runs the ADO Context Expert, then pre-fills Communication Plan fields.

## Output Format

```
## Cherwell Communication Plan -- Pre-filled

| Field | Suggested Value | Confidence |
|-------|----------------|------------|
| Pre-Change Communication | [value] | [auto/draft/needs-input] |
| During-Change Communication | [value] | [auto/draft/needs-input] |
| Post-Change Communication | [value] | [auto/draft/needs-input] |
| Failure Communication | [value] | [auto/draft/needs-input] |

Please confirm each or tell me what to adjust.
```

## Cross-References

- `CAB_change-request-doc` -- CR workflow invokes this after the Cherwell Risk Questionnaire
- `CAB_cherwell-risk-questionnaire` -- The 12 risk questions are separate from the Communication Plan
- See `reference_cr_template.md` Appendix C for the field descriptions
