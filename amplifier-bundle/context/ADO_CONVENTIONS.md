# ADO Conventions

## Before Any ADO Work

Read the workspace configuration first. Use `--workspace` flag on Python wrappers to target the correct board. Never guess the sprint name — use MCP `work_list_team_iterations` to fetch available iterations.

Read the ADO work item before starting any implementation. Never create a work item without checking for an existing duplicate first.

## Work Item Standards

**Stories**:
- Must have Acceptance Criteria and Story Points before moving to Active
- AC format: Gherkin (Given/When/Then) for new stories; match existing format for edits
- Follow `reference_alaska_story_template.md` as source of truth
- Title: verb phrase from user's perspective ("User can view X", not "Add X feature")

**Features**:
- Must reference at least one measurable outcome metric before moving out of Proposed
- Follow `reference_alaska_feature_template.md` as source of truth
- WHY section must use Without/With contrast framing (team convention)
- Features that are purely technical still need a "Why" connecting to a business or reliability goal

**Tasks**:
- Always children of a parent Story — never free-floating tasks
- Title: imperative ("Add rate limiting to /auth endpoint"), not noun phrase
- No sizing — no story points, T-shirts, or hours. Sizing is the team's job in planning
- Describe the WHAT, never the HOW — no code references, no file paths, no specific technical solutions

**Bugs**:
- Can be standalone or children of a Story
- Required before Active: Priority (1-4), Severity (1-4), reproduction steps
- State flow: New -> Active -> Resolved -> Closed; never skip Resolved
- Title: describe observed behavior, not cause ("Login fails when session expires" not "Fix null session check")

## PR to Work Item Linking

Include `AB#<work-item-id>` in the commit message or PR description. This auto-links the PR in ADO.

## Definition of Done

A work item is not Closed until:
1. PR is merged and pipeline passed
2. Change deployed to target environment
3. `AB#<id>` in merge commit or PR description

## Tool Strategy

**Python wrappers** (for recipe `bash` steps — deterministic data fetching):
- `get_work_item.py`, `create_work_item.py`, `update_work_item.py`, `delete_work_item.py`
- `query_wiql.py`, `link_parent.py`, `list_types.py`, `list_work_items.py`
- `format_html.py`, `auth_check.py`, `create_pr.py`, `list_repos.py`
- `get_comments.py`, `get_revisions.py`
- All support `--workspace` flag for multi-board targeting
- Located at `.claude/scenarios/az-devops-tools/`

**ADO MCP server** (for recipe `agent` steps — conversational enrichment):
- Wiki search, iterations, capacity, team listing
- Agents call MCP tools directly; MCP does NOT work in `bash` steps
