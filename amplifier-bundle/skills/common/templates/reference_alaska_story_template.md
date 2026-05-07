# Alaska User Story Template

This is the authoritative template for all ADO User Stories. Skills and agents must follow this structure exactly.

---

## Title

Verb phrase from the user's perspective: "User can view X", not "Add X feature"

## Description (Connextra)

```
As a [persona — specific user role, not "a user"],
I want [capability — what they can do],
so that [benefit — why it matters to them].
```

### Context

Brief background on why this story exists. Reference parent Feature if applicable.

### Scope

- In scope: [bullet list]
- Out of scope: [bullet list]

## Acceptance Criteria (Gherkin)

3-5 testable criteria. Each must trace to something in the Description.

```
Given [precondition]
When [action]
Then [expected outcome]
```

Cover:
- Happy path (required)
- Error/edge cases (at least one)
- Boundary conditions (when applicable)

## Outcome Metric

Quantifiable measure of success tied to specific AC. Must include:
- **Metric**: what is measured
- **Baseline**: current value (or "to be established")
- **Target**: expected value after delivery
- **Timeframe**: when to measure (e.g., "30 days post-deploy")
- **AC link**: which AC this metric validates

## DoR Reminders

Checklist questions to confirm before moving to Active. Surface these for the PM to consider — do not answer them automatically.

- [ ] Is the parent Feature identified and linked?
- [ ] Are all AC testable by QA without PM interpretation?
- [ ] Is there a design artifact linked (if frontend)?
- [ ] Are dependencies on other teams identified?
- [ ] Is the outcome metric baselined?
- [ ] Does the team have enough context to estimate?

## DoD Checklist

- [ ] All AC verified by QA
- [ ] Code reviewed and merged
- [ ] Pipeline passing
- [ ] Deployed to target environment
- [ ] `AB#<id>` in merge commit or PR description
- [ ] Outcome metric instrumentation confirmed
- [ ] No regressions in related functionality

## Release Readiness

Skeleton — fill in as the story progresses toward release:

- [ ] Feature flag configured (if applicable)
- [ ] Rollback plan documented
- [ ] Monitoring/alerting in place for outcome metric
- [ ] Support team briefed (if user-facing change)
- [ ] Documentation updated (if applicable)
