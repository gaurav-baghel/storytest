# storytest

![CI](https://github.com/gaurav-baghel/storytest/actions/workflows/ci.yml/badge.svg)

**Turn a user story into a risk-based test plan, Playwright test skeletons and a locator contract, in one command.**

SDETs spend hours reading Jira stories and writing out test cases before a single test is automated. `storytest` does the first pass for you:

```
story (Markdown or Jira JSON)
        │
        ▼
  Claude (structured tool output)  ── or ──  offline heuristic engine
        │
        ▼
 ┌──────────────┬────────────────┬──────────────────┬───────────────────┐
 │ plan.md      │ plan.json      │ spec.ts          │ locators.json     │
 │ for review   │ for tooling    │ Playwright Test  │ data-testid list  │
 └──────────────┴────────────────┴──────────────────┴───────────────────┘
```

## Features

- **Covers every acceptance criterion:** each one maps to at least one positive scenario, with negative, boundary, security and accessibility cases added where they are relevant.
- **Risk-based priorities (P0-P3)** and the lowest test level that proves the behaviour (API before UI).
- **Schema-validated output:** Claude is forced to answer through a tool with a JSON schema, and every plan is validated (priorities, types, duplicate IDs) before anything is written.
- **Playwright skeletons that compile:** one `test()` per automatable scenario, `test.step()` per step, priority and type tags (`@p0 @negative`) for `--grep`, marked `test.fixme` until implemented. CI type-checks them with `tsc --strict`.
- **Locator contract:** suggested `data-testid` values to agree with developers before the UI is built.
- **Works offline:** with no API key it falls back to a deterministic heuristic engine (Given/When/Then parsing, boundary detection from numbers, negative paths from rule words, domain checks for payments and auth).
- **Jira-ready input:** reads Markdown/plain text or a Jira issue JSON export, including Jira Cloud's rich-text (ADF) descriptions.

## Quick start

```bash
pip install -e ".[claude,dev]"

# Offline (no key needed)
storytest generate examples/stories/SHOP-142.md -p offline -o out

# With Claude
export ANTHROPIC_API_KEY=sk-...
storytest generate examples/stories/*.md examples/stories/*.json -o out
```

Output:

```
ok SHOP-142: 12 scenarios (accessibility=1, edge=2, negative=3, positive=5, security=1) -> out
ok AUTH-77: 6 scenarios (accessibility=1, edge=1, positive=3, security=1) -> out
```

| Flag | Meaning |
|---|---|
| `-p auto` (default) | Claude if `ANTHROPIC_API_KEY` is set, otherwise offline |
| `-p claude` / `-p offline` | Force a provider |
| `-m MODEL` | Claude model id (or set `STORYTEST_MODEL`) |
| `-o DIR` | Output directory (default `out/`) |

## Example

Input: [`examples/stories/SHOP-142.md`](examples/stories/SHOP-142.md)

```markdown
# SHOP-142: Apply a coupon code at checkout
## Acceptance criteria
- Given a logged-in user with items in the cart, when they enter a valid code and click "Apply coupon", then the order total is reduced by the coupon discount.
- A coupon only applies when the cart subtotal is at least 499.
...
```

Generated Playwright skeleton (excerpt):

```ts
const ids = {
  applyCoupon: 'apply-coupon', // Apply coupon
  remove: 'remove', // Remove
} as const;

test.describe('SHOP-142: Apply a coupon code at checkout', () => {
  test('TC-01 Verify: Given a logged-in user with items in the cart, ... @p0 @positive', async ({ page }) => {
    test.fixme(true, 'Generated skeleton: implement steps');
    await test.step('they enter a valid code and click "Apply coupon"', async () => {
      // TODO
    });
    // expect: the order total is reduced by the coupon discount
  });
```

Full generated outputs are in [`examples/output/`](examples/output/).

## Project layout

```
storytest/
  story.py      # Markdown and Jira (ADF) parsing
  models.py     # TestPlan schema and validation
  providers.py  # ClaudeProvider (forced tool use) and HeuristicProvider
  render.py     # Markdown, Playwright and locator renderers
  cli.py        # storytest generate ...
tests/          # pytest suite, including a mocked Claude client
```

## Running the tests

```bash
pytest -q
```

CI runs the suite on Python 3.10 and 3.12, generates plans for the example stories and type-checks the generated specs.

## Roadmap

- Pull stories straight from Jira by key
- Generate Rest-Assured (Java) skeletons for API scenarios
- Diff mode: update an existing plan when a story changes

## License

MIT
