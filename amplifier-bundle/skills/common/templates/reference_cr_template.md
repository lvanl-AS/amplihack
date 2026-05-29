# Change Request Summary Template

Reference template for the Change Request Document workflow. Structured from real Alaska Airlines CR summary documents, the Cherwell form fields, Change Record Style Guide, Risk Decision Tree v0.93, and CR Manifest requirements.

## Document Header

```
Change Request Summary for CR#[XXXXXX]
Deployment Overview for IT Teams and Change Managers
```

## Section 1: Deployment Details

| Field | Description | Data Source |
|-------|-------------|-------------|
| Service / Component | System(s) being deployed | Code Changes Expert: repos/services |
| Change Summary | What is being changed — written for a **business partner audience**, not technical staff. For multi-service changes, organize by service with story references. | ADO Context Expert: feature desc + story summaries |
| Version | Deployment version, build tag, or package version. For multi-service changes, list per-service with deploy tag links and build links. | Code Changes Expert: target branches, tags, pipeline builds |
| Change Request Link | Link to the CR in Cherwell/ServiceNow | User provides |
| ADO Items | Linked User Stories and Bugs with IDs, titles, and ADO links | Auto-populated from story fetch |

### Drafting Guidance for Section 1

**Change Title** (for Cherwell form, not the document table): Titles MUST follow Style Guide format: `[Location (as needed)] + [action] + [object] + [modifier] + [scope]`

**Standard vocabulary for actions** (use these terms, not synonyms):

| Term | Meaning |
|------|---------|
| Install | Add new software or hardware |
| Deploy | Automated software delivery |
| Uninstall | Remove software or hardware |
| Upgrade | New version of something existing |
| Patch | Vendor code maintenance update |
| Release | Automated pipeline code delivery |
| Decommission | Removing something from the enterprise |
| Restart | Application services stopped and started |
| Reboot | Infrastructure components shut down and started |
| DR Exercise | Service move test between primary/secondary |

**Examples:**
- `ANCKK Upgrade network router to v10.2`
- `Deploy Flight Attendant API v2.7 on DNA servers`

### Cherwell Classify Fields

These fields map directly to the Cherwell form "New/Classify" screen (not shown in the document, but needed for Cherwell entry):

| Cherwell Field | Options | Data Source |
|----------------|---------|-------------|
| What Are You Changing? | Laptop/Desktop, Mobile Device, Application Code, Server, Database, Storage, Network, Firewall, Mainframe | Code Changes Expert: infer from file types and repo names |
| Where Is It Changing? | MyGate Data Center, Sealand Data Center, SEQ Data Center, Cloud, Corporate, Horizon GQ, Center Point, Flight Ops, GCC, MyGate Building, Street, BSM Data Center (VA), SAC Data Center (VA), SCD Data Center (VA) | Deployment configs, user confirms |
| How Is It Changing? | New, Patch, Update/Maintenance, Decommission | ADO Context Expert + Code Changes Expert |
| Primary Impacted System | System name (dropdown in Cherwell) | Code Changes Expert: primary repo/service |

## Section 2: Impacted Systems

| Field | Description | Data Source |
|-------|-------------|-------------|
| Primary Systems | Systems directly modified by this change | Code Changes Expert: repos + PR diffs |
| Downstream/Upstream Dependencies | Systems that feed data to or consume data from changed systems | ADO Context Expert + Code Changes Expert, user confirms |
| Guest Flows / Touchpoints | User-facing flows or features affected by this change | ADO Context Expert: AC + story descriptions |
| Risk Level | Low / Medium / High — from Risk Decision Tree classification | Risk Decision Tree output |

### Ground Stop / Day-of-Travel System Check

**AUTOMATIC HIGH RISK** — If any impacted system is or interacts with:
- **Account** (Ground Stop application)
- **BTS** (Ground Stop application)
- **ABD** (Ground Stop application)
- **CSA Mobile** (Ground Stop application / Day of Travel)

These systems directly affect safety, flight operations, revenue, and guest experience. Even small or routine changes to these systems are HIGH risk and cannot use the Standard Change path.

### Shared Service Check

Any **API consumed by multiple applications or teams** is a shared service under the Risk Decision Tree and classifies as HIGH risk. Flag any multi-consumer APIs detected in the PR data.

## Section 3: Rollback Strategy

| Field | Description | Data Source |
|-------|-------------|-------------|
| Rollback Method | How the change will be reversed (e.g., pipeline rollback stage, feature flag toggle, deploy previous build) | Code Changes Expert + deployment.yaml, user confirms |
| Rollback Owner | Person or team responsible for executing rollback | User provides |
| Rollback Trigger | Specific conditions that would trigger a rollback decision | Draft from ADO Context Expert failure indicators + Code Changes Expert risk signals, user confirms |
| Estimated Rollback Time | Expected time to complete rollback (also provides **Back-Out Duration** in minutes for Cherwell) | Draft from pipeline history, user confirms |
| Rollback Steps | Step-by-step procedure to reverse the change, with links to pipeline runs or builds to redeploy | Draft from deployment method + pipeline data, user confirms |

### Multi-Service Rollback

For changes spanning multiple services, rollback steps should list per-service actions in reverse deployment order with specific pipeline/build links (see CR126633 and CR127579 examples).

### Fail-Forward Documentation (When Rollback Is Not Possible)

Some changes are fail-forward by nature (e.g., database migrations, published API contract changes). When rollback is not possible, the CR MUST document:

| Field | Description |
|-------|-------------|
| Why rollback is not possible | Specific technical reason (e.g., "destructive schema migration removes column X") |
| How impact will be detected | Metrics, alerts, or checks that surface problems |
| How the system will be stabilized or fixed forward | Concrete recovery steps |
| Stop/go decision points | Pre-deployment gates where the team decides whether to proceed |

## Section 4: Alerting and Monitoring

| Field | Description | Data Source |
|-------|-------------|-------------|
| Dashboards | Links to relevant monitoring dashboards (Sumo Logic, Firebase, Tealium, etc.) | User provides |
| Alerts | Links to alerting wiki pages or specific alert rules | User provides |
| On-Call Channel | Teams channel or support channel for incident response | User provides |
| Success Criteria | How to verify the deployment succeeded — concrete, observable outcomes | Draft from ADO Context Expert (AC-based), user confirms |

## Section 5: Documentation Links

| Field | Description | Data Source |
|-------|-------------|-------------|
| RBX | Link to RBX documentation (if applicable) | User provides |
| MBX | Link to MBX documentation (if applicable) | User provides |
| Runbook | **REQUIRED** — Link(s) to operational runbook, wiki pages, playbooks. Multiple links allowed. Required even for bug fixes impacting production. | User provides — mandatory per CR Manifest |
| Testing Documentation | Link to E2E test suite build or test plan (if applicable) | User provides or auto from pipeline data |

## Section 6: Proof of Testing

Evidence that the change works as expected. This section contains:
- **Per-change evidence**: Pipeline run screenshots, UI screenshots, Postman responses, screen recordings, video links
- **Brief narrative**: What the evidence shows and why it demonstrates success

For multi-service changes, organize evidence per service or per story.

| Evidence Type | Description | Data Source |
|---------------|-------------|-------------|
| Pipeline Runs | Screenshots of successful pipeline runs (Build, Test, QA, Prod stages) | User provides screenshots |
| UI Verification | Screenshots proving the UI change works correctly | User provides screenshots |
| API Verification | Postman/curl screenshots showing correct API responses | User provides screenshots |
| Screen Recordings | Video files or links demonstrating the feature end-to-end | User provides |

**Note**: The workflow should prompt the user to provide evidence for each story/change item and describe what the evidence demonstrates.

## Document Footer

```
Note: Replace bracketed placeholders before submitting for change management approval.
```

---

## Appendix A: Risk Decision Tree Classification (v0.93)

The Risk Decision Tree is a deterministic algorithm that classifies changes as Low/Medium/High. This classification drives the Cherwell risk level and approval requirements.

```
1. ALL Changes must have a Change Request
   -> (Or within 24 hours for Emergency Changes)

2. Does this Change impact or interact with a Ground Stop App
   or Customer Facing App? (Account, BTS, ABD, CSA Mobile)
   -> YES -> HIGH

3. Does the Change affect any Shared Service?
   (Network, middleware, API consumed by multiple apps/teams)
   -> YES -> HIGH

4. If the Change Fails, what is the blast radius?
   -> All Users -> HIGH
   -> Some Users -> MEDIUM
   -> ... OR continue to step 5

5. Change is fully tested in a mirror of the live environment?
   -> Less than 100% Tested -> MEDIUM
   -> 100% Successfully Tested -> LOW
   -> ... OR continue to step 6

6. All Other Changes:
   -> If Standard Change -> LOW
   -> Otherwise -> MEDIUM
```

**Implications of risk level:**

| Risk Level | Approval Required | Additional During Soft Freeze | Additional During Hard Freeze |
|------------|------------------|-------------------------------|-------------------------------|
| **Low** | Peer Review only | Director approval | Director + 2x (MD or VP ITS) + CAB |
| **Medium** | Peer Review + CAB (min 2 members) | Director approval + CAB | Director + 2x (MD or VP ITS) + CAB |
| **High** | Peer Review + CAB (min 2 members) + Director | Director approval + CAB | Director + 2x (MD or VP ITS) + CAB |

**Key deadlines:**
- **Friday 6:00 PM PST** — CR must be submitted with required approvals for inclusion in Monday VP review and Thursday CAB
- **Thursday 2:00 PM PST** — CAB meeting (weekly)

**Change freeze rules:**
- **Soft Freeze**: Every Friday 12:00 AM - Sunday 11:59 PM PST. Director approval required. Standard changes can still proceed.
- **Hard Freeze**: Scheduled by upper management. Director + 2 MD/VP + CAB required. Standard changes via pipeline CANNOT proceed during hard freeze — must clone to Normal CR.

## Appendix B: CR Manifest (Required Attachments)

Per the CR Manifest requirements, the following must be attached to the CR in Cherwell/ServiceNow:

| Attachment | Required? | Notes |
|------------|-----------|-------|
| **Runbook** | Yes | ITS Operations Runbook Template. Consolidates System Summary + Triage & Troubleshooting |
| **Diagrams** | Yes | Logical, physical, architecture, dataflow, workflow. Can link to SharePoint |
| **Deployment/Implementation Plan** | Yes | Can be in CR form if short enough |
| **Rollback/Backout Plan** | Yes | Can be in CR form if short enough |
| **Test Plan and Validated Results** | Yes | Pre-production testing OR post-implementation validation |
| **Communication Plan** | Yes | Filled in Cherwell form directly (not in summary document) |
| **Additional Approvals** | If applicable | Director, MD, VP, Business |

## Appendix C: Communication Plan (Cherwell Form)

Communication Plan is filled directly in the Cherwell form "Communications Plan" tab, not as a section in the CR summary document. Required for ALL change types.

| Field | Description |
|-------|-------------|
| Pre-Change Communication | Who needs to know before the change, and what |
| During-Change Communication | How status updates will be shared during implementation |
| Post-Change Communication | Who to notify of completion, and how to verify |
| Failure Communication | Who to notify if rollback is triggered |

## Appendix D: Cherwell Risk Assessment Questionnaire

These 12 questions are answered in the Cherwell form and drive the system's risk calculation (Low/Medium/High). The CR workflow should help users answer these correctly based on available data.

| # | Question | Type | Can Auto-Fill? |
|---|----------|------|----------------|
| 1 | How Complex Is This Change? | Dropdown | Yes — from Code Changes Expert (repo count, team count, integration depth) |
| 2 | Is This Change Using Automation Tools To Reduce Manual Steps? | Yes/No | Yes — from pipeline data (pipeline-deployed = Yes) |
| 3 | How Difficult Is It To Verify The Change Completed Successfully? | Dropdown | Partially — from ADO Context Expert (AC completeness, validation clarity) |
| 4 | Does This Change Have a Back Out Plan? | Yes/No | Yes — from Section 3 existence |
| 5 | How Long to Back Out of This Change? | Dropdown | Yes — from pipeline history rollback times |
| 6 | Will This Change Require an Outage? | Yes/No | Partially — from deployment configs |
| 7 | If the Change Fails, Is the System Recoverable Within the Outage Window? | Yes/No | Partially — from rollback time estimate vs outage window |
| 8 | Does This Change Fall Within the 10:30pm - 4:00am Maintenance Window? (Or During an Approved Exception Period) | Yes/No | Yes — if deployment time is provided |
| 9 | How Many Times Has This Change Been Successful? | Dropdown | Yes — from pipeline run history (successful runs against main) |
| 10 | Has This Change Been Tested? | Yes/No | Partially — from test files in diffs, proof of testing |
| 11 | Have You Documented and Archived Proof of Testing? | Yes/No | No — user must confirm |
| 12 | List any remaining concerns regarding testing this change | Text | Draft from Testing gaps in expert outputs |

**Note**: Selecting "Complex" or "Very Complex" for question 1 raises the calculated risk level. These questions determine the Cherwell risk level, which is separate from (but related to) the CRAM score.

---

## Field Classification

### Auto-fillable (high confidence)
- Service / Component (from PR repos)
- ADO Items (from story fetch)
- Primary Systems (from PR repos)
- Risk Level (from Risk Decision Tree)
- Related Work Items (from ADO)
- Pull Request Links (from PR fetch)
- What Are You Changing? (from repo/file analysis — Cherwell form)
- Cherwell Q2: Automation Tools (from pipeline data)
- Cherwell Q4: Back Out Plan (from Section 3)

### Can-draft, user-confirms (medium confidence)
- Change Summary
- Version
- Downstream/Upstream Dependencies
- Guest Flows / Touchpoints
- Rollback Method
- Rollback Trigger
- Estimated Rollback Time
- Rollback Steps
- Success Criteria
- Cherwell Q1, Q3, Q5, Q6, Q7, Q8, Q9, Q10, Q12

### User-must-provide (no automated source)
- Change Request Link
- Rollback Owner
- Dashboards
- Alerts
- On-Call Channel
- RBX / MBX
- Runbook
- Proof of Testing (screenshots, videos, evidence)
- Communication Plan (Cherwell form fields)
- Cherwell Q11: Documented Proof of Testing
