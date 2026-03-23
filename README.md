# 🛠️ claude-engineer-toolkit (`cet`)

> A CLI toolkit that brings Claude AI into your daily backend engineering workflow.  
> Not a chatbot. Not a playground. **Sharp tools for working engineers.**

[![PyPI version](https://badge.fury.io/py/claude-engineer-toolkit.svg)](https://badge.fury.io/py/claude-engineer-toolkit)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

```
pip install claude-engineer-toolkit
export ANTHROPIC_API_KEY=your_key

cet explain legacy_auth.php          # understand any code in seconds
cet pr --diff                        # review your staged changes like a senior
cet test user_service.py             # generate pytest scaffolds instantly
cet spec ./routes/                   # generate OpenAPI spec from your code
```

---

## Why `cet`?

You already use Claude in the browser. `cet` brings it **into your terminal, your git hooks, and your CI pipeline** — where you actually work.

Each tool is:
- **Independent** — use one, ignore the rest
- **Composable** — pipes into your existing workflow
- **Configurable** — override prompts and behavior via `.cet.toml`
- **Fast** — responses are cached so re-runs on unchanged files are instant

---

## Tools

### `cet explain` — Understand any code instantly

Feed it a file (any language) and get a plain-English breakdown.

```bash
cet explain legacy_payment_processor.php
cet explain src/auth/jwt_middleware.go --focus security
cet explain complicated_query.sql --format markdown > explanation.md
```

**Output includes:**
- High-level summary
- Component breakdown (class by class / function by function)
- Hidden complexity & gotchas
- Suggested improvements

---

### `cet pr` — PR review like a senior engineer

Reviews your staged git diff and gives structured, actionable feedback.

```bash
cet pr                              # reviews staged changes
cet pr --branch main                # compares current branch to main
cet pr --focus security             # security-focused review
```

**Output includes:**
- Overall assessment (approve / request changes / needs discussion)
- File-by-file breakdown with line-level comments
- Security and performance flags

---

### `cet test` — Generate test scaffolds instantly

Point it at any Python file and get a ready-to-run pytest scaffold.

```bash
cet test src/services/user_service.py
cet test src/api/payments.py --coverage-focus edge-cases
```

**Output includes:**
- Full pytest file with imports and fixtures
- Happy path + edge case tests
- Suggested mocks and patches

---

### `cet spec` — Generate OpenAPI specs from code

Point it at your routes/controllers and get a valid OpenAPI 3.1 spec.

```bash
cet spec src/routes/
cet spec src/api/users.py --output openapi.yaml
cet spec . --framework fastapi
```

---

## Installation

```bash
pip install claude-engineer-toolkit
export ANTHROPIC_API_KEY=your_key_here
cet --version
```

---

## Configuration (`.cet.toml`)

```toml
[project]
name = "my-api"
language = "python"
framework = "fastapi"

[claude]
model = "claude-sonnet-4-5"
cache = true

[tools.pr]
focus = "security"
team_conventions = """
  - We use conventional commits
  - SQLAlchemy preferred over raw SQL
"""

[tools.test]
framework = "pytest"
output_dir = "tests/"

[tools.spec]
output = "docs/openapi.yaml"
```

---

## Plugin System

```python
from cet import tool, ClaudeClient

@tool("db-review", description="Review SQL migrations for risk")
def db_review(file: str, client: ClaudeClient) -> str:
    code = open(file).read()
    return client.ask(prompt_template="db_review", context={"code": code})
```

```bash
cet db-review migrations/0042_add_payments.sql
```

---

## GitHub Actions

```yaml
- name: Install cet
  run: pip install claude-engineer-toolkit

- name: AI PR Review
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  run: cet pr --branch ${{ github.base_ref }}
```

---

## Roadmap

- [ ] `cet doc` — generate inline docs and README sections
- [ ] `cet env` — audit `.env` files for missing vars and security risks
- [ ] `cet migrate` — PHP → Python migration co-pilot
- [ ] VS Code extension

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). New tools especially welcome.

```bash
git clone https://github.com/yourusername/claude-engineer-toolkit
cd claude-engineer-toolkit
pip install -e ".[dev]"
pytest
```

---

MIT License · Built by a backend engineer, for backend engineers.
