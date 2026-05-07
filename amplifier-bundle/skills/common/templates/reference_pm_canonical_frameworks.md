# PM Canonical Frameworks Reference

Reference material for agents. Never mention framework names to users — use the concepts in plain English.

---

## Prioritization

### RICE
- **Reach**: How many users affected in a time period
- **Impact**: How much each user is affected (minimal / low / medium / high / massive)
- **Confidence**: How sure are we about estimates (high / medium / low)
- **Effort**: Person-months of work
- Score = (Reach x Impact x Confidence) / Effort

### Cagan's Four Risks
Evaluate every feature against:
1. **Value risk**: Will users choose to use it?
2. **Usability risk**: Can users figure out how to use it?
3. **Feasibility risk**: Can engineering build it?
4. **Business viability risk**: Does it work for the business (legal, financial, brand)?

### MoSCoW
- **Must have**: Non-negotiable for the release
- **Should have**: Important but not critical
- **Could have**: Nice to have, include if easy
- **Won't have (this time)**: Explicitly deferred

## Discovery & Validation

### Jobs to Be Done (JTBD)
"When [situation], I want to [motivation], so I can [expected outcome]."
Focus on the job the user is trying to accomplish, not the solution.

### Opportunity Solution Trees (Teresa Torres)
- Start with a desired outcome
- Map opportunities (user pain points / needs)
- Generate multiple solutions per opportunity
- Design experiments to test assumptions

### Assumption Mapping
Plot assumptions on a 2x2:
- X-axis: Evidence (none → strong)
- Y-axis: Impact if wrong (low → catastrophic)
- Top-left quadrant = test first (high impact, no evidence)

## Goal Setting

### OKRs (Objectives and Key Results)
- **Objective**: Qualitative, ambitious, time-bounded, inspiring
- **Key Results**: 2-5 measurable outcomes (not tasks/activities)
  - Bad KR: "Launch feature X" (that's a task)
  - Good KR: "Reduce support contacts by 25%"
- Grading: 0.0-1.0 scale. 0.7 = success (stretch targets)

### North Star Metric
Single metric that captures the core value delivered to users.
- Must be measurable, cross-functional, and a leading indicator
- Supported by 3-5 input metrics that drive it

## Story Quality

### INVEST
- **Independent**: Can be developed without depending on other stories
- **Negotiable**: Details can be discussed, not a contract
- **Valuable**: Delivers value to the user or business
- **Estimable**: Team can roughly size it
- **Small**: Fits in a single sprint
- **Testable**: Clear pass/fail criteria exist

### SPIDR Splitting
When a story is too big, split by:
- **Spike**: Research unknowns first
- **Paths**: Different user flows / happy vs error path
- **Interfaces**: Different platforms / channels
- **Data**: Different data types or sources
- **Rules**: Different business rules or edge cases

### Vertical Slicing
Every story cuts through all layers (UI → API → DB). Never split horizontally ("build the API" / "build the UI" as separate stories).

### Story Mapping (Jeff Patton)
- **Backbone**: High-level user activities (left to right)
- **Walking skeleton**: Minimum viable path through each activity
- **Body**: Additional stories that enrich each activity, prioritized top to bottom

## Metrics

### AARRR (Pirate Metrics)
Acquisition → Activation → Retention → Revenue → Referral.
Identify which stage the feature targets.

### HEART (Google UX)
- **Happiness**: User satisfaction (surveys, NPS)
- **Engagement**: Frequency, depth of interaction
- **Adoption**: New users of a feature
- **Retention**: Continued use over time
- **Task success**: Completion rate, time on task, errors

### DORA (DevOps Research & Assessment)
- Deployment frequency
- Lead time for changes
- Change failure rate
- Time to restore service

### Metric Anti-Patterns
- Vanity metrics (total signups vs active users)
- No baseline established before launch
- Lagging-only indicators (revenue) without leading indicators (engagement)
- Metric overload (>5 metrics per feature)
- Sandbagging targets to guarantee "success"
