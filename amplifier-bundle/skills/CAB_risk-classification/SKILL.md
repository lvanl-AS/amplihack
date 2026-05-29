---
name: CAB_risk-classification
description: |
  Classifies a change using the Alaska Airlines Risk Decision Tree v0.93.
  Deterministic algorithm — Ground Stop/Customer Facing App → HIGH,
  Shared Service → HIGH, blast radius All Users → HIGH, mirror-tested → LOW.
  Outputs risk level, approval requirements, freeze implications, and
  change type guidance. Can be invoked standalone or as part of the CR workflow.
version: 1.0.0
type: skill
auto_activate_keywords:
  - risk classification
  - risk decision tree
  - what risk level
  - change risk level
  - is this high risk
  - classify risk
agents:
  - amplifier-bundle/agents/specialized/ado-context-expert.md
  - amplifier-bundle/agents/specialized/code-changes-expert.md
tools_required:
  - .claude/scenarios/az-devops-tools/select_board.py
  - .claude/scenarios/az-devops-tools/auth_check.py
  - .claude/scenarios/az-devops-tools/fetch_child_stories.py
  - .claude/scenarios/az-devops-tools/get_linked_prs.py
recipe: amplifier-bundle/recipes/CAB_risk-classification.yaml
---

# Risk Decision Tree Classification Skill

Classifies a change using the Alaska Airlines Risk Decision Tree v0.93 algorithm. This is a DETERMINISTIC classification — not a judgment call. The tree has specific, named decision points that produce Low, Medium, or High risk classifications.

## When to Activate

Activate when the user:
- Wants to know the risk level of a change before creating a full CR
- Says "what risk level", "classify this change", "is this high risk"
- Needs to determine approval requirements for a deployment
- Wants to check if a change can use the Standard Change path

## The Algorithm (Risk Decision Tree v0.93)

Evaluate in order. Stop at the FIRST match:

### Step 1: Ground Stop / Customer Facing App Check
**Does this change impact or interact with Account, BTS, ABD, or CSA Mobile?**
- YES → **HIGH RISK** — These are Ground Stop / Day-of-Travel applications that directly affect safety, flight operations, revenue, and guest experience. Even small or routine changes are HIGH risk. Standard Changes CANNOT use the GUID process for these systems.

### Step 2: Shared Service Check
**Does the change affect any Shared Service?** (Network, middleware, API consumed by multiple applications or teams)
- YES → **HIGH RISK**

### Step 3: Blast Radius Check
**If the Change Fails, what is the blast radius?**
- All Users → **HIGH RISK**
- Some Users → **MEDIUM RISK**
- Continue to Step 4 if limited/unknown

### Step 4: Mirror Testing Check
**Change is fully tested in a mirror of the live environment?**
- Less than 100% Tested → **MEDIUM RISK**
- 100% Successfully Tested → **LOW RISK**
- Continue to Step 5 if unknown

### Step 5: Default Classification
- If **Standard Change** → **LOW RISK**
- Otherwise → **MEDIUM RISK**

## Approval Requirements by Risk Level

| Risk Level | Normal Period | Soft Freeze (Fri 12AM - Sun 11:59PM PST) | Hard Freeze |
|---|---|---|---|
| **Low** | Peer Review only | + Director approval | + Director + 2x (MD or VP ITS) + CAB |
| **Medium** | Peer Review + CAB (min 2 members) | + Director approval | + Director + 2x (MD or VP ITS) + CAB |
| **High** | Peer Review + CAB (min 2 members) + Director | + Director approval + CAB | + Director + 2x (MD or VP ITS) + CAB |

## Change Type Constraints

- **Standard Changes** touching Ground Stop/Day-of-Travel apps MUST be submitted as Normal CRs
- **Standard Changes** cannot proceed via pipeline during Hard Freeze — must clone to Normal CR
- **Emergency Changes** can be documented post-implementation for Sev 1/2 incidents, but must be presented at CAB within 7 days
- **Informational** is NO LONGER a valid change type (per AAG Q&A, March 2026). Use Standard, Normal, or Emergency only.

## Key Deadlines

- **Friday 6:00 PM PST**: CR must be submitted with required approvals for inclusion in Monday VP review
- **Thursday 2:00 PM PST**: Weekly CAB meeting
- **Approved Maintenance Window**: 10:30 PM - 4:00 AM

## Execution

### Standalone (quick classification)
Provide story IDs or a description of the change. The skill will:
1. Fetch story data and linked PRs (if IDs provided)
2. Run both expert agents for context extraction
3. Walk the Risk Decision Tree deterministically
4. Output risk level, approval requirements, and change type guidance

### From CR workflow (integrated)
When invoked from the CR recipe, expert context is already computed. The skill skips data fetch and runs the tree directly against the expert outputs.

## Output Format

```
===RISK_CLASSIFICATION===
RISK_LEVEL: <LOW/MEDIUM/HIGH>
TREE_BRANCH: <which step triggered — e.g., "Step 1: Ground Stop App detected (Account)">
GROUND_STOP: <true/false>
SHARED_SERVICE: <true/false>
BLAST_RADIUS: <all_users/some_users/limited/unknown>
MIRROR_TESTED: <yes/no/unknown>

APPROVAL_REQUIRED:
- Normal period: <list approvals>
- Soft freeze (Fri-Sun): <list approvals>
- Hard freeze: <list approvals>

CHANGE_TYPE_GUIDANCE:
- <guidance based on classification>

DEADLINE_REMINDER:
- Friday 6:00 PM PST: CR submission deadline
- Thursday 2:00 PM PST: CAB meeting
===END_RISK_CLASSIFICATION===
```

## Cross-References

- `CAB_change-request-doc` — CR workflow invokes this at Phase 4
- `CAB_cram-scoring` — CRAM scorer includes Risk Decision Tree in its output
- `CAB_cherwell-risk-questionnaire` — Cherwell questionnaire references the tree classification
- See `reference_cr_template.md` Appendix A for the full tree
