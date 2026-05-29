---
name: CAB_cram-scoring
description: |
  Generates a CRAM risk assessment using the Alaska Airlines CRAM template.
  3 weighted categories, 11 subcriteria, 1-3 scale, total 6-18.
  Reuses expert agents from CR workflow. Skips data fetch when context is pre-provided.
version: 1.0.0
type: skill
auto_activate_keywords:
  - CRAM
  - risk assessment
  - risk matrix
  - change risk
  - CRAM scoring
  - risk score
canonical_source: amplifier-bundle/skills/CAB_cram-scoring/SKILL.md
recipe: amplifier-bundle/recipes/CAB_cram-scoring.yaml
---

# CRAM Scoring

Canonical spec: `amplifier-bundle/skills/CAB_cram-scoring/SKILL.md`
Recipe: `amplifier-bundle/recipes/CAB_cram-scoring.yaml`

Read the canonical source for the full workflow, agents, and key behaviors.
