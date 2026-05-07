# ado-metrics-coach checklist

**Source**: `.claude/agents/ado-metrics-coach.md` — Drucker MBO → Grove iMBOs →
Doerr OKRs → Google → *Measure What Matters*; Christina Wodtke *Radical Focus*;
Ravi Mehta NCTs; AARRR (McClure); HEART (Rodden et al., Google UX); DORA;
North Star metric; Sean Ellis PMF Test ("very disappointed" 40%+); Cutler
outputs-vs-outcomes-vs-impact.

**Refinement IDs**: `ado-metrics-coach.<category>.<item>`.

---

## Mandatory verifications

### Outcome over output
- [ ] ado-metrics-coach.outcome.not-output [all] — Metric is an outcome ("checkout conversion +5%"), NOT an output ("ship checkout v2")?
  - Severity: critical when KR is a task

### Leading + lagging pair
- [ ] ado-metrics-coach.indicator.leading-defined [all] — Leading indicator (predictive, actionable) defined?
- [ ] ado-metrics-coach.indicator.lagging-defined [all] — Lagging indicator (proves it worked, longer horizon) defined?
- [ ] ado-metrics-coach.indicator.not-lagging-only [all] — Not lagging-only (too slow to inform iteration)?
  - Severity: warning

### Baseline + target + prediction
- [ ] ado-metrics-coach.metric.baseline [all] — Baseline value documented?
  - Severity: critical when "increase 5%" without saying from what
- [ ] ado-metrics-coach.metric.target [all] — Target with time horizon?
- [ ] ado-metrics-coach.metric.prediction-before-launch [all] — Expected magnitude written down before launch (compared in retro)?

### OKR discipline (when using OKRs)
- [ ] ado-metrics-coach.okr.objective-qualitative [generation] — Objective qualitative, ambitious, time-bounded, inspiring (not a task)?
- [ ] ado-metrics-coach.okr.3-5-krs [generation] — 3-5 KRs per O?
- [ ] ado-metrics-coach.okr.necessary-and-sufficient [all] — Hitting 1.0 on every KR genuinely delivers the Objective (necessary AND sufficient)?
  - Severity: critical when not (Wodtke's #5 OKR mistake)
- [ ] ado-metrics-coach.okr.stretch [all] — Stretch target (consistent 1.0 = sandbagging)?
- [ ] ado-metrics-coach.okr.not-tied-to-comp [all] — NOT tied to compensation (drives sandbagging — Wodtke's #4)?
  - Severity: critical
- [ ] ado-metrics-coach.okr.weekly-checkins [generation] — Weekly check-ins, not "set and forget"?
- [ ] ado-metrics-coach.okr.value-objective [all] — Hitting 1.0 actually changes something (no Low-Value Objectives)?

### North Star
- [ ] ado-metrics-coach.northstar.captures-value [generation] — Captures value the product DELIVERS, not revenue (revenue is downstream)?
- [ ] ado-metrics-coach.northstar.cross-functional [generation] — Every team can affect it?
- [ ] ado-metrics-coach.northstar.leading-of-revenue [generation] — Moves before revenue moves?

### Framework selection
- [ ] ado-metrics-coach.framework.fits-org [all] — Framework matches org needs:
  - OKRs — strategic alignment, change-driving
  - NCTs — when work doesn't reduce to one moving number
  - North Star — single org-wide directional metric
  - AARRR — growth funnel diagnosis
  - HEART — feature-level UX
  - DORA — engineering delivery
  - Metric tree — connecting feature metrics to business outcomes

### Decision rule
- [ ] ado-metrics-coach.decision.rule-pre-defined [all] — What we do at 0.7 / 1.0 / miss — pre-defined?
  - Severity: warning when "metric without a decision rule"

### Anti-patterns
- [ ] ado-metrics-coach.antipattern.kr-as-task [review] — Most common OKR failure: KRs as tasks?
  - Severity: critical
- [ ] ado-metrics-coach.antipattern.vanity [review] — MAU / downloads / signups without quality qualifier?
- [ ] ado-metrics-coach.antipattern.metric-overload [review] — 20 KPIs nobody acts on?
- [ ] ado-metrics-coach.antipattern.compounded-objective [review] — Multiple goals shoved together; nothing is the focus?
- [ ] ado-metrics-coach.antipattern.activity-metric [review] — "200 customer calls" instead of "X% conversion improvement"?
- [ ] ado-metrics-coach.antipattern.cascading-rigidly [review] — Top-down dictate without bidirectional alignment?

---

## Class-of-issue extrapolation `[review]`

- "KR-as-task at OKR-3 — also look at: every other KR; how many are 'ship X' vs 'X drives Y behavior'?"

---

## What "no issues found" requires (review mode)

- Outcomes not outputs
- Leading + lagging pair, with baseline + target + prediction
- OKR rules respected (necessary-AND-sufficient, stretch, not-comp-tied, weekly check-ins, value Objective)
- Right framework for situation
- Decision rule pre-defined
- Anti-patterns absent

---

## Generation/consult mode usage

In OKR authoring: Objective qualitative; 3-5 KRs each measurable outcome; necessary AND sufficient check; stretch; quarterly cadence.

In metric design: outcome before output; pair leading + lagging; predict the metric before launch; layer North Star + AARRR + HEART; metric tree linking feature → business outcome.

In North Star selection: capture product value (not revenue), cross-functional, leading of revenue.

---

## Refinement notes

(none yet)
