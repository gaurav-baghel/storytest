"""Command line entry point: storytest generate <story> [-o out/]."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .models import TestPlan
from .providers import get_provider
from .render import to_locator_contract, to_markdown, to_playwright
from .story import load_story


def write_outputs(plan: TestPlan, out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = plan.story_id.lower()
    files = {
        out_dir / f"{stem}.plan.md": to_markdown(plan),
        out_dir / f"{stem}.plan.json": json.dumps(plan.to_dict(), indent=2) + "\n",
        out_dir / f"{stem}.spec.ts": to_playwright(plan),
        out_dir / f"{stem}.locators.json": to_locator_contract(plan),
    }
    for path, content in files.items():
        path.write_text(content, encoding="utf-8")
    return list(files)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="storytest",
                                 description="Turn user stories into test plans and Playwright skeletons.")
    ap.add_argument("--version", action="version", version=f"storytest {__version__}")
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("generate", help="Generate a test plan from story files (.md, .txt or Jira .json)")
    g.add_argument("stories", nargs="+", type=Path)
    g.add_argument("-o", "--out", type=Path, default=Path("out"))
    g.add_argument("-p", "--provider", choices=["auto", "claude", "offline"], default="auto",
                   help="auto uses Claude when ANTHROPIC_API_KEY is set, otherwise offline")
    g.add_argument("-m", "--model", help="Claude model id (default: $STORYTEST_MODEL or claude-sonnet-5-5)")
    args = ap.parse_args(argv)

    provider = get_provider(args.provider, args.model)
    failed = 0
    for path in args.stories:
        try:
            story = load_story(path)
            plan = provider.generate(story)
            written = write_outputs(plan, args.out)
        except Exception as exc:  # report and keep going with other stories
            print(f"x {path}: {exc}", file=sys.stderr)
            failed += 1
            continue
        cov = ", ".join(f"{k}={v}" for k, v in sorted(plan.coverage().items()))
        print(f"ok {story.id}: {len(plan.scenarios)} scenarios ({cov}) -> {written[0].parent}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
