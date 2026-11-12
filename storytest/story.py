"""Parse a user story from Markdown/plain text or a Jira issue JSON export."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Story:
    id: str
    title: str
    description: str
    acceptance_criteria: list[str] = field(default_factory=list)

    def as_prompt_text(self) -> str:
        ac = "\n".join(f"- {c}" for c in self.acceptance_criteria) or "(none given)"
        return (f"Story ID: {self.id}\nTitle: {self.title}\n\nDescription:\n{self.description}\n\n"
                f"Acceptance criteria:\n{ac}")


_AC_HEADER = re.compile(r"^#+\s*acceptance criteria|^acceptance criteria\s*:?", re.I)
_BULLET = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+(.*)$")


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:40] or "story"


def parse_markdown(text: str, fallback_id: str = "") -> Story:
    lines = text.strip().splitlines()
    title, story_id = "", fallback_id
    desc: list[str] = []
    ac: list[str] = []
    in_ac = False
    for raw in lines:
        line = raw.rstrip()
        if not title and line.startswith("# "):
            title = line[2:].strip()
            m = re.match(r"^([A-Z][A-Z0-9]+-\d+)[:\s]+(.*)$", title)
            if m:
                story_id, title = m.group(1), m.group(2).strip()
            continue
        if _AC_HEADER.match(line.strip()):
            in_ac = True
            continue
        if in_ac and line.startswith("#"):
            in_ac = False
        if in_ac:
            m = _BULLET.match(line)
            if m:
                ac.append(m.group(1).strip())
            elif line.strip() and ac:
                ac[-1] += " " + line.strip()  # wrapped bullet
        else:
            desc.append(line)
    if not title:
        title = next((l.strip() for l in lines if l.strip()), "Untitled story")
    return Story(id=story_id or _slug(title), title=title,
                 description="\n".join(desc).strip(), acceptance_criteria=ac)


def _adf_to_text(node) -> str:
    """Flatten Atlassian Document Format (Jira Cloud descriptions) to text."""
    if isinstance(node, str):
        return node
    if isinstance(node, list):
        return "".join(_adf_to_text(n) for n in node)
    if not isinstance(node, dict):
        return ""
    if node.get("type") == "text":
        return node.get("text", "")
    inner = _adf_to_text(node.get("content", []))
    if node.get("type") == "listItem":
        return "- " + inner.strip() + "\n"
    if node.get("type") in ("paragraph", "heading"):
        prefix = "## " if node.get("type") == "heading" else ""
        return prefix + inner + "\n"
    return inner


def parse_jira_json(data: dict) -> Story:
    fields = data.get("fields", data)
    desc = fields.get("description") or ""
    if isinstance(desc, dict):
        desc = _adf_to_text(desc)
    body = parse_markdown(f"# {fields.get('summary', 'Untitled')}\n{desc}")
    return Story(id=data.get("key") or body.id, title=fields.get("summary", body.title),
                 description=body.description, acceptance_criteria=body.acceptance_criteria)


def load_story(path: str | Path) -> Story:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    if p.suffix.lower() == ".json":
        return parse_jira_json(json.loads(text))
    return parse_markdown(text, fallback_id=p.stem.upper() if re.match(r"^[A-Za-z]+-\d+$", p.stem) else "")
