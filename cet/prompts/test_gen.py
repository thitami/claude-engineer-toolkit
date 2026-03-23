from __future__ import annotations
from typing import Optional, List
"""Prompt templates for the test generation tool."""

SYSTEM = """You are a senior backend engineer writing tests.
Generate a complete, runnable test file using the specified framework.

Rules:
- Use Arrange-Act-Assert structure
- Name tests descriptively: test_<function>_<scenario>_<expected>
- Cover: happy path, edge cases, error conditions
- Use fixtures and mocks appropriately
- Include docstrings only when the test intent isn't obvious from the name
- Generate realistic test data, not placeholder strings like "test_value"
- Output ONLY the Python test file — no explanation, no markdown fences
"""

USER_TEMPLATE = """Generate tests for this Python file.

**File:** `{filename}`
**Framework:** {framework}
{coverage_focus_line}
{project_context}

```python
{code}
```
"""

def build_user_prompt(
    filename: str,
    code: str,
    framework: str = "pytest",
    coverage_focus: Optional[str] = None,
    project_context: str = "",
) -> str:
    coverage_focus_line = f"**Coverage focus:** {coverage_focus}" if coverage_focus else ""
    return USER_TEMPLATE.format(
        filename=filename,
        code=code,
        framework=framework,
        coverage_focus_line=coverage_focus_line,
        project_context=project_context,
    )
