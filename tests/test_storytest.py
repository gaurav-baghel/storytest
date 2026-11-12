import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from storytest.cli import main
from storytest.models import PlanValidationError, TestPlan
from storytest.providers import ClaudeProvider, HeuristicProvider
from storytest.render import to_markdown, to_playwright
from storytest.story import load_story, parse_markdown

EXAMPLES = Path(__file__).parent.parent / "examples" / "stories"


def test_parse_markdown_extracts_id_title_and_criteria():
    s = load_story(EXAMPLES / "SHOP-142.md")
    assert s.id == "SHOP-142"
    assert s.title == "Apply a coupon code at checkout"
    assert len(s.acceptance_criteria) == 5


def test_parse_jira_adf_json():
    s = load_story(EXAMPLES / "AUTH-77.json")
    assert s.id == "AUTH-77"
    assert len(s.acceptance_criteria) == 3
    assert "locked" in s.acceptance_criteria[0]


def test_wrapped_bullets_are_joined():
    s = parse_markdown("# X-1: T\n## Acceptance criteria\n- first line\n  continues here\n- second")
    assert s.acceptance_criteria == ["first line continues here", "second"]


def test_every_criterion_has_a_positive_scenario():
    story = load_story(EXAMPLES / "SHOP-142.md")
    plan = HeuristicProvider().generate(story)
    covered = {s.criterion for s in plan.scenarios if s.type == "positive"}
    assert set(story.acceptance_criteria) <= covered
    plan.validate()


def test_boundary_and_negative_cases_are_added():
    plan = HeuristicProvider().generate(load_story(EXAMPLES / "SHOP-142.md"))
    types = plan.coverage()
    assert types.get("edge", 0) >= 1 and types.get("negative", 0) >= 1


def test_validation_rejects_bad_priority():
    bad = {"story_id": "A-1", "title": "t", "summary": "", "risks": [], "locators": [],
           "scenarios": [{"id": "TC-01", "title": "x", "type": "positive", "priority": "P9",
                          "level": "ui", "steps": ["a"], "expected": ["b"]}]}
    with pytest.raises(PlanValidationError):
        TestPlan.from_dict(bad)


def test_playwright_spec_escapes_quotes_and_skips_manual():
    plan = HeuristicProvider().generate(load_story(EXAMPLES / "SHOP-142.md"))
    spec = to_playwright(plan)
    assert "import { test, expect } from '@playwright/test';" in spec
    assert "@accessibility" not in spec  # manual scenario is not emitted
    for line in spec.splitlines():
        if line.strip().startswith("test("):
            body = line.split("test(", 1)[1]
            assert body.count("'") - body.count("\\'") == 2  # one quoted, escaped title


def test_markdown_has_scenario_table():
    md = to_markdown(HeuristicProvider().generate(load_story(EXAMPLES / "AUTH-77.json")))
    assert "| ID | Title |" in md and "TC-01" in md


def test_claude_provider_parses_tool_output():
    payload = {"story_id": "A-1", "title": "t", "summary": "s", "risks": [], "locators": [
        {"name": "Login button", "test_id": "login-btn", "role": "button"}],
        "scenarios": [{"id": "TC-01", "title": "login works", "type": "positive", "priority": "P0",
                       "level": "ui", "steps": ["click login"], "expected": ["dashboard shown"]}]}
    calls = {}

    class FakeMessages:
        def create(self, **kw):
            calls.update(kw)
            return SimpleNamespace(content=[SimpleNamespace(type="tool_use", input=payload)])

    provider = ClaudeProvider.__new__(ClaudeProvider)
    provider.client = SimpleNamespace(messages=FakeMessages())
    provider.model = "test-model"
    plan = provider.generate(parse_markdown("# A-1: t\n## Acceptance criteria\n- login works"))
    assert plan.scenarios[0].title == "login works"
    assert calls["tool_choice"] == {"type": "tool", "name": "submit_test_plan"}


def test_cli_writes_all_outputs(tmp_path):
    rc = main(["generate", str(EXAMPLES / "SHOP-142.md"), "-p", "offline", "-o", str(tmp_path)])
    assert rc == 0
    names = sorted(p.name for p in tmp_path.iterdir())
    assert names == ["shop-142.locators.json", "shop-142.plan.json", "shop-142.plan.md", "shop-142.spec.ts"]
    TestPlan.from_dict(json.loads((tmp_path / "shop-142.plan.json").read_text()))
