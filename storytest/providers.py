"""Plan providers: Claude (via the Anthropic API) and an offline heuristic provider."""
from __future__ import annotations

import os
import re
from typing import Protocol

from .models import PLAN_SCHEMA, Locator, Scenario, TestPlan
from .story import Story

SYSTEM_PROMPT = """You are a senior SDET. Turn the user story into a risk-based test plan.
Rules:
- Cover every acceptance criterion with at least one positive scenario; set `criterion` to it.
- Add negative, edge, security and accessibility scenarios only where the story makes them relevant.
- P0 = blocks release, P1 = core flow, P2 = important edge, P3 = nice to have.
- Pick the lowest level that proves the behaviour (api before ui where possible).
- Steps are short imperative actions; expected results are observable and checkable.
- Suggest stable data-testid locators (kebab-case) for every UI element the UI scenarios touch.
- List ambiguities in the story as open_questions instead of guessing.
- Scenario ids are TC-01, TC-02, ... in order."""


class Provider(Protocol):
    def generate(self, story: Story) -> TestPlan: ...


class ClaudeProvider:
    """Uses tool use with a forced tool choice so the output always matches PLAN_SCHEMA."""

    def __init__(self, model: str | None = None, api_key: str | None = None):
        try:
            import anthropic
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("Install the 'anthropic' package: pip install storytest[claude]") from exc
        self.client = anthropic.Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))
        self.model = model or os.environ.get("STORYTEST_MODEL", "claude-sonnet-5-5")

    def generate(self, story: Story) -> TestPlan:
        resp = self.client.messages.create(
            model=self.model,
            max_tokens=8000,
            system=SYSTEM_PROMPT,
            tools=[{
                "name": "submit_test_plan",
                "description": "Submit the structured test plan for the story.",
                "input_schema": PLAN_SCHEMA,
            }],
            tool_choice={"type": "tool", "name": "submit_test_plan"},
            messages=[{"role": "user", "content": story.as_prompt_text()}],
        )
        for block in resp.content:
            if getattr(block, "type", "") == "tool_use":
                return TestPlan.from_dict(block.input)
        raise RuntimeError("Claude did not return a test plan")


class HeuristicProvider:
    """Offline, deterministic provider. Good for demos, CI and stories without an API key."""

    _UI_NOUNS = re.compile(r"\b(button|field|input|page|screen|link|banner|message|toast|modal|dropdown|form|cart|checkbox)\b", re.I)
    _QUOTED = re.compile(r"[\"“']([^\"”']{2,40})[\"”']")
    _NUM = re.compile(r"\b\d+(?:\.\d+)?\b")

    def generate(self, story: Story) -> TestPlan:
        scenarios: list[Scenario] = []
        locators: dict[str, Locator] = {}
        criteria = story.acceptance_criteria or [story.title]

        def add(**kw) -> None:
            kw["id"] = f"TC-{len(scenarios) + 1:02d}"
            scenarios.append(Scenario(**kw))

        for i, ac in enumerate(criteria):
            is_ui = bool(self._UI_NOUNS.search(ac))
            given, when, then = self._split_gwt(ac)
            add(title=f"Verify: {self._short(ac)}", type="positive",
                priority="P0" if i == 0 else "P1", level="ui" if is_ui else "api",
                preconditions=[given] if given else ["User is logged in"],
                steps=[when] if when else [f"Perform the action described: {self._short(ac)}"],
                expected=[then] if then else [ac], criterion=ac)
            for q in self._QUOTED.findall(ac):
                tid = re.sub(r"[^a-z0-9]+", "-", q.lower()).strip("-")
                if tid and tid not in locators:
                    locators[tid] = Locator(name=q, test_id=tid, role="button" if "button" in ac.lower() else "")
            if self._NUM.search(ac):
                add(title=f"Boundary values for: {self._short(ac)}", type="edge", priority="P2",
                    level="api", steps=["Test the value just below, at, and just above each limit in the criterion"],
                    expected=["Behaviour switches exactly at the stated limit"], criterion=ac)
            if re.search(r"\b(invalid|error|fail|not|only|must|expired|limit)\b", ac, re.I):
                add(title=f"Negative path for: {self._short(ac)}", type="negative", priority="P1",
                    level="ui" if is_ui else "api", steps=["Provide input that violates the rule"],
                    expected=["Request is rejected with a clear, user-facing error", "No partial state is saved"],
                    criterion=ac)

        text = (story.description + " " + " ".join(criteria)).lower()
        if re.search(r"payment|price|amount|discount|coupon|order|checkout", text):
            add(title="Idempotency: repeat the same action twice quickly", type="edge", priority="P1", level="api",
                steps=["Send the same request twice concurrently"],
                expected=["Only one effect is applied", "Totals stay consistent"])
        if re.search(r"login|password|token|account|user", text):
            add(title="Unauthenticated access is blocked", type="security", priority="P1", level="api",
                steps=["Call the endpoint without a session or with an expired token"],
                expected=["401/403 returned", "No data leaked in the response body"])
        if any(s.level == "ui" for s in scenarios):
            add(title="Keyboard and screen-reader access for new UI", type="accessibility", priority="P2",
                level="manual", steps=["Navigate the new elements with keyboard only", "Inspect with a screen reader"],
                expected=["All controls reachable and labelled"], automate=False)

        return TestPlan(
            story_id=story.id, title=story.title,
            summary=f"{len(scenarios)} scenarios covering {len(criteria)} acceptance criteria (offline heuristic mode).",
            risks=["Generated without an LLM: review wording and add domain-specific cases."],
            scenarios=scenarios, locators=list(locators.values()),
            open_questions=[] if story.acceptance_criteria else ["Story has no acceptance criteria; coverage is a guess."],
        )

    @staticmethod
    def _short(text: str, n: int = 70) -> str:
        return text if len(text) <= n else text[: n - 1].rstrip() + "…"

    @staticmethod
    def _split_gwt(ac: str) -> tuple[str, str, str]:
        m = re.match(r"(?i)\s*given\s+(.*?),?\s+when\s+(.*?),?\s+then\s+(.*)$", ac)
        if not m:
            return "", "", ""
        return tuple(x.strip().rstrip(".") for x in m.groups())  # type: ignore[return-value]


def get_provider(name: str, model: str | None = None) -> Provider:
    if name == "claude":
        return ClaudeProvider(model=model)
    if name == "offline":
        return HeuristicProvider()
    if name == "auto":
        return ClaudeProvider(model=model) if os.environ.get("ANTHROPIC_API_KEY") else HeuristicProvider()
    raise ValueError(f"Unknown provider {name!r}")
