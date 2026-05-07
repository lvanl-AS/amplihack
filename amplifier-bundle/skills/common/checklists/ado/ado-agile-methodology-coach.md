# ado-agile-methodology-coach checklist

**Source**: `.claude/agents/ado-agile-methodology-coach.md` — 2020 Scrum Guide;
Anderson Kanban + STATIK; Beck XP; Poppendieck Lean (7 wastes); Goldratt TOC + 5
Focusing Steps; Forsgren/Humble/Kim DORA + Three Ways; Ron Jeffries Dark Scrum;
Verwijs/Schartau Zombie Scrum; Fowler "Agile Industrial Complex"; Atlassian Health
Monitor.

**Refinement IDs**: `ado-agile-methodology-coach.<category>.<item>`.

---

## Mandatory verifications

### Framework selection
- [ ] ado-agile-methodology-coach.framework.context-first [all] — Diagnosis of context (team size, criticality, customer access, regulatory load, distribution) BEFORE picking framework?
- [ ] ado-agile-methodology-coach.framework.not-default-scrum [all] — Don't default to Scrum without reason?
- [ ] ado-agile-methodology-coach.framework.matches-context [all] — Framework matches situation (matrix above):
  - Scrum — single product team, regular cadence, evolving requirements
  - Kanban — ops, support, maintenance, mixed-priority, continuous demand
  - Scrumban — Scrum team adopting flow thinking; maintenance teams
  - XP — engineering practices regardless of shell
  - LeSS / Nexus — multi-team Scrum
  - SAFe — large enterprise needing structure (with eyes open to bureaucracy critique)
  - Crystal — small teams; methodology weight tuned to size/criticality

### Engineering practices (regardless of framework)
- [ ] ado-agile-methodology-coach.engineering.xp-substance [all] — XP practices (TDD, pairing/mobbing, refactoring, CI, simple design) adopted regardless of process shell?
  - Severity: critical when missing (Dark Scrum surface)

### Ceremonies
- [ ] ado-agile-methodology-coach.ceremony.connected-to-purpose [review] — Each ceremony connected to its purpose; ceremonies that lost purpose dropped?
- [ ] ado-agile-methodology-coach.ceremony.refinement-10pct [generation] — Refinement at ~10% capacity, weekly (not "refinement = sprint planning")?
- [ ] ado-agile-methodology-coach.ceremony.planning-3-topics [generation] — Sprint planning's 3 topics (Why valuable / What can be done / How will it be done), not legacy Part 1/Part 2 split?
- [ ] ado-agile-methodology-coach.ceremony.review-stakeholder-feedback [generation] — Sprint Review = stakeholder feedback, NOT status theater?

### DORA reality check
- [ ] ado-agile-methodology-coach.dora.pulled-first [all] — DORA metrics pulled BEFORE defending the process (deployment freq / lead time / change failure rate / MTTR / reliability)?
  - Severity: critical (a team with great Scrum ceremonies and Low DORA is in process theater)

### Anti-pattern detection
- [ ] ado-agile-methodology-coach.antipattern.dark-scrum [review] — Dark Scrum (Jeffries): Scrum used as a whip, velocity as KPI, no engineering practices, "done" doesn't mean releasable?
  - Severity: critical
- [ ] ado-agile-methodology-coach.antipattern.zombie-scrum [review] — Zombie Scrum (Verwijs/Schartau): all ceremonies on cadence, no working software ships, no stakeholder contact, no improvement?
  - Severity: critical
- [ ] ado-agile-methodology-coach.antipattern.water-scrum-fall [review] — Sprint Zero + long upstream requirements + hardening sprint at the end + DoD that excludes deployment?
  - Severity: critical
- [ ] ado-agile-methodology-coach.antipattern.cargo-cult-spotify [review] — "Squads/tribes/chapters" labels without psychological safety / trust / real autonomy (Kniberg himself begs people not to copy)?
- [ ] ado-agile-methodology-coach.antipattern.industrial-complex [review] — Capital-A Agile (certification economy) without lowercase-agile (mindset)?

### Lean Software Development (Poppendieck)
- [ ] ado-agile-methodology-coach.lean.7-wastes [generation] — 7 wastes (partially done work / extra features / relearning / handoffs / task switching / delays / defects) actively reduced?
- [ ] ado-agile-methodology-coach.lean.value-stream-mapping [generation] — Value Stream Mapping separates value-add / necessary-non-value-add / pure waste?

### Theory of Constraints (Goldratt)
- [ ] ado-agile-methodology-coach.toc.5-focusing-steps [generation] — Five Focusing Steps applied (Identify → Exploit → Subordinate → Elevate → Repeat)?
- [ ] ado-agile-methodology-coach.toc.constraint-named [all] — System constraint identified before optimizing locally?

### Three Ways (Gene Kim)
- [ ] ado-agile-methodology-coach.three-ways.flow [generation] — Flow (left-to-right, systems thinking) prioritized?
- [ ] ado-agile-methodology-coach.three-ways.feedback [generation] — Feedback (right-to-left, fast and amplified, fail forward)?
- [ ] ado-agile-methodology-coach.three-ways.continual-learning [generation] — Continual learning + experimentation (deliberate failure injection)?

---

## Class-of-issue extrapolation `[review]`

- "Velocity used as KPI in PR description — also look at: every retro action item, every status meeting agenda; is velocity weaponized elsewhere?"

---

## What "no issues found" requires (review mode)

- Framework matches context (not defaulted to Scrum)
- XP-style engineering practices present regardless of framework
- Ceremonies connected to purpose; refinement is healthy; planning has 3 topics; review = real stakeholder feedback
- DORA pulled and respectable
- Dark Scrum / Zombie Scrum / water-scrum-fall / cargo-cult / Industrial-Complex antipatterns absent

---

## Generation/consult mode usage

In selection: diagnose context first → match framework → recommend XP regardless → identify cost of overhead.

In ceremony design: time-box per 2020 Scrum Guide; connect each to purpose; healthy refinement; 3-topic planning; stakeholder-feedback review.

In health diagnosis: pull DORA first; watch for Dark / Zombie / water-scrum-fall / cargo-cult / Industrial Complex; surface symptoms with evidence.

---

## Refinement notes

(none yet)
