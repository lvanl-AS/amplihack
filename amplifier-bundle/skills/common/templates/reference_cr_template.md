# Change Request Summary Template

Reference template for the Change Request Document workflow. Structured from the Alaska Airlines Change Request template.

## Section 1: Deployment Details

| Field | Description | Data Source |
|-------|-------------|-------------|
| Change Title | Short name for the change | ADO Context Expert: feature title |
| Description of Change | What is being changed and why | ADO Context Expert: feature desc + story summaries |
| Deployment Date/Time | Scheduled deployment window | User provides |
| Target Environment(s) | Which environments are affected | ADO Context Expert + Code Changes Expert, user confirms |
| Deployment Method | How the change will be deployed (pipeline, manual, etc.) | Code Changes Expert + deployment.yaml, user confirms |
| Change Type | Standard / Normal / Emergency | User selects |

## Section 2: Impacted Systems

| Field | Description | Data Source |
|-------|-------------|-------------|
| Primary Systems/Services | Systems directly modified by this change | Code Changes Expert: repos + PR diffs |
| Dependencies | Systems that depend on the changed systems | ADO Context Expert + Code Changes Expert |
| Upstream Systems | Systems that feed data/requests to changed systems | ADO Context Expert, user confirms |
| Downstream Systems | Systems that consume data/output from changed systems | ADO Context Expert, user confirms |
| Integration Points | APIs, queues, databases shared across boundaries | Code Changes Expert + ADO Context Expert |

## Section 3: Rollback Strategy

| Field | Description | Data Source |
|-------|-------------|-------------|
| Deployment Order | Ordered sequence of service/repo deployments | Draft from deployment.yaml + Code Changes Expert, user confirms |
| Rollback Order | Reverse of deployment order with methods and times | Draft from deployment.yaml + pipeline history, user confirms |
| Rollback Steps | Step-by-step procedure to reverse the change | Draft from deployment method, user confirms |
| Rollback Time Estimate | Expected time to complete rollback | Draft from pipeline history, user confirms |
| Rollback Triggers | Conditions that would trigger a rollback decision | Draft from ADO Context Expert failure indicators, user confirms |
| Success Criteria | How to verify the deployment succeeded | Draft from ADO Context Expert (AC-based), user confirms |
| Validation Steps | Post-deployment checks to confirm success | Draft from ADO Context Expert + Code Changes Expert, user confirms |
| Irreversible Changes | Changes that cannot be rolled back with mitigation | Code Changes Expert: migration/schema files, user confirms |

## Section 4: Alerting & Monitoring

| Field | Description | Data Source |
|-------|-------------|-------------|
| Dashboards to Monitor | Links to relevant monitoring dashboards | User provides |
| Key Metrics to Watch | Specific metrics that indicate health/problems | Draft from ADO Context Expert + Code Changes Expert, user confirms |
| Alerts to Watch | Existing alerts relevant to this change | User provides |
| Escalation Path | Who to contact if issues arise, in order | User provides |
| On-Call Team | Team responsible during deployment window | User provides |

## Section 5: Documentation Links

| Field | Description | Data Source |
|-------|-------------|-------------|
| Runbook Link | Link to operational runbook | User provides |
| Architecture Documentation | Relevant architecture docs | User provides |
| Change Request Link | Link to the CR in change management system | User provides |
| Related Work Items | ADO Feature and Story IDs | Auto-populated from workflow |
| Pull Request Links | Links to all PRs included in this change | Auto-populated from PR fetch |

---

## Field Classification

### Auto-fillable (high confidence)
- Change Title (from Feature title)
- Related Work Items (from ADO)
- Pull Request Links (from PR fetch)
- Primary Systems/Services (from PR repos)

### Can-draft, user-confirms (medium confidence)
- Description of Change
- Target Environment(s)
- Deployment Method
- Dependencies / Upstream / Downstream
- Integration Points
- Deployment Order
- Rollback Order
- Rollback Steps
- Rollback Time Estimate
- Rollback Triggers
- Success Criteria
- Validation Steps
- Irreversible Changes
- Key Metrics to Watch

### User-must-provide (no automated source)
- Deployment Date/Time
- Change Type
- Dashboards to Monitor
- Alerts to Watch
- Escalation Path
- On-Call Team
- Runbook Link
- Architecture Documentation
- Change Request Link
