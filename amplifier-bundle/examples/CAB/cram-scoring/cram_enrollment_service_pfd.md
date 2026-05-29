# CRAM Risk Assessment — Enrollment Service Front Door Migration

**Story:** #1443778 — Enrollment Service | Move to Platform Premium Front Door
**Feature:** #1518474 — Account Personalization | Move Account and Enrollment Services to modern front door
**Date:** 2026-05-29
**Scored by:** CRAM Scoring Skill (amplihack)

## Scores

| Category | Subcriterion | Score | Justification |
|---|---|---|---|
| **Business Impact** | System Criticality | 2/3 | Enrollment Service is Tier 2 — guest-facing but not revenue-critical. Routing change only; no application logic modified. |
| | Customer Impact | 2/3 | Guests hitting Enrollment Service through Front Door URLs. Misroute could cause enrollment failures, but Classic AFD remains operational as fallback. |
| | Regulatory Compliance | 1/3 | No regulatory or compliance requirements affected. Infrastructure routing change with no data handling modifications. |
| **Execution Risk** | Change Complexity | 1/3 | 2 repos, 2 PRs. PlatformFrontDoor: additive Terraform resources (origin groups, backends, env vars). enrollmentservice-dotnetcore: 4-line APIM config value swap. No cross-service dependencies. |
| | Testing Coverage | 2/3 | Infrastructure change — no unit tests applicable. Validation relies on health probes, HTTP 200 checks, and traffic distribution verification post-deploy. No pre-deploy integration test suite for Front Door routing. |
| | Rollback Feasibility | 1/3 | Fully reversible. Revert PR #297 (4-line value swap, 1-7 min) + revert PR #128 + terraform apply (2-4 min). Total rollback < 15 min. Classic AFD remains operational throughout. |
| **Operational Risk** | Change Window | 1/3 | Wednesday June 4, 5:00 AM PT — off-hours deployment outside business hours. |
| | Operational Readiness | 2/3 | CR document complete. Existing Azure Front Door and APIM dashboards available. No new monitoring configuration added. On-call identified (Mike Sheehan). |
| | Vendor Dependency | 1/3 | Azure-native services only. No third-party vendor changes. Microsoft Azure Front Door Premium is the target — standard Azure service. |
| | Secure Coding | 1/3 | No application code changes. Terraform resource provisioning and APIM config value swap only. No security hotspots. |
| | Resilience & Recovery | 1/3 | Classic AFD remains fully operational during migration as instant fallback. Rollback is a config revert, not a rebuild. No data migration or state changes. |

## Weighted Scores

| Category | Method | Raw | Weight | Weighted Score |
|---|---|---|---|---|
| Business Impact | Highest of (2, 2, 1) | 2 | x3 | **6** |
| Execution Risk | Average of (1, 2, 1) | 1.33 | x2 | **2.7** |
| Operational Risk | Average of (1, 2, 1, 1, 1) | 1.2 | x1 | **1.2** |
| **Total** | | | | **9.9** |

## Risk Level: Low Risk

Total weighted score: 9.9 (range 6-10 = Low Risk)

Standard approval process. No additional oversight required.

## Risk Details

### Business Impact (Weighted: 6)
The Enrollment Service is guest-facing but the change is purely at the infrastructure routing layer — no application code is modified. Classic Azure Front Door remains fully operational during the migration window, providing an immediate fallback path. The highest subcriterion (System Criticality and Customer Impact, both 2/3) reflects the production-facing nature of the service, while Regulatory Compliance scores low because no data handling or compliance-relevant logic is touched.

### Execution Risk (Weighted: 2.7)
This is a straightforward infrastructure change. Two repositories, two PRs, both already merged and reviewed. The PlatformFrontDoor PR adds Terraform resources (origin groups, endpoint backends, environment-specific variables) — all additive. The enrollmentservice-dotnetcore PR is a 4-line APIM config value swap. Testing Coverage scores highest in this category because infrastructure routing changes lack pre-deploy integration tests — validation is post-deploy (health probes, HTTP checks, traffic distribution). Rollback is fast and well-documented.

### Operational Risk (Weighted: 1.2)
Off-hours deployment (5 AM PT Wednesday) minimizes risk. Existing monitoring covers both Front Door and APIM dashboards. No vendor dependencies beyond standard Azure services. No application code changes means no secure coding concerns. The Classic AFD fallback provides resilience without any manual intervention needed.

## Data Gaps
- No pre-deploy integration test suite for Front Door routing — validation is post-deploy only
- No new monitoring configuration added — relies on existing Azure telemetry

## Risk Mitigations Already in Place
- **Classic AFD remains operational** — instant fallback path, no cutover until verified
- **Off-hours deployment** — Wednesday 5:00 AM PT, minimal traffic window
- **Fast rollback** — < 15 min total (4-line config revert + Terraform revert)
- **Additive changes only** — no destructive operations, no resource deletion in this deployment
- **All PRs merged and reviewed** — no draft or incomplete work
- **On-call identified** — Mike Sheehan
- **CR document completed** — full change request documentation
- **Legacy resource deletion is separate** — NOT part of this deployment

## Repositories and PRs

| Repository | PR | Title | Status |
|---|---|---|---|
| enrollmentservice-dotnetcore | #297 | AB#1443778 Migrate Enrollment Service Endpoint to Premium Front Door | Merged |
| PlatformFrontDoor | #128 | AB#1443778 Create Routes for Enrollment & Account Service on Premium Front Door | Merged |
