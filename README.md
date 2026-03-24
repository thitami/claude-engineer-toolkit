# 🛠️ claude-engineer-toolkit (`cet`)

> Claude AI in your terminal. Not a chatbot wrapper —
> **sharp, composable tools for backend engineers who ship.**

[![PyPI version](https://badge.fury.io/py/claude-engineer-toolkit.svg)](https://badge.fury.io/py/claude-engineer-toolkit)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-48%20passing-brightgreen.svg)](tests/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
```bash
pip install claude-engineer-toolkit
export ANTHROPIC_API_KEY=your_key

cet explain legacy_auth.php             # understand any code in seconds
cet pr --branch main                    # review your diff like a senior engineer
cet spec ./routes/ --framework fastapi  # generate OpenAPI spec from code
```


---

![cet demo](demo/cet-demo.gif)

---

## The problem

You open a legacy file. 400 lines of PHP written in 2014. No docs, no tests, no author.
You need to understand it in 10 minutes.

Or: you are reviewing a PR while context-switching from three other things.
You want a second opinion before you approve.

Or: you need an OpenAPI spec for a service that was never documented.

`cet` solves these. One command, one answer, back to work.

---

## Tools

### `cet explain` — understand any code instantly

Any language. Any size. Structured breakdown: what it does, how it works, what will bite you.
```bash
cet explain legacy_payment_processor.php
cet explain src/auth/jwt_middleware.go --focus security
cet explain complicated_query.sql --format markdown > explanation.md
```

Output:
- **Summary** — what this code does and why it exists
- **Component breakdown** — function by function, non-obvious logic called out
- **Gotchas** — silent failures, global state, security assumptions, framework magic
- **Improvements** — specific, named, actionable (not "add error handling")

---

### `cet pr` — PR review like a senior engineer

Reviews your staged changes or branch diff. Verdict, real issues, no noise.
```bash
cet pr                              # review staged changes
cet pr --branch main                # compare current branch to main
cet pr --focus security             # security-focused review
cet pr --output github-comment      # format for GitHub Actions comment
```

Output:
- **Verdict** — Approve / Request Changes / Needs Discussion
- **File-by-file review** with quoted diff lines for each flag
- **Severity flags** — SECURITY · BUG · PERF · DESIGN
- **Action items** — numbered, merge-blocking issues only

---

### `cet spec` — generate OpenAPI specs from code

Point it at your routes and get a valid OpenAPI 3.1 YAML. Framework-aware.
```bash
cet spec src/routes/
cet spec src/api/users.py --output docs/openapi.yaml
cet spec . --framework fastapi
cet spec . --framework flask --format json
```

Output: valid OpenAPI 3.1 YAML with inferred schemas, auth, status codes, and realistic examples.

---

## Installation
```bash
pip install claude-engineer-toolkit
export ANTHROPIC_API_KEY=your_key  # get yours at console.anthropic.com
cet --help
```

Requires Python 3.9+. Works on macOS, Linux, Windows.

---

## Configuration

Drop a `.cet.toml` in your project root. `cet` walks up the directory tree to find it.
```toml
[project]
name = "billing-api"
language = "python"
framework = "fastapi"

[claude]
model = "claude-sonnet-4-5"
cache = true

[tools.pr]
focus = "security"
team_conventions = """
  - Conventional commits (feat:, fix:, chore:)
  - SQLAlchemy only — no raw SQL
  - All public endpoints must have docstrings
"""

[tools.spec]
output = "docs/openapi.yaml"
```

Team conventions are injected into the PR review prompt — reviews feel like they know your codebase.

---


## Docker

No Python setup required — run `cet` directly from Docker.

**One-off run:**
```bash
docker run --rm \
  -e ANTHROPIC_API_KEY=your_key \
  -v $(pwd):/code \
  ghcr.io/thitami/claude-engineer-toolkit \
  explain src/auth.py
```

**With docker compose (mounts your current project):**
```bash
export ANTHROPIC_API_KEY=your_key
docker compose run --rm cet explain src/auth.py
docker compose run --rm cet pr --branch main
docker compose run --rm cet spec src/routes/
```

**In GitHub Actions CI:**
```yaml
- name: AI PR Review
  run: |
    docker run --rm \
      -e ANTHROPIC_API_KEY=${{ secrets.ANTHROPIC_API_KEY }} \
      -v ${{ github.workspace }}:/code \
      ghcr.io/thitami/claude-engineer-toolkit \
      pr --branch ${{ github.base_ref }}
```

## GitHub Actions
```yaml
name: AI PR Review
on: [pull_request]
jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - run: pip install claude-engineer-toolkit
      - run: cet pr --branch ${{ github.base_ref }} --output github-comment
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

---

## Caching

Responses cached locally at `~/.cet/cache/`, keyed on file content hash.
Re-running `cet explain` on an unchanged file is instant and free.
```bash
cet cache --status    # show cache size
cet cache --clear     # clear everything
```

---

## Roadmap

- [x] `cet test` — generate pytest scaffolds for any Python file
- [x] `cet doc` — add inline docs and docstrings to any code file
- [ ] `cet env` — audit `.env` files for missing vars and security risks
- [ ] `cet migrate` — PHP to Python migration co-pilot
- [ ] Plugin system — add custom tools via decorator
- [ ] VS Code extension

---

## Contributing

New tools are especially welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).
```bash
git clone https://github.com/thitami/claude-engineer-toolkit
cd claude-engineer-toolkit
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest   # 48 tests, all green
```

---

MIT License

*Built by a backend engineer with 14 years of PHP and Python scars.
If you have ever opened a legacy file and thought "what is this" — this tool is for you.*
