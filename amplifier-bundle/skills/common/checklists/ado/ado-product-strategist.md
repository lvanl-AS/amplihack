# ado-product-strategist checklist

**Source**: `.claude/agents/ado-product-strategist.md` — Rumelt *Good Strategy/Bad
Strategy* (Diagnosis → Guiding Policy → Coherent Actions); Cagan's 4 product risks;
RICE/ICE/MoSCoW/Kano/WSJF; JTBD lineages (Christensen / Ulwick / Moesta); Cutler
"12 Signs You're Working in a Feature Factory"; Stripe trapdoor decisions; DRI / Informed Captain.

**Refinement IDs**: `ado-product-strategist.<category>.<item>`.

This agent is BOTH review-mode (audit a strategy doc / proposed feature) AND
generation-mode (consult on prioritization / vetting). Mode tags matter.

---

## Mandatory verifications

### Strategy kernel (Rumelt)
- [ ] ado-product-strategist.kernel.diagnosis [all] — Diagnosis of "what's actually going on" present (not just goals)?
  - Severity: critical when missing
- [ ] ado-product-strategist.kernel.guiding-policy [all] — Guiding policy ("the bet") articulated, not a wish list?
- [ ] ado-product-strategist.kernel.coherent-actions [all] — Actions reinforce each other; the set is coherent (not a portfolio of independent items)?

### Cagan's 4 product risks (every initiative must address)
- [ ] ado-product-strategist.risk.value [all] — Value risk: will customers buy / use it?
- [ ] ado-product-strategist.risk.usability [all] — Usability risk: can they figure out how?
- [ ] ado-product-strategist.risk.feasibility [all] — Feasibility risk: can we build it?
- [ ] ado-product-strategist.risk.viability [all] — Viability risk: does our business model support it?

### Cagan's 10 vetting questions
- [ ] ado-product-strategist.vetting.unanswered-flagged [all] — Each of Cagan's 10 questions answered, or unanswered ones explicitly flagged?

### Prioritization framework fit
- [ ] ado-product-strategist.prio.framework-fits [all] — Framework chosen matches situation:
  - RICE — mid-large org, defensible cross-product
  - ICE — growth experiments, fast iteration
  - MoSCoW — timeboxed delivery, MVP definition
  - Kano — differentiation in commodity markets
  - WSJF — SAFe / dependency-heavy
  - Cost of Delay — executive trade-offs
- [ ] ado-product-strategist.prio.consistent-scale [review] — Single scoring scale across the backlog? No half RICE / half t-shirts?

### Outcome vs output discipline
- [ ] ado-product-strategist.outcome.not-output [all] — Roadmap items expressed as outcomes ("activation up 15pp"), not outputs ("ship X")?
  - Severity: critical when output-driven roadmap with dates
- [ ] ado-product-strategist.outcome.evidence-not-hippo [all] — Evidence-based, not "the SVP wants this"? (Amazon Fire Phone $170M lesson)

### Decision accountability
- [ ] ado-product-strategist.decision.dri-named [all] — Significant decision has a named DRI / Informed Captain / DACI?
  - Severity: critical when decision-by-committee
- [ ] ado-product-strategist.decision.trapdoor-classified [generation] — Reversibility classified (Stripe trapdoor framework); deliberation budget proportional?

### Feature lifecycle
- [ ] ado-product-strategist.lifecycle.exit-criteria [all] — Exit criteria defined at launch (usage threshold + horizon)? 5D Sunset Strategy applicable?

### Anti-patterns to flag
- [ ] ado-product-strategist.antipattern.solution-shaped-problem [review] — "Users want a button" (solution) flagged; rewrite as problem?
- [ ] ado-product-strategist.antipattern.feature-factory [review] — Cutler's 12 signs (no measurement, success theater, large batches, no scrapped work)?
- [ ] ado-product-strategist.antipattern.sunk-cost [review] — "We've invested X so we have to ship" — flagged?
- [ ] ado-product-strategist.antipattern.vision-as-strategy [review] — Aspirations without diagnosis/policy/actions kernel?

---

## Class-of-issue extrapolation `[review]`

- "Output-driven roadmap item 'ship checkout v2' — also look at: every roadmap item; is anything else expressed as ship-X-by-Y instead of outcome?"

---

## What "no issues found" requires (review mode)

- Strategy kernel present (diagnosis + policy + coherent actions)
- All 4 risks addressed
- Cagan's 10 vetted
- Right framework for situation
- Outcomes not outputs
- DRI named
- Anti-patterns absent

---

## Generation/consult mode usage

In vetting: restate problem in plain English (not solution); run Cagan's 10; identify dominant risk; score with right framework; surface alternatives.

In prioritization: confirm outcome being moved (not just "value"); pick framework fitting maturity; apply consistently; watch for sandbagging / framework gaming / necessary-but-not-sufficient items.

In strategy diagnosis: identify diagnosis (what's actually going on?), articulate guiding policy (the bet), list coherent actions; flag fluff and "vision mistaken for strategy."

---

## Refinement notes

(none yet)
