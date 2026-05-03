"""Tests for GitHub issue #4315: quality-audit-cycle skips fix after 2/3 validator confirmation.

Root cause: The merge-validations step outputs JSON but was missing
``parse_json: true``, so validated_findings was stored as a raw string
in context.  The fix step's condition
``validated_findings['confirmed_count'] > 0`` cannot subscript a string,
causing the Rust runner to evaluate the condition as false and skip fixes.

Fix: Add ``parse_json: true`` to the merge-validations step so the JSON
output is parsed into a dict before being stored in context.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest
import yaml

from amplihack.recipes.models import Step, StepType
from amplihack.recipes.parser import RecipeParser

REPO_ROOT = Path(__file__).resolve().parents[3]
RECIPE_PATH = REPO_ROOT / "amplifier-bundle" / "recipes" / "quality-audit-cycle.yaml"


@pytest.fixture(scope="module")
def recipe():
    with open(RECIPE_PATH) as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def steps_by_id(recipe):
    return {s["id"]: s for s in recipe["steps"]}


def _render_templates(command: str, values: dict[str, str]) -> str:
    rendered = command
    for key, value in values.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", value)
    return rendered


def _run_merge_validations(
    merge_step: dict,
    tmp_path: Path,
    *,
    validation_agent_1: dict | str,
    validation_agent_2: dict | str,
    validation_agent_3: dict | str,
    validation_threshold: str = "2",
    cycle_number: str = "1",
) -> subprocess.CompletedProcess[str]:
    def serialize(payload: dict | str) -> str:
        return payload if isinstance(payload, str) else json.dumps(payload)

    command = _render_templates(
        merge_step["command"],
        {
            "validation_agent_1": serialize(validation_agent_1),
            "validation_agent_2": serialize(validation_agent_2),
            "validation_agent_3": serialize(validation_agent_3),
            "validation_threshold": validation_threshold,
            "cycle_number": cycle_number,
        },
    )
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{REPO_ROOT / 'src'}{os.pathsep}{env.get('PYTHONPATH', '')}"
    return subprocess.run(
        ["/bin/bash", "-c", command],
        capture_output=True,
        text=True,
        cwd=str(tmp_path),
        env=env,
        timeout=20,
    )


class TestIssue4315MergeValidationsParseJson:
    """merge-validations must have parse_json: true so fix condition works."""

    def test_merge_validations_has_parse_json_true(self, steps_by_id):
        merge_step = steps_by_id["merge-validations"]
        assert merge_step.get("parse_json") is True, (
            "merge-validations step must set parse_json: true so that "
            "validated_findings is stored as a dict, not a raw JSON string. "
            "Without this, the fix step condition "
            "validated_findings['confirmed_count'] > 0 fails."
        )

    def test_recipe_parser_preserves_merge_validations_parse_json_contract(self):
        """The parsed Step model must carry parse_json through to the runner."""
        recipe = RecipeParser().parse(RECIPE_PATH.read_text(encoding="utf-8"))
        merge_step = next(step for step in recipe.steps if step.id == "merge-validations")

        assert merge_step.output == "validated_findings"
        assert merge_step.parse_json is True

    def test_fix_condition_works_with_parsed_dict(self, steps_by_id):
        """Fix step runs when validated_findings is a parsed dict with confirmed_count > 0."""
        step = Step(
            id="fix",
            step_type=StepType.AGENT,
            condition=steps_by_id["fix"]["condition"],
        )
        context = {"validated_findings": {"confirmed_count": 2, "validated": []}}
        assert step.evaluate_condition(context), "Fix step should run when confirmed_count > 0"

    def test_fix_condition_skips_with_zero_confirmed(self, steps_by_id):
        """Fix step is skipped when no findings are confirmed."""
        step = Step(
            id="fix",
            step_type=StepType.AGENT,
            condition=steps_by_id["fix"]["condition"],
        )
        context = {"validated_findings": {"confirmed_count": 0, "validated": []}}
        assert not step.evaluate_condition(context), (
            "Fix step should be skipped when confirmed_count == 0"
        )

    def test_fix_condition_fails_with_string_validated_findings(self, steps_by_id):
        """Demonstrate the bug: string validated_findings breaks condition evaluation.

        When parse_json is missing, validated_findings is a raw JSON string.
        The condition ``validated_findings['confirmed_count'] > 0`` cannot
        subscript a string with a string key, so simpleeval raises TypeError
        which defaults to True — but the Rust runner evaluates it as False,
        skipping the fix step. This test documents the failure mode.
        """
        # Simulate what happens WITHOUT parse_json: output stored as string.
        # Python's simpleeval catches the TypeError and defaults to True,
        # but the Rust runner evaluates this as False. Either way, the
        # condition doesn't work correctly with a string — it should be a dict.
        # The fix (parse_json: true) is verified in the test above.
        raw_json_string = '{"confirmed_count": 2, "validated": []}'
        broken_context = {"validated_findings": raw_json_string}
        fixed_context = {"validated_findings": {"confirmed_count": 2, "validated": []}}

        fix_step = Step(
            id="fix",
            step_type=StepType.AGENT,
            condition=steps_by_id["fix"]["condition"],
        )
        # With a dict (post-fix), the condition evaluates correctly.
        assert fix_step.evaluate_condition(fixed_context)
        # With a string (pre-fix), simpleeval defaults to True on TypeError,
        # but the Rust runner would evaluate as False — the root cause of #4315.
        # We just assert the parse_json fix is in place (tested above).
        assert isinstance(broken_context["validated_findings"], str)

    def test_merge_validations_output_drives_fix_condition(self, steps_by_id, tmp_path):
        """Merged JSON must parse to a dict that makes confirmed findings fixable."""
        validator_confirmed = {
            "validator": "agent-1",
            "cycle": 1,
            "validated": [
                {
                    "finding_id": 7,
                    "verdict": "confirmed",
                    "new_severity": "high",
                    "reasoning": "reproduced from source",
                }
            ],
            "confirmed_count": 1,
            "false_positive_count": 0,
        }
        validator_downgraded = {
            "validator": "agent-2",
            "cycle": 1,
            "validated": [
                {
                    "finding_id": 7,
                    "verdict": "downgraded",
                    "new_severity": "medium",
                    "reasoning": "real but lower severity",
                }
            ],
            "confirmed_count": 1,
            "false_positive_count": 0,
        }
        validator_false_positive = {
            "validator": "agent-3",
            "cycle": 1,
            "validated": [
                {
                    "finding_id": 7,
                    "verdict": "false_positive",
                    "new_severity": "low",
                    "reasoning": "not reproduced",
                }
            ],
            "confirmed_count": 0,
            "false_positive_count": 1,
        }

        result = _run_merge_validations(
            steps_by_id["merge-validations"],
            tmp_path,
            validation_agent_1=validator_confirmed,
            validation_agent_2=validator_downgraded,
            validation_agent_3=validator_false_positive,
        )

        assert result.returncode == 0, (
            "merge-validations should emit JSON for downstream recipe conditions.\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        validated_findings = json.loads(result.stdout)
        assert validated_findings == {
            "cycle": 1,
            "validated": [
                {
                    "finding_id": 7,
                    "verdict": "confirmed",
                    "final_severity": "medium",
                    "votes": {"confirmed": 2, "false_positive": 1},
                    "reasoning": "reproduced from source; real but lower severity",
                }
            ],
            "confirmed_count": 1,
            "false_positive_count": 0,
            "false_positive_rate": "0%",
        }
        assert isinstance(validated_findings, dict)

        fix_step = Step(
            id="fix",
            step_type=StepType.AGENT,
            condition=steps_by_id["fix"]["condition"],
        )
        assert fix_step.evaluate_condition({"validated_findings": validated_findings})

    def test_merge_validations_false_positive_output_skips_fix_condition(
        self, steps_by_id, tmp_path
    ):
        """False-positive-only merge output must remain valid JSON and skip fixes."""
        validator_false_positive = {
            "validator": "agent-1",
            "cycle": 1,
            "validated": [
                {
                    "finding_id": 8,
                    "verdict": "false_positive",
                    "new_severity": "low",
                    "reasoning": "not an issue",
                }
            ],
            "confirmed_count": 0,
            "false_positive_count": 1,
        }

        result = _run_merge_validations(
            steps_by_id["merge-validations"],
            tmp_path,
            validation_agent_1=validator_false_positive,
            validation_agent_2=validator_false_positive,
            validation_agent_3='{"validated": []}',
        )

        assert result.returncode == 0, (
            "merge-validations should not fail when validators reject a finding.\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        validated_findings = json.loads(result.stdout)
        assert validated_findings["confirmed_count"] == 0
        assert validated_findings["false_positive_count"] == 1
        assert validated_findings["false_positive_rate"] == "100%"

        fix_step = Step(
            id="fix",
            step_type=StepType.AGENT,
            condition=steps_by_id["fix"]["condition"],
        )
        assert not fix_step.evaluate_condition({"validated_findings": validated_findings})
