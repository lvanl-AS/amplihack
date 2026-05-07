# ado-story-architect checklist

**Source**: `.claude/agents/ado-story-architect.md` — Connextra format (UK 2001),
3 C's (Jeffries 2001), INVEST (Wake 2003), SPIDR (Cohn) + Hamburger Method (Adzic) +
Lawrence/Green's 9 splitting patterns, Three Amigos (Dinwiddie), Story Mapping (Patton),
DoR/DoD, Gherkin Given/When/Then.

**Refinement IDs**: `ado-story-architect.<category>.<item>`.

This agent dispatches in BOTH generation mode (writing/splitting stories) and
review mode (grading INVEST, AC quality). Mode tags matter.

---

## Mandatory verifications

### Story format
- [ ] ado-story-architect.format.connextra [all] — "As a [persona], I want [capability], so that [benefit]" (or Job Story / Chris Matts variant)?
- [ ] ado-story-architect.format.real-persona [all] — Persona is a real research-based persona, NOT "as a developer..." or "as a system..."?
  - Severity: critical (those are tasks, not stories)
- [ ] ado-story-architect.format.benefit-articulated [all] — "So that..." benefit articulated? If you can't articulate the benefit, the story isn't worth doing.
  - Severity: critical when missing

### INVEST
- [ ] ado-story-architect.invest.independent [all] — Independent — not in a dependent chain (sign of horizontal slicing)?
- [ ] ado-story-architect.invest.negotiable [all] — Negotiable — not a 12-page spec dictating implementation?
- [ ] ado-story-architect.invest.valuable [all] — Valuable — user-visible value (refactor → not a story; enabler/task)?
  - Severity: critical when invisible-to-user
- [ ] ado-story-architect.invest.estimable [all] — Estimable — measurable AC ("page load < 2s on 4G"), not "improve performance"?
- [ ] ado-story-architect.invest.small [all] — Small — fits in one sprint? Not a mega-story (>13 pts)?
  - Severity: warning (mega-stories hide risk, defy estimation)
- [ ] ado-story-architect.invest.testable [all] — Testable — observable behaviors as AC?

### Acceptance criteria (Gherkin)
- [ ] ado-story-architect.ac.present [all] — 1-3 AC present?
  - Severity: critical when missing entirely (story undeliverable; review = opinion)
- [ ] ado-story-architect.ac.behavior-not-implementation [all] — "Then the user remains logged in across page reloads" (right) NOT "Then a JWT is stored in localStorage" (wrong)?
- [ ] ado-story-architect.ac.gwt-strict-order [generation] — Strict Given/When/Then ordering — outcomes not in Given, preconditions not in Then?
- [ ] ado-story-architect.ac.negative-path [all] — At least one AC for the unhappy path?

### Splitting (when too big)
- [ ] ado-story-architect.split.spidr-walked [generation] — SPIDR walked top to bottom (Spike → Paths → Interfaces → Data → Rules)?
- [ ] ado-story-architect.split.vertical-not-horizontal [all] — Slices vertical (cut through UI → API → business → data), NOT horizontal (UI-only / backend-only)?
  - Severity: critical when horizontal at story level
- [ ] ado-story-architect.split.each-passes-invest [all] — Each slice independently passes INVEST (especially Valuable)?

### Story mapping
- [ ] ado-story-architect.map.backbone-walking-skeleton [generation] — Backbone (top-row activities), walking skeleton (user tasks), body (stories), MVP slice line?
- [ ] ado-story-architect.map.4-lenses [generation] — Patton's 4 lenses for MVP slicing: Differentiator / Spoiler / Cost reducer / Table stakes?

### Definition of Ready (optional but recommended)
- [ ] ado-story-architect.dor.checklist [generation] — Story follows template; AC defined; persona real; dependencies resolved; small enough for one sprint; designs attached if UI-facing; INVEST satisfied; estimable.

### Anti-patterns
- [ ] ado-story-architect.antipattern.developer-as [review] — "As a developer I want..." — task, not story?
  - Severity: critical
- [ ] ado-story-architect.antipattern.no-ac [review] — Stories without AC?
- [ ] ado-story-architect.antipattern.story-as-spec [review] — Long prose in the card violates 3 C's; push detail into AC?
- [ ] ado-story-architect.antipattern.solution-statement [review] — "Use Redis for session storage" — rewrite as the problem?

---

## Class-of-issue extrapolation `[review]`

- "Story missing AC at AB#1234 — also look at: every story in this sprint; do any others have empty / placeholder AC?"

---

## What "no issues found" requires (review mode)

- Connextra (or variant) format with real persona + benefit
- INVEST passes letter-by-letter
- 1-3 AC behavior-focused, GWT-ordered, negative path included
- No mega-story, no horizontal slice, no developer-as-persona
- DoR satisfied (when used)

---

## Generation/consult mode usage

In authoring: anchor to a real persona; lead with benefit; 1-3 AC in Gherkin; validate INVEST; embed designs; explicit out-of-scope notes.

In splitting: confirm parent is genuinely too big; walk SPIDR top-to-bottom; fall back to hamburger if team thinks technically; each slice passes INVEST; refuse horizontal layers.

In story mapping: backbone → walking skeleton → body; MVP slice via Patton's 4 lenses.

---

## Refinement notes

(none yet)
