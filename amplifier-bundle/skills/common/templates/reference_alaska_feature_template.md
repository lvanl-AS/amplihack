# Alaska Feature Template

This is the authoritative template for all ADO Features. Skills and agents must follow this structure exactly. The audience for a Feature pitch is leadership — write accordingly.

---

## Title

Concise, outcome-oriented. Derived from the body, not the other way around.

## WHAT

One sentence summarizing the feature, followed by scope bullets.

**Scope:**
- [Capability 1]
- [Capability 2]
- [Capability N]

**Out of scope:**
- [Explicit exclusion 1]
- [Explicit exclusion 2]

## WHY

**Must use Without/With contrast framing** (team convention):

> **Without this:** [Describe the current pain — what users experience today, what the business loses, what technical risk exists]
>
> **With this:** [Describe the improved state — what changes for users, what the business gains, what risk is mitigated]

Connect to a business or reliability goal. Features that are purely technical still need a "Why" that links to outcomes.

## STAKEHOLDERS

List by name and role. **Always ask the PM — never invent stakeholder names.**

| Name | Role | Interest |
|------|------|----------|
| [Name] | [PM / Eng Lead / Design / etc.] | [What they care about] |

## Three-Audience Wins

All three audiences must be represented. At least one bullet each.

### Guest Wins
- [How this improves the guest/user experience]

### Business Wins
- [How this moves business metrics — revenue, retention, cost reduction]

### Tech Wins
- [How this improves the technical foundation — reliability, performance, maintainability]

## Quality Measure AC

Guardrails — things that must NOT get worse:

- No increase in [metric X, e.g., page load time, error rate]
- No degradation in [metric Y, e.g., accessibility score, test coverage]
- No regression in [related feature Z]

## Additional Considerations

Drive these as a conversation with the PM:

- **Dependencies**: Other teams, services, or systems required
- **Risks**: Known risks and proposed mitigations
- **Rollout strategy**: Feature flag, canary, ring deployment, big bang
- **Exit criteria**: When do we consider this feature "done done"?
- **No-gos**: Things we explicitly will NOT do (scope creep prevention)

## Acceptance Criteria

Functional criteria for the feature as a whole. Each must be testable.

1. [Criterion — Given/When/Then or plain English]
2. [Criterion]
3. [Criterion]

## Metrics

### North Star Metric
- **Metric**: [Primary success measure]
- **Baseline**: [Current value]
- **Target**: [Expected value]
- **Timeframe**: [Measurement window]

### Leading Indicators
- [Indicator 1 — early signal that the North Star will move]
- [Indicator 2]
- [Indicator 3]

Trace each metric to specific AC where possible.
