---
name: CAB_risk-classification
description: |
  Classifies a change using the Alaska Airlines Risk Decision Tree v0.93.
  Deterministic: Ground Stop App → HIGH, Shared Service → HIGH,
  blast radius All Users → HIGH, mirror-tested → LOW. Outputs risk level
  and approval requirements.
version: 1.0.0
type: skill
auto_activate_keywords:
  - risk classification
  - risk decision tree
  - what risk level
  - change risk level
  - is this high risk
  - classify risk
canonical_source: amplifier-bundle/skills/CAB_risk-classification/SKILL.md
recipe: amplifier-bundle/recipes/CAB_risk-classification.yaml
---

# Risk Decision Tree Classification

Canonical spec: `amplifier-bundle/skills/CAB_risk-classification/SKILL.md`

Read the canonical source for the full algorithm, approval requirements, and output format.
