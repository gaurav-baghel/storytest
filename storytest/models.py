"""Data model for a generated test plan."""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any

PRIORITIES = ("P0", "P1", "P2", "P3")
TEST_TYPES = ("positive", "negative", "edge", "security", "accessibility", "api")
LEVELS = ("ui", "api", "unit", "manual")


class PlanValidationError(ValueError):
    """Raised when a plan returned by a provider does not match the schema."""


@dataclass
class Locator:
    name: str          # human name, e.g. "Apply coupon button"
    test_id: str       # suggested data-testid, e.g. "apply-coupon-btn"
    role: str = ""     # ARIA role hint, e.g. "button"


@dataclass
class Scenario:
    id: str
    title: str
    type: str
    priority: str
    level: str
    preconditions: list[str] = field(default_factory=list)
    steps: list[str] = field(default_factory=list)
    expected: list[str] = field(default_factory=list)
    automate: bool = True
    criterion: str = ""  # acceptance criterion this scenario covers


@dataclass
class TestPlan:
    story_id: str
    title: str
    summary: str
    risks: list[str]
    scenarios: list[Scenario]
    locators: list[Locator]
    open_questions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TestPlan":
        try:
            scenarios = [Scenario(**s) for s in data["scenarios"]]
            locators = [Locator(**l) for l in data.get("locators", [])]
            plan = cls(
                story_id=str(data["story_id"]),
                title=str(data["title"]),
                summary=str(data.get("summary", "")),
                risks=list(data.get("risks", [])),
                scenarios=scenarios,
                locators=locators,
                open_questions=list(data.get("open_questions", [])),
            )
        except (KeyError, TypeError) as exc:
            raise PlanValidationError(f"Plan does not match schema: {exc}") from exc
        plan.validate()
        return plan

    def validate(self) -> None:
        if not self.scenarios:
            raise PlanValidationError("Plan has no scenarios")
        seen: set[str] = set()
        for s in self.scenarios:
            if s.id in seen:
                raise PlanValidationError(f"Duplicate scenario id: {s.id}")
            seen.add(s.id)
            if s.priority not in PRIORITIES:
                raise PlanValidationError(f"{s.id}: bad priority {s.priority!r}")
            if s.type not in TEST_TYPES:
                raise PlanValidationError(f"{s.id}: bad type {s.type!r}")
            if s.level not in LEVELS:
                raise PlanValidationError(f"{s.id}: bad level {s.level!r}")
            if not s.steps or not s.expected:
                raise PlanValidationError(f"{s.id}: needs steps and expected results")
        ids = [l.test_id for l in self.locators]
        if len(ids) != len(set(ids)):
            raise PlanValidationError("Duplicate locator test_id")

    def coverage(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for s in self.scenarios:
            out[s.type] = out.get(s.type, 0) + 1
        return out


# JSON schema used to force Claude's tool output into this shape.
PLAN_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["story_id", "title", "summary", "risks", "scenarios", "locators"],
    "properties": {
        "story_id": {"type": "string"},
        "title": {"type": "string"},
        "summary": {"type": "string"},
        "risks": {"type": "array", "items": {"type": "string"}},
        "open_questions": {"type": "array", "items": {"type": "string"}},
        "locators": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "test_id"],
                "properties": {
                    "name": {"type": "string"},
                    "test_id": {"type": "string"},
                    "role": {"type": "string"},
                },
            },
        },
        "scenarios": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id", "title", "type", "priority", "level", "steps", "expected"],
                "properties": {
                    "id": {"type": "string"},
                    "title": {"type": "string"},
                    "type": {"type": "string", "enum": list(TEST_TYPES)},
                    "priority": {"type": "string", "enum": list(PRIORITIES)},
                    "level": {"type": "string", "enum": list(LEVELS)},
                    "preconditions": {"type": "array", "items": {"type": "string"}},
                    "steps": {"type": "array", "items": {"type": "string"}},
                    "expected": {"type": "array", "items": {"type": "string"}},
                    "automate": {"type": "boolean"},
                    "criterion": {"type": "string"},
                },
            },
        },
    },
}
