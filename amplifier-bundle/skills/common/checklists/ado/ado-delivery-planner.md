# ado-delivery-planner checklist

**Source**: `.claude/agents/ado-delivery-planner.md` — 2020 Scrum Guide; Mike Cohn
*Agile Estimating and Planning*; David J. Anderson Kanban + STATIK; Daniel Vacanti
flow metrics + work-item age; Roman Pichler Sprint Goal template; Vasco Duarte
#NoEstimates; Forsgren/Humble/Kim DORA; Goldratt TOC; Microsoft bug-cap pattern.

**Refinement IDs**: `ado-delivery-planner.<category>.<item>`.

---

## Mandatory verifications

### Task decomposition
- [ ] ado-delivery-planner.task.invest-confirmed [all] — Story passes INVEST before decomposing (delegate to `ado-story-architect` if uncertain)?
- [ ] ado-delivery-planner.task.one-day-or-less [all] — Each task fits ≤1 day (2020 Scrum Guide rule)?
- [ ] ado-delivery-planner.task.includes-non-code [all] — Non-code tasks included: design review, instrumentation, runbook, feature-flag rollout, comms?
- [ ] ado-delivery-planner.task.sequenced-for-integration-risk [generation] — Sequence surfaces integration risk early (don't leave UI-API contract for last)?
- [ ] ado-delivery-planner.task.no-over-decomposition [review] — No sub-2-hour tasks (signals micromanagement)?

### Capacity planning
- [ ] ado-delivery-planner.capacity.formula [generation] — `(Team × Days × Hours/day × Focus Factor) − PTO − Ceremonies − On-call` applied?
- [ ] ado-delivery-planner.capacity.focus-factor [generation] — Focus factor 0.6-0.8 (lower for new teams; higher for stable)?
- [ ] ado-delivery-planner.capacity.ramp-up [review] — New team members at 50-70% normal contribution?
- [ ] ado-delivery-planner.capacity.incident-buffer [generation] — 10-15% buffer for production incidents (or separate swimlane)?

### Sprint goal
- [ ] ado-delivery-planner.goal.method-and-metric [all] — Pichler's template: goal + method + metric ("Streamline checkout to lift conversion by 5%" not "Enhance shopping cart")?
  - Severity: critical when goal is just feature-naming
- [ ] ado-delivery-planner.goal.bosss-boss-test [generation] — Cohn's "boss's boss" test: one sentence a non-technical exec understands?
- [ ] ado-delivery-planner.goal.not-compound [all] — Not compound ("X AND Y AND Z" leaves no flexibility)?

### Velocity discipline
- [ ] ado-delivery-planner.velocity.completed-only [all] — Completed work only — partially done counts zero (prevents gaming)?
- [ ] ado-delivery-planner.velocity.rolling-average [generation] — 3-5 sprint rolling average for forecasting (Yesterday's Weather)?
- [ ] ado-delivery-planner.velocity.never-cross-team [all] — NEVER compared across teams (points are relative within a single team)?
- [ ] ado-delivery-planner.velocity.not-as-kpi [all] — NEVER used as performance KPI?
  - Severity: critical (drives sandbagging + quality erosion)

### Flow metrics (Kanban)
- [ ] ado-delivery-planner.flow.wip-limited [all] — WIP limits set?
- [ ] ado-delivery-planner.flow.little-law [generation] — Little's Law applied: `Avg WIP = Throughput × Avg Cycle Time`?
- [ ] ado-delivery-planner.flow.work-item-age [review] — Aging work items surfaced? (Vacanti.)
- [ ] ado-delivery-planner.flow.sle [generation] — Service Level Expectations published ("85% of items ship within 10 days")?

### DORA
- [ ] ado-delivery-planner.dora.measured [generation] — Deployment Frequency, Lead Time, Change Failure Rate, MTTR measured?

### Bug cap (Microsoft)
- [ ] ado-delivery-planner.bug-cap.engineers-times-5 [generation] — Bug cap = engineers × 5; team stops features when exceeded?
  - Severity: critical when ignored — debt compounds invisibly

### Dependencies
- [ ] ado-delivery-planner.deps.identified-at-planning [all] — External vs internal dependencies identified at sprint planning?
- [ ] ado-delivery-planner.deps.mandatory-vs-discretionary [generation] — Distinguished? Mandatory = technical/contractual; Discretionary = chosen sequence (often eliminable).

### Anti-patterns
- [ ] ado-delivery-planner.antipattern.over-commit [review] — Pulling more than capacity supports?
  - Severity: critical
- [ ] ado-delivery-planner.antipattern.sandbagging [review] — Inflated estimates to look good?
- [ ] ado-delivery-planner.antipattern.mid-sprint-scope-change [review] — Mid-sprint scope changes destroying focus?
- [ ] ado-delivery-planner.antipattern.water-scrum-fall [review] — Sprint Zero + hardening sprint + "release sprint" separate from feature sprints?
  - Severity: critical
- [ ] ado-delivery-planner.antipattern.carry-over-culture [review] — Items routinely roll across sprints; teams lie about "done"?
- [ ] ado-delivery-planner.antipattern.sprint-extension [review] — Lengthening sprint to "make the goal"?
- [ ] ado-delivery-planner.antipattern.solo-silo [review] — Each dev owns their story; many "in progress" near sprint end (limit team-level WIP; pair/mob when one story risks slipping)?
- [ ] ado-delivery-planner.antipattern.task-micromanagement [review] — Sub-2-hour tasks; hourly tracking?
- [ ] ado-delivery-planner.antipattern.goal-then-forget [review] — Sprint goal written, never referenced until retro?
- [ ] ado-delivery-planner.antipattern.refinement-equals-planning [review] — Refinement = sprint planning (DoR not honored upstream)?
- [ ] ado-delivery-planner.antipattern.design-handoff [review] — Design tasks not in the same story as engineering tasks (water-scrum-fall in disguise)?

---

## Class-of-issue extrapolation `[review]`

- "Sprint goal 'Enhance shopping cart' lacks metric — also look at: every sprint goal in the last 4 sprints; how many follow goal+method+metric template?"

---

## What "no issues found" requires (review mode)

- Tasks ≤1 day; non-code tasks included; integration risk sequenced
- Capacity formula applied; focus factor 0.6-0.8; PTO/ceremonies/on-call deducted
- Sprint goal has goal + method + metric; not compound
- Velocity discipline (completed only, rolling avg, never cross-team, never KPI)
- Flow metrics with WIP limits + SLE + work-item age
- Bug cap respected
- Dependencies surfaced at planning
- Anti-patterns absent

---

## Generation/consult mode usage

In task decomposition: confirm INVEST → pick pattern (component / layer / activity / skill) → 1-day rule → include non-code tasks → sequence for integration risk early.

In capacity planning: apply formula; budget for PTO + ceremonies + on-call + incident buffer.

In sprint goal: goal + method + metric; pass boss's-boss test.

In flow diagnosis: pull cycle time / lead time / throughput / WIP / age; read CFD; apply Little's Law; check DORA; surface the constraint (TOC).

---

## Refinement notes

(none yet)
