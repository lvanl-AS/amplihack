# ado-discovery-coach checklist

**Source**: `.claude/agents/ado-discovery-coach.md` — Teresa Torres *Continuous
Discovery Habits* + Opportunity Solution Trees; Cagan's 4 product risks; Rob
Fitzpatrick *The Mom Test*; Eric Ries *Lean Startup* (MVP-as-experiment); Alberto
Savoia pretotyping; Steve Blank Customer Development; Bob Moesta Switch interviews
+ Four Forces of Progress; Jake Knapp Design Sprints.

**Refinement IDs**: `ado-discovery-coach.<category>.<item>`.

---

## Mandatory verifications

### Outcome framing
- [ ] ado-discovery-coach.outcome.behavior-not-feature [all] — Idea restated as an outcome we're trying to move (behavior change), not a feature to ship?
  - Severity: critical when feature-disguised-as-outcome

### Opportunity Solution Tree
- [ ] ado-discovery-coach.ost.outcome-top [generation] — Outcome at top of tree?
- [ ] ado-discovery-coach.ost.opportunities-from-research [generation] — Opportunities derived from customer research, not invented?
- [ ] ado-discovery-coach.ost.three-parallel-solutions [generation] — At least 3 candidate solutions per opportunity (parallelism beats single-track)?

### Assumption mapping
- [ ] ado-discovery-coach.assumption.listed [all] — Assumptions per solution explicitly listed?
- [ ] ado-discovery-coach.assumption.ranked-by-risk [all] — Ranked by (probability of being wrong) × (impact if wrong) — RAT?
- [ ] ado-discovery-coach.assumption.cheapest-test [all] — Cheapest test for the riskiest assumption identified?

### Cagan's 4 risks addressed
- [ ] ado-discovery-coach.risk.value [all] — Value risk: will customers buy / use it?
- [ ] ado-discovery-coach.risk.usability [all] — Usability: can they figure out how?
- [ ] ado-discovery-coach.risk.feasibility [all] — Feasibility: can we build it?
- [ ] ado-discovery-coach.risk.viability [all] — Viability: does our model support it?

### Customer interviews (Mom Test discipline)
- [ ] ado-discovery-coach.interview.generative-vs-evaluative [generation] — Generative (find unknown unknowns) vs evaluative (test specific solution) distinguished?
- [ ] ado-discovery-coach.interview.about-their-life [all] — About THEIR life, not our idea?
  - Severity: critical when leading questions
- [ ] ado-discovery-coach.interview.specifics-past-not-opinions-future [all] — Specifics in the past ("walk me through the last time you...") NOT opinions of the future ("would you use...")?
- [ ] ado-discovery-coach.interview.5-minimum [generation] — At least 5 interviews per round (Nielsen)?
  - Severity: warning when sample of one
- [ ] ado-discovery-coach.interview.no-leading [all] — No "Don't you think this is great?"-style leading questions?

### Experiment selection (cheapest first)
- [ ] ado-discovery-coach.experiment.lightest-fits [all] — Lightest experiment that resolves the question:
  - Pretotype (hours) → does the *idea* resonate?
  - Fake door / smoke test (days) → demand?
  - Landing page / pre-order (days) → demand + WTP?
  - Concierge MVP (1-4 weeks) → manual experience value?
  - Wizard of Oz (1-4 weeks) → automated experience value?
  - Single-feature MVP (weeks) → core feature alone enough?
- [ ] ado-discovery-coach.experiment.success-defined-upfront [all] — Success metric AND decision rule defined BEFORE running?
  - Severity: critical when undefined
- [ ] ado-discovery-coach.experiment.duration-audience [generation] — Duration + audience size pre-set?
- [ ] ado-discovery-coach.experiment.clean-termination [generation] — Clean termination plan (especially fake doors — "coming soon" must be honest)?

### Continuous discovery cadence
- [ ] ado-discovery-coach.cadence.weekly [generation] — Weekly customer touchpoints by the team building (not handed off)?
  - Less than weekly = episodic research, NOT continuous discovery.
- [ ] ado-discovery-coach.cadence.trio-attends [generation] — PM + designer + tech lead attend; not delegated to a research team (Cagan's "very damaging" pattern)?

### Anti-patterns
- [ ] ado-discovery-coach.antipattern.skip-discovery [review] — Skip discovery → ship → fail (the most expensive validation)?
  - Severity: critical
- [ ] ado-discovery-coach.antipattern.discovery-as-phase [review] — "Discovery sprint" then handoff to delivery? (Waterfall in disguise.)
- [ ] ado-discovery-coach.antipattern.mvp-as-shippable [review] — MVP treated as "minimum shippable product" instead of experiment (Ries explicit definition)?
- [ ] ado-discovery-coach.antipattern.feature-wishlist-as-data [review] — Customer feature wishes treated as evidence?
- [ ] ado-discovery-coach.antipattern.hypothetical-fluff [review] — "I might use it" treated as commitment?
- [ ] ado-discovery-coach.antipattern.achieving-failure [review] — Flawless execution of the wrong plan (Drucker)?

---

## Class-of-issue extrapolation `[review]`

- "Single interview cited as evidence — also look at: every claim in this discovery doc; how many are backed by 5+ interviews vs 1?"

---

## What "no issues found" requires (review mode)

- Outcome (not feature) framing
- OST with research-derived opportunities + 3 parallel solutions
- Assumptions ranked by risk; cheapest test for riskiest
- All 4 Cagan risks addressed
- Mom Test interview discipline
- Right-sized experiment with pre-defined success metric + decision rule
- Continuous (weekly) cadence; trio attends

---

## Generation/consult mode usage

Discovery planning: outcome → OST → assumptions → RAT → cheapest test → success threshold.

Interview design: generative vs evaluative; Mom Test rules; story-based prompts; 5+ per round.

Experiment design: lightest experiment; metric + decision rule pre-set; clean termination.

Design Sprint: confirm 4-7 people + Decider + dedicated week; Mon-Fri structure; output is validated direction or saved cost.

---

## Refinement notes

(none yet)
