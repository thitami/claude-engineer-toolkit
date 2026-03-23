# Contributing to claude-engineer-toolkit

Contributions are very welcome — especially new tools.

## Setup

```bash
git clone https://github.com/yourusername/claude-engineer-toolkit
cd claude-engineer-toolkit
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Adding a New Tool

Each tool consists of three files:

1. **`cet/prompts/mytool.py`** — system prompt + user prompt builder
2. **`cet/tools/mytool.py`** — tool logic (file reading, calling client, formatting output)
3. **`cet/cli.py`** — register the new `@app.command()`

### Step 1: Write your prompts

```python
# cet/prompts/mytool.py

SYSTEM = """You are a senior engineer doing X.
Output format: ...
"""

USER_TEMPLATE = """Do X for this code:
{code}
"""

def build_user_prompt(code: str) -> str:
    return USER_TEMPLATE.format(code=code)
```

### Step 2: Write your tool

```python
# cet/tools/mytool.py
from cet.config import Config
from cet.client import ClaudeClient
from cet.prompts import mytool as prompts

def mytool_tool(file: str, no_cache: bool) -> None:
    config = Config.load()
    client = ClaudeClient(config)
    code = open(file).read()
    result = client.ask(
        system=prompts.SYSTEM,
        user=prompts.build_user_prompt(code),
        tool_name="mytool",
        use_cache=not no_cache,
    )
    print(result)
```

### Step 3: Register the command in `cli.py`

```python
from cet.tools.mytool import mytool_tool

@app.command()
def mytool(file: str = typer.Argument(...)):
    """My new tool."""
    mytool_tool(file=file, no_cache=False)
```

### Step 4: Write tests

```bash
pytest tests/ -v
```

## Code Style

```bash
ruff check .
mypy cet/
```

## PR Checklist

- [ ] New tool follows the 3-file pattern above
- [ ] Tests added in `tests/`
- [ ] README updated with the new tool's usage
- [ ] `ruff` and `mypy` pass
