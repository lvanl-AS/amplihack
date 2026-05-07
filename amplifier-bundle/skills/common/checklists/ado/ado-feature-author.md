# ado-feature-author checklist

**Source**: `.claude/agents/ado-feature-author.md` — Amazon PR-FAQ + Working Backwards
+ banned PowerPoint (Bezos 2004); Shape Up Pitch (Singer/Basecamp); Figma 3-section
PRD (Yamashita); Intercom Intermission; Linear minimalist; Lenny's 1-Pager; Stripe
memo culture + trapdoor decisions; LaunchDarkly progressive delivery (deploy ≠ release).

**Refinement IDs**: `ado-feature-author.<category>.<item>`.

---

## Mandatory verifications

### Problem-first framing
- [ ] ado-feature-author.problem.first [all] — Problem statement before any solution language?
  - Severity: critical when solution disguised as problem ("users need a notifications panel" vs "users miss state changes")
- [ ] ado-feature-author.problem.customer-terms [all] — Problem framed in customer terms, not internal terms (codenames, system names)?
- [ ] ado-feature-author.problem.plain-english [all] — Plain English; a stranger could read it once and explain the bet back?

### Format choice
- [ ] ado-feature-author.format.matches-bet [all] — Format matches the org and bet size:
  - PR-FAQ — big new product/capability, multi-team, year+ initiative
  - Shape Up Pitch — discrete 6-week bet, single team, fixed appetite
  - Figma 3-section PRD — cross-functional with launch coordination
  - Intercom Intermission — internal change, fits one A4 page
  - Linear minimalist — small team, high taste alignment
  - Lenny 1-pager — default for most projects

### Standard sections (lightweight 1-pager)
- [ ] ado-feature-author.section.hypothesis [all] — Hypothesis / solution sketch with embedded designs (not linked)?
- [ ] ado-feature-author.section.scope-no-gos [all] — Scope: what's IN, what's OUT, explicit no-gos?
  - Severity: critical when no-gos missing (scope creep absorption surface)
- [ ] ado-feature-author.section.success-metrics [all] — Success metrics (leading + lagging), with baseline + target + prediction-before-launch?
  - Severity: critical when only output ("ship by Q3") metric
- [ ] ado-feature-author.section.rollout [all] — Rollout strategy: feature flag plan, exposure progression (dark → canary → ring → GA), kill switch, A/B variant?
  - Severity: critical when treated as deploy-and-pray
- [ ] ado-feature-author.section.launch-checklist [generation] — Launch checklist: legal / security / marketing / support coordination?
- [ ] ado-feature-author.section.exit-criteria [all] — Exit criteria: usage threshold + horizon at which we'd sunset?
  - Severity: warning when missing (orphan code accumulates)
- [ ] ado-feature-author.section.open-questions [generation] — Open questions captured with named owner per item?

### PR-FAQ specific (when format chosen)
- [ ] ado-feature-author.prfaq.press-release-page-one [generation] — Page 1: headline + sub-headline + intro + customer problem + solution + customer quote + getting-started?
- [ ] ado-feature-author.prfaq.faq-pages-2-6 [generation] — Pages 2-6: customer FAQs + internal FAQs (why now, why us, P&L, unknowns)?

### Shape Up specific
- [ ] ado-feature-author.shapeup.appetite-set-first [generation] — Appetite ("worth 6 weeks of one team") set BEFORE designing?
- [ ] ado-feature-author.shapeup.right-altitude [generation] — Sketched neither too raw nor too speced?
- [ ] ado-feature-author.shapeup.rabbit-holes [generation] — Rabbit holes (places team could get stuck) identified?
- [ ] ado-feature-author.shapeup.no-gos-explicit [generation] — No-gos (out-of-scope variants) listed?

### Trapdoor classification (Stripe)
- [ ] ado-feature-author.trapdoor.classified [generation] — Decision reversibility classified; deliberation budget proportional?

### Anti-patterns
- [ ] ado-feature-author.antipattern.length-as-rigor [review] — Long PRD hiding weak thinking (short PRDs force clarity)?
- [ ] ado-feature-author.antipattern.no-success-metric [review] — No success metric, or output-only?
- [ ] ado-feature-author.antipattern.hidden-assumption [review] — "Users want X" without evidence — flag as assumption?
- [ ] ado-feature-author.antipattern.spec-as-handoff [review] — PM solo writes, throws over to engineering? (Trio must co-create.)
- [ ] ado-feature-author.antipattern.powerpoint-substitute [review] — Bullets and decks instead of narrative? (Amazon banned this for a reason.)
- [ ] ado-feature-author.antipattern.while-were-at-it [review] — Absorbed feature additions = unwritten scope creep?

---

## Class-of-issue extrapolation `[review]`

- "Solution-disguised-as-problem at intro paragraph — also look at: every section heading; do any others embed solution language?"

---

## What "no issues found" requires (review mode)

- Problem first, customer terms, plain English
- Format matches bet
- Lightweight sections present (hypothesis / scope+no-gos / metrics / rollout / launch / exit / open Qs)
- PR-FAQ or Shape Up specifics if those formats chosen
- Trio has weighed in
- Anti-patterns absent

---

## Generation/consult mode usage

In authoring: confirm problem statement first; pick format; lead with customer impact; success metrics with prediction-before-launch; explicit no-gos; embed designs; capture open questions with owners.

In shaping (Shape Up): set appetite first; sketch at right altitude; identify rabbit holes; list no-gos; remember pitch is a bet, not a commitment.

---

## Refinement notes

(none yet)
