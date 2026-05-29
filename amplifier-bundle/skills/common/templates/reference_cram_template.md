# CRAM — Change Risk Assessment Matrix Template

Reference template for the CRAM scoring workflow. Sourced from the Alaska Airlines Change Risk Assessment Matrix.

## Scoring Scale

Each subcriterion is scored 1-3:
- **1** = Low Risk — Safe, routine changes with low complexity and predictable outcomes
- **2** = Medium Risk — Moderately complex changes that require oversight, scheduling review, and leadership review
- **3** = High Risk — Significant risk of major incidents, requires senior leadership review, stringent controls, and strategic scheduling

## Category 1: Business Impact (Weight = 3)

**Scoring: Highest subcriterion score × 3**

The biggest driver — what could this break?

### 1a. System Criticality

| Score | Criteria |
|---|---|
| 1 | Tier 3 or Tier 4 systems; impacts a single department |
| 2 | Tier 2 systems; impacts a single site or multiple departments |
| 3 | Tier 0 or Tier 1 systems OR impacts multiple sites / critical operations |

### 1b. Customer Impact

| Score | Criteria |
|---|---|
| 1 | No potential customer impact; internal-only change |
| 2 | Limited potential customer impact; minor service degradation or short outage |
| 3 | Significant potential customer impact; major outage or service disruption |

### 1c. Regulatory Compliance

| Score | Criteria |
|---|---|
| 1 | No compliance implications |
| 2 | Minor compliance considerations; documented and approved |
| 3 | High compliance risk; regulatory breach possible if change fails |

**Data sources:** ADO Context Expert (user journeys, business criticality, compliance mentions), Code Changes Expert (repos/systems involved, tier classification)

## Category 2: Execution Risk (Weight = 2)

**Scoring: Average of subcriterion scores × 2**

The second driver — how hard is it to do safely?

### 2a. Change Complexity

| Score | Criteria |
|---|---|
| 1 | Simple change; 1-2 teams, single system, few steps, minimal risk, limited scope, predictable outcome |
| 2 | Moderate complexity; 3-4 teams, one complex system or minor integration |
| 3 | High complexity; 5+ teams, multiple systems, deep integration, unpredictable outcomes |

### 2b. Testing Coverage

| Score | Criteria |
|---|---|
| 1 | Fully tested, evidence available, low risk |
| 2 | Partially tested, failed test cases, risk acknowledged, acceptable with oversight |
| 3 | Untested or failed, no mitigation; high risk if deployed |

### 2c. Rollback Feasibility

| Score | Criteria |
|---|---|
| 1 | Easy rollback; < 30 minutes |
| 2 | Moderate rollback; 30 min to 2 hours |
| 3 | Difficult rollback; > 2 hours or requires major recovery effort |

**Data sources:** Code Changes Expert (repo count, team count, test files, PR status), pipeline data (rollback time estimates), ADO Context Expert (story states, AC completeness)

## Category 3: Operational Risk (Weight = 1)

**Scoring: Average of subcriterion scores × 1**

Still important, but lighter weight — are we truly ready to run it now?

### 3a. Change Window

| Score | Criteria |
|---|---|
| 1 | No outage expected or within the Approved Maintenance Window |
| 2 | Outage occurring during Off-Hours (22:30-04:49) or during the weekend Soft-Freeze |
| 3 | Outage during Peak / Business Hours / Pre-Flight / Global Ops (05:00-17:00) or during a Hard Freeze |

### 3b. Operational Readiness

| Score | Criteria |
|---|---|
| 1 | All documentation, observability, approvals, and resources confirmed; support teams ready |
| 2 | Some gaps in documentation, observability, or readiness; mitigations in place |
| 3 | Significant gaps; unclear ownership or missing approvals |

### 3c. Vendor Dependency

| Score | Criteria |
|---|---|
| 1 | No vendor involvement; fully internal |
| 2 | Vendor involvement for minor tasks or advisory |
| 3 | Vendor dependency for critical tasks; delays or coordination risks |

### 3d. Secure Coding

| Score | Criteria |
|---|---|
| 1 | Standard Quality Gate (or higher) is used; No Critical or High vulnerabilities are present |
| 2 | Security Plus or Security Quality Gate is used; Unresolved security hotspots are present |
| 3 | No Quality Gate is configured; Critical or High vulnerabilities exist, and security hotspots remain unresolved |

### 3e. Resilience & Recovery (RR)

| Score | Criteria |
|---|---|
| 1 | RR plan fully automated, tested successfully, and evidence demonstrating less than 1 hour total elapsed time for recovery prior to outside validation |
| 2 | RR plan tested and lacking full automation or with issues remediated without re-testing; Recovery process is < 2 hours total elapsed time for recovery prior to outside validation |
| 3 | No RR testing evidence; recovery plan unverified and/or recovery process is > 2 hours total elapsed time for recovery prior to outside validation |

**Data sources:** CR document (deployment window, operational readiness), Code Changes Expert (vendor dependencies, security scan results), pipeline data (RR testing evidence, recovery time)

## Overall Risk Score

**Formula:**
- Business Impact weighted score = **highest** of (1a, 1b, 1c) × 3
- Execution Risk weighted score = **average** of (2a, 2b, 2c) × 2
- Operational Risk weighted score = **average** of (3a, 3b, 3c, 3d, 3e) × 1
- **Total** = Business Impact + Execution Risk + Operational Risk

| Total Weighted Score | Risk Level | Implications |
|---|---|---|
| 6-10 | **Low Risk** | Standard deployment process |
| 11-15 | **Medium Risk** | Requires oversight, scheduling review, and leadership review |
| 16-18 | **High Risk** | Requires senior leadership review, stringent controls, and strategic scheduling |

## Output Format

```markdown
## CRAM Risk Assessment

### Scores

| Category | Subcriterion | Score | Justification |
|---|---|---|---|
| **Business Impact** | System Criticality | X/3 | [justification] |
| | Customer Impact | X/3 | [justification] |
| | Regulatory Compliance | X/3 | [justification] |
| **Execution Risk** | Change Complexity | X/3 | [justification] |
| | Testing Coverage | X/3 | [justification] |
| | Rollback Feasibility | X/3 | [justification] |
| **Operational Risk** | Change Window | X/3 | [justification] |
| | Operational Readiness | X/3 | [justification] |
| | Vendor Dependency | X/3 | [justification] |
| | Secure Coding | X/3 | [justification] |
| | Resilience & Recovery | X/3 | [justification] |

### Weighted Scores

| Category | Method | Raw | Weight | Weighted Score |
|---|---|---|---|---|
| Business Impact | Highest of (X, X, X) | X | ×3 | X |
| Execution Risk | Average of (X, X, X) | X.X | ×2 | X.X |
| Operational Risk | Average of (X, X, X, X, X) | X.X | ×1 | X.X |
| **Total** | | | | **X.X** |

### Risk Level: [Low / Medium / High]

### Risk Details

#### Business Impact (Weighted: X)
[2-3 sentences grounding the scores in data]

#### Execution Risk (Weighted: X.X)
[2-3 sentences grounding the scores in data]

#### Operational Risk (Weighted: X.X)
[2-3 sentences grounding the scores in data]

### Data Gaps
- [Any subcriteria scored conservatively due to missing data]

### Risk Mitigations Already in Place
- [Mitigations identified from the data]
```
