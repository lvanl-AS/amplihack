# CRAM — Change Risk Assessment Matrix Template

Reference template for the CRAM scoring workflow. Sourced from the Alaska Airlines Change Risk Assessment Matrix. Updated with objective thresholds from the Risk Decision Tree v0.93, IT Incident Severity Levels Standard, Standard Change requirements, and AAG IT Change Management Q&A (March 2026).

**Important distinction**: CRAM is an additional risk assessment tool. The **Cherwell Risk Assessment Questionnaire** (12 questions on the Classify screen) determines the system-calculated risk level (Low/Medium/High). CRAM provides a deeper, weighted analysis for CAB review. Both may be used for the same change.

**Valid change types**: Standard, Normal, Emergency. Informational is no longer a valid type per AAG Q&A (March 2026).

## Scoring Scale

Each subcriterion is scored 1-3:
- **1** = Low Risk — Safe, routine changes with low complexity and predictable outcomes
- **2** = Medium Risk — Moderately complex changes that require oversight, scheduling review, and leadership review
- **3** = High Risk — Significant risk of major incidents, requires senior leadership review, stringent controls, and strategic scheduling

## Category 1: Business Impact (Weight = 3)

**Scoring: Highest subcriterion score x 3**

The biggest driver — what could this break?

### 1a. System Criticality

| Score | Criteria |
|---|---|
| 1 | Tier 3 or Tier 4 systems; impacts a single department |
| 2 | Tier 2 systems; impacts a single site or multiple departments |
| 3 | Tier 0 or Tier 1 systems OR impacts multiple sites / critical operations |

**Tier Classification** — official tiers are documented in ORBIS:

| Tier | Definition | Examples |
|---|---|---|
| 0 | Infrastructure | Core platform, networking, shared infra |
| 1 | Critical — Ground Stop, Operations, Check-in | Core auth/session tied to check-in |
| 2 | Critical — Revenue, Employee Impact | Enrollment, loyalty, payment flows; profile/settings UI with revenue exposure |
| 3 | Not critical | Internal tooling; profile/settings UI without revenue exposure |

**AUTOMATIC SCORE 3 — Ground Stop / Day-of-Travel Applications:**
The following systems are ALWAYS Tier 1 (score 3), regardless of change size:
- **Account** (Ground Stop application)
- **BTS** (Ground Stop application)
- **ABD** (Ground Stop application)
- **CSA Mobile** (Ground Stop application / Day of Travel)

Per the Risk Decision Tree FAQ: "Any change that impacts a Ground Stop application or Day of Travel service is automatically classified as high risk, even if the change is small or routine, because these systems directly affect safety, flight operations, revenue, and guest experience."

**Even Standard Changes lose their Standard status** when touching Ground Stop/Day-of-Travel systems — they must be submitted as Normal CRs.

**Shared Service Rule:**
Any **API consumed by multiple applications or teams** is a shared service. Shared services score 2 minimum (Tier 2) and often 3 if they are network/middleware/platform-level. This includes multi-consumer APIs even if they seem low-risk individually.

**Scoring guidance:**
- Enrollment, loyalty, payment flows -> Tier 2 (score 2)
- Profile/settings UI -> Tier 2 or 3 depending on revenue exposure
- Core auth/session tied to check-in -> Tier 1 (score 3)
- Internal tooling -> Tier 3 (score 1)
- Multi-consumer API -> Tier 2 minimum (score 2+)
- If tier is unknown, ask the user or check ORBIS. Use `[PLACEHOLDER: ORBIS tier for <service>]` if user says to proceed without it.

**SLA uptime targets:** 99.9% for Tier 1-2, 99.5% for Tier 3.

**IT Incident Severity connection:**
- Tier 0-1 systems with critical urgency = Severity 1 incident (1 hour mitigation SLA, 20 min team initiation)
- Tier 2 systems with high urgency = Severity 2 incident (4 hour mitigation SLA)
- This context informs the potential blast radius of a failed change.

**ServiceNow CI link and ORBIS link** — these are never in code or wiki. If needed, use `[PLACEHOLDER: ServiceNow CI link]` and `[PLACEHOLDER: ORBIS link]`.

**Reviewed By** — who should sign the runbook. If unknown, use `[PLACEHOLDER: Reviewer name]`.

### 1b. Customer Impact

| Score | Criteria |
|---|---|
| 1 | No potential customer impact; internal-only change |
| 2 | Limited potential customer impact; minor service degradation or short outage |
| 3 | Significant potential customer impact; major outage or service disruption |

**Risk Decision Tree connection:**
- Blast radius "All Users" -> score 3
- Blast radius "Some Users" -> score 2
- Guest-facing services with operational dependency -> score 2-3 (per AAG Q&A: "heightened scrutiny on day-of-travel and operationally critical systems")

### 1c. Regulatory Compliance

| Score | Criteria |
|---|---|
| 1 | No compliance implications |
| 2 | Minor compliance considerations; documented and approved |
| 3 | High compliance risk; regulatory breach possible if change fails |

**PCI requirement**: For PCI-related changes, ALL security vulnerabilities must be resolved (not just critical/high) per Standard Change requirements. PCI changes touching Dependabot/Aqua findings that aren't fully resolved = score 2-3.

**Compliance frameworks in scope**: PCI, SOX, ISO/IEC 27001:2013 (per IT Incident Severity Standard).

**Data sources:** ADO Context Expert (user journeys, business criticality, compliance mentions), Code Changes Expert (repos/systems involved, tier classification)

## Category 2: Execution Risk (Weight = 2)

**Scoring: Average of subcriterion scores x 2**

The second driver — how hard is it to do safely?

### 2a. Change Complexity

| Score | Criteria |
|---|---|
| 1 | Simple change; 1-2 teams, single system, few steps, minimal risk, limited scope, predictable outcome |
| 2 | Moderate complexity; 3-4 teams, one complex system or minor integration |
| 3 | High complexity; 5+ teams, multiple systems, deep integration, unpredictable outcomes |

**Cherwell connection:** Selecting "Complex" or "Very Complex" for question 1 on the Cherwell Risk Assessment Questionnaire raises the calculated risk level. Ensure CRAM complexity score aligns with the Cherwell answer.

### 2b. Testing Coverage

| Score | Criteria |
|---|---|
| 1 | Fully tested, evidence available, low risk |
| 2 | Partially tested, failed test cases, risk acknowledged, acceptable with oversight |
| 3 | Untested or failed, no mitigation; high risk if deployed |

**Risk Decision Tree connection:**
- "100% Successfully Tested in a mirror of the live environment" -> supports score 1 and LOW risk classification
- "Less than 100% Tested" -> supports score 2+ and MEDIUM risk classification

**Cherwell connection:** Maps to questions 10 ("Has This Change Been Tested?"), 11 ("Have You Documented and Archived Proof of Testing?"), and 12 (testing concerns).

### 2c. Rollback Feasibility

| Score | Criteria |
|---|---|
| 1 | Easy rollback; < 30 minutes |
| 2 | Moderate rollback; 30 min to 2 hours |
| 3 | Difficult rollback; > 2 hours or requires major recovery effort |

**Fail-forward changes:** When rollback is not possible (database migrations, published API changes), the score depends on the quality of fail-forward documentation: detection plan, stabilization plan, and stop/go decision points. Well-documented fail-forward with fast fix-forward capability = score 2. Undocumented fail-forward = score 3.

**Cherwell connection:** Maps to questions 4 ("Does This Change Have a Back Out Plan?") and 5 ("How Long to Back Out of This Change?"). The back-out duration must be provided in minutes.

**Data sources:** Code Changes Expert (repo count, team count, test files, PR status), pipeline data (rollback time estimates), ADO Context Expert (story states, AC completeness)

## Category 3: Operational Risk (Weight = 1)

**Scoring: Average of subcriterion scores x 1**

Still important, but lighter weight — are we truly ready to run it now?

### 3a. Change Window

| Score | Criteria |
|---|---|
| 1 | No outage expected or within the **Approved Maintenance Window (10:30 PM - 4:00 AM)** |
| 2 | Outage occurring during Off-Hours (outside maintenance window but not peak) or during the **weekend Soft Freeze (Friday 12:00 AM - Sunday 11:59 PM PST)**. Soft freeze requires Director approval. |
| 3 | Outage during **Peak / Business Hours / Pre-Flight / Global Ops (05:00-17:00)** or during a **Hard Freeze**. Hard freeze requires Director + 2 MD/VP + CAB. Standard changes via pipeline prohibited during hard freeze. |

**Cherwell connection:** Maps to question 8 ("Does This Change Fall Within the 10:30pm - 4:00am Maintenance Window?").

### 3b. Operational Readiness

| Score | Criteria |
|---|---|
| 1 | All documentation, observability, approvals, and resources confirmed; support teams ready |
| 2 | Some gaps in documentation, observability, or readiness; mitigations in place |
| 3 | Significant gaps; unclear ownership or missing approvals |

**CR Manifest check:** A fully ready change has: Runbook, Diagrams, Deployment Plan, Rollback Plan, Test Plan with results, Communication Plan, and all required approvals.

**Cherwell connection:** Maps to the Documentation/Monitoring checkboxes on the Task Plan screen:
- "Service Desk, Prod Ops and System Documentation updated?" (Yes/N/A)
- "Monitoring updates have been made or tasks to update monitoring systems?" (Yes/N/A)

### 3c. Vendor Dependency

| Score | Criteria |
|---|---|
| 1 | No vendor involvement; fully internal |
| 2 | Vendor involvement for minor tasks or advisory |
| 3 | Vendor dependency for critical tasks; delays or coordination risks |

### 3d. Secure Coding

| Score | Criteria |
|---|---|
| 1 | **Alaska Standard Quality Gate (70% coverage)** or higher is used; No Critical or High vulnerabilities are present |
| 2 | Security Plus or Security Quality Gate is used; Unresolved security hotspots are present |
| 3 | No Quality Gate is configured; Critical or High vulnerabilities exist, and security hotspots remain unresolved |

**SonarQube requirement:** Alaska Standard quality gate requires **70% code coverage** minimum. This is a hard requirement for Standard Change eligibility.

**Standard Change security requirements:**
- SonarQube: Alaska Standard (70% coverage) or higher quality gate
- Aqua (if containerized): All critical/high vulnerabilities with vendor fix resolved
- Dependabot: All critical/high vulnerabilities resolved
- **PCI-related changes: ALL vulnerabilities resolved** (not just critical/high) for both Dependabot and Aqua

### 3e. Resilience & Recovery (RR)

| Score | Criteria |
|---|---|
| 1 | RR plan fully automated, tested successfully, and evidence demonstrating less than 1 hour total elapsed time for recovery prior to outside validation |
| 2 | RR plan tested and lacking full automation or with issues remediated without re-testing; Recovery process is < 2 hours total elapsed time for recovery prior to outside validation |
| 3 | No RR testing evidence; recovery plan unverified and/or recovery process is > 2 hours total elapsed time for recovery prior to outside validation |

**Data sources:** CR document (deployment window, operational readiness), Code Changes Expert (vendor dependencies, security scan results), pipeline data (RR testing evidence, recovery time)

## Overall Risk Score

**Formula:**
- Business Impact weighted score = **highest** of (1a, 1b, 1c) x 3
- Execution Risk weighted score = **average** of (2a, 2b, 2c) x 2
- Operational Risk weighted score = **average** of (3a, 3b, 3c, 3d, 3e) x 1
- **Total** = Business Impact + Execution Risk + Operational Risk

| Total Weighted Score | Risk Level | Implications |
|---|---|---|
| 6-10 | **Low Risk** | Standard deployment process. Peer review only. |
| 11-15 | **Medium Risk** | Requires oversight, scheduling review, leadership review. Peer + CAB (min 2 members). |
| 16-18 | **High Risk** | Requires senior leadership review, stringent controls, strategic scheduling. Peer + CAB + Director. |

### CRAM Risk Level -> Approval Requirements

| CRAM Level | Normal Period | Soft Freeze (Fri-Sun) | Hard Freeze |
|---|---|---|---|
| Low (6-10) | Peer Review | + Director approval | + Director + 2 MD/VP + CAB |
| Medium (11-15) | Peer + CAB | + Director approval | + Director + 2 MD/VP + CAB |
| High (16-18) | Peer + CAB + Director | + Director + CAB | + Director + 2 MD/VP + CAB |

**Key deadline:** CRs must be submitted by **Friday 6:00 PM PST** with required approvals for inclusion in Monday VP review and Thursday CAB meeting (2:00 PM PST).

**Note:** The CRAM score provides a detailed risk picture but the **Cherwell Risk Assessment Questionnaire** (12 questions) determines the system-calculated risk level. Both assessments should align — if CRAM says High but Cherwell says Low, investigate the discrepancy.

## Scoring Calibration (from historical CRAMs)

Based on 13 real CRAM assessments for this team, these patterns guide scoring:

### Subcriteria that almost always score 1

| Subcriterion | Score=1 rate | Guidance |
|---|---|---|
| **Change Window** | 100% (always 1) | Team deploys within 10:30 PM - 4:00 AM maintenance window. Score 1 unless evidence of off-hours/peak deployment or freeze period. |
| **Vendor Dependency** | 100% (always 1) | All changes are internal. Score 1 unless third-party service integration is in the diff. |
| **Regulatory Compliance** | 77% (never 3) | Compliance is rarely a factor. Score 1 unless PCI, PII, HIPAA, SOX, or ISO 27001 signals are present. |
| **Operational Readiness** | 85% (never 3) | Docs/approvals are generally ready. Score 1 unless gaps are explicitly identified in CR Manifest review. |
| **Rollback Feasibility** | 77% (rarely above 1) | Most changes are easily reversible. Score 1 for config/feature flag changes, 2+ for database migrations or multi-system state changes. Note: feature flag changes ARE changes requiring CRs. |

### High-variance subcriteria (focus evidence-gathering here)

| Subcriterion | Distribution | Guidance |
|---|---|---|
| **System Criticality** | Evenly split 1-3 | Drives Business Impact. Use ORBIS tier. Ground Stop apps (Account, BTS, ABD, CSA Mobile) = automatic 3. Multi-consumer APIs = 2+. Ask the user if tier is unknown. |
| **Customer Impact** | Evenly split 1-3 | Guest-facing changes score 2-3. Internal tooling scores 1. Day-of-travel services get heightened scrutiny. Blast radius All Users = 3, Some Users = 2. |
| **Secure Coding** | Evenly split 1-3 | Quality gate status is NOT in code — always flag as a data gap or ask the user for SonarQube status. Alaska Standard = 70% coverage. PCI changes need ALL vulns resolved. |
| **Testing Coverage** | 50/50 split between 1 and 2 (never 3) | Team never deploys fully untested. Score 1 if test files are in the diff, 2 if partial or infrastructure-only changes without test suites. "100% tested in mirror" from Risk Decision Tree = 1. |
| **Resilience & Recovery** | Mostly 1-2 | Score 1 if automated rollback evidence exists, 2 if manual but documented, 3 only if no evidence at all. |

### Overall patterns

- **No High Risk (16-18) has ever been scored** for this team. Range is 6-15, mean 10.8. Do not score High Risk without strong, specific evidence.
- **Business Impact drives the total** because of the x3 weight on the highest score. A single 3 in Business Impact -> weighted 9 -> halfway to Medium.
- **Secure Coding is the most unpredictable** subcriterion. When quality gate data is missing, flag it as a data gap rather than guessing.

### Low-confidence scoring guidance

Some subcriteria are inherently subjective and the scorer may not have enough
signal from code or ADO data to score confidently. When the score could
reasonably be one level higher or lower, add the subcriterion key to the
`low_confidence` array in the output. The review step will open a dialogue with
the user for these.

**Most likely to be low-confidence:**
- **Customer Impact** — "limited" vs "significant" impact depends on user journey context that may not be in the PR or story. If you can't clearly determine whether end users would notice a failure, flag it.
- **Change Complexity** — team count and integration depth are often not explicit in the data. If you're inferring team count from repo ownership or guessing at integration depth, flag it.
- **Testing Coverage** — absence of test files doesn't always mean untested (testing may happen outside the PR workflow). If the only signal is "no test files in diff", flag it.
- **Rollback Feasibility** — rollback time is an estimate. If you're guessing from change type rather than pipeline data, flag it.
- **Operational Readiness** — whether documentation/approvals/monitoring are truly confirmed is often not visible in code. If you're defaulting to the baseline rather than finding evidence, flag it.

**Rarely low-confidence** (objective signals available):
- System Criticality (ORBIS tier), Change Window (time-based), Vendor Dependency (binary), Regulatory Compliance (binary), Secure Coding (data gap rather than ambiguity), Resilience & Recovery (data gap rather than ambiguity)

## Output Format

The scorer MUST output a JSON block containing scores and justifications. This
JSON feeds into the Excel generator to produce the official CRAM spreadsheet.

Justifications are for the human review step — they do NOT appear in the final
CRAM document (which is just the template with scores filled in).

```
===CRAM_SCORES===
{
  "scores": {
    "system_criticality": <1-3>,
    "customer_impact": <1-3>,
    "regulatory_compliance": <1-3>,
    "change_complexity": <1-3>,
    "testing_coverage": <1-3>,
    "rollback_feasibility": <1-3>,
    "change_window": <1-3>,
    "operational_readiness": <1-3>,
    "vendor_dependency": <1-3>,
    "secure_coding": <1-3>,
    "resilience_recovery": <1-3>
  },
  "justifications": {
    "system_criticality": "<1-2 sentences citing specific data>",
    "customer_impact": "<1-2 sentences citing specific data>",
    "regulatory_compliance": "<1-2 sentences citing specific data>",
    "change_complexity": "<1-2 sentences citing specific data>",
    "testing_coverage": "<1-2 sentences citing specific data>",
    "rollback_feasibility": "<1-2 sentences citing specific data>",
    "change_window": "<1-2 sentences citing specific data>",
    "operational_readiness": "<1-2 sentences citing specific data>",
    "vendor_dependency": "<1-2 sentences citing specific data>",
    "secure_coding": "<1-2 sentences citing specific data>",
    "resilience_recovery": "<1-2 sentences citing specific data>"
  },
  "low_confidence": ["<subcriteria where evidence was ambiguous and score could reasonably go either way>"],
  "data_gaps": ["<subcriteria scored conservatively due to missing data>"],
  "mitigations": ["<mitigations identified from the data>"],
  "risk_decision_tree": {
    "ground_stop_app": <true/false>,
    "shared_service": <true/false>,
    "blast_radius": "<all_users/some_users/limited/unknown>",
    "mirror_tested": "<yes/no/unknown>",
    "tree_classification": "<LOW/MEDIUM/HIGH>",
    "tree_reasoning": "<1 sentence explaining which tree branch was hit>"
  }
}
===END_CRAM_SCORES===
```
