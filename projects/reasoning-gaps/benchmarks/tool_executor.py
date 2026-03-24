"""Python code execution tool for ReasonGap tool-use evaluation condition.

Provides a sandboxed Python subprocess executor that models can call via
the tool_use API. Used for the tool_use condition to test whether models
can solve algorithmic problems by writing and executing code.

Safety constraints:
- 30-second execution timeout
- No network access (blocked imports)
- No file writes (blocked built-ins)
- Limited import allowlist
"""

from __future__ import annotations

import logging
import re
import subprocess
import sys
import textwrap
from typing import Any

logger = logging.getLogger(__name__)

# Maximum execution time for a single code snippet
EXECUTION_TIMEOUT: int = 30

# Imports allowed in the sandboxed environment
ALLOWED_IMPORTS: set[str] = {
    "math", "itertools", "functools", "collections", "heapq",
    "bisect", "operator", "string", "re", "json", "copy",
    "decimal", "fractions", "random", "statistics", "typing",
}

# Imports explicitly blocked (network, filesystem, subprocess)
BLOCKED_IMPORTS: set[str] = {
    "os", "sys", "subprocess", "socket", "http", "urllib",
    "requests", "shutil", "pathlib", "tempfile", "glob",
    "signal", "ctypes", "importlib", "builtins", "__builtin__",
}

# Tool definition for Anthropic API
ANTHROPIC_TOOL_DEFINITION: dict[str, Any] = {
    "name": "python_execute",
    "description": (
        "Execute Python code and return the output. "
        "Use this to solve algorithmic problems. "
        "Print your final answer on the last line."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "Python code to execute",
            }
        },
        "required": ["code"],
    },
}

# Tool definition for OpenAI API
OPENAI_TOOL_DEFINITION: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "python_execute",
        "description": (
            "Execute Python code and return the output. "
            "Use this to solve algorithmic problems. "
            "Print your final answer on the last line."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Python code to execute",
                }
            },
            "required": ["code"],
        },
    },
}

# System prompt for tool-use condition
TOOL_USE_SYSTEM_PROMPT: str = (
    "You have access to a python_execute tool. "
    "Write and execute Python code to solve this problem. "
    "Return only the final answer on the last line."
)

# Fallback prompt for OpenRouter (no native tool_use support)
OPENROUTER_TOOL_PROMPT: str = (
    "You have access to a Python execution environment. "
    "Write Python code in a ```python code block to solve this problem. "
    "The code will be executed and the output returned to you. "
    "Print only the final answer as the last line of output."
)


def _check_code_safety(code: str) -> str | None:
    """Check code for unsafe patterns. Returns error message if unsafe, None if OK."""
    # Check for blocked imports
    import_pattern = re.compile(
        r'(?:^|\s)(?:import|from)\s+(\w+)', re.MULTILINE
    )
    for match in import_pattern.finditer(code):
        module = match.group(1)
        if module in BLOCKED_IMPORTS:
            return f"Import of '{module}' is not allowed in sandboxed execution."

    # Check for dangerous built-in calls
    dangerous_calls = [
        (r'\bopen\s*\(', "File operations are not allowed."),
        (r'\bexec\s*\(', "exec() is not allowed."),
        (r'\beval\s*\(', "eval() is not allowed."),
        (r'\bcompile\s*\(', "compile() is not allowed."),
        (r'\b__import__\s*\(', "__import__() is not allowed."),
    ]
    for pattern, msg in dangerous_calls:
        if re.search(pattern, code):
            return msg

    return None


def execute_python(code: str) -> dict[str, str]:
    """Execute Python code in a sandboxed subprocess.

    Args:
        code: Python code string to execute.

    Returns:
        Dict with 'stdout', 'stderr', and 'success' fields.
    """
    # Pre-check code safety
    safety_error = _check_code_safety(code)
    if safety_error:
        return {
            "stdout": "",
            "stderr": f"Safety error: {safety_error}",
            "success": False,
        }

    # Build a wrapper script that restricts the execution environment
    wrapper = textwrap.dedent("""\
        import sys
        # Remove dangerous modules from importable set
        _blocked = {blocked_str}
        class _ImportBlocker:
            def find_module(self, name, path=None):
                if name.split('.')[0] in _blocked:
                    return self
                return None
            def load_module(self, name):
                raise ImportError(f"Import of '{{name}}' is blocked in sandboxed execution.")
        sys.meta_path.insert(0, _ImportBlocker())

        # Execute user code
        {code}
    """).format(
        blocked_str=repr(BLOCKED_IMPORTS),
        code=textwrap.indent(code, ""),
    )

    try:
        result = subprocess.run(
            [sys.executable, "-c", wrapper],
            capture_output=True,
            text=True,
            timeout=EXECUTION_TIMEOUT,
            env={
                "PATH": "",
                "HOME": "/tmp",
                "LANG": "en_US.UTF-8",
            },
        )

        return {
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "success": result.returncode == 0,
        }

    except subprocess.TimeoutExpired:
        return {
            "stdout": "",
            "stderr": f"Execution timed out after {EXECUTION_TIMEOUT} seconds.",
            "success": False,
        }
    except Exception as exc:
        return {
            "stdout": "",
            "stderr": f"Execution error: {exc}",
            "success": False,
        }


def extract_code_from_response(response: str) -> str | None:
    """Extract Python code from a model response containing ```python blocks.

    Used for OpenRouter fallback where models don't have native tool_use.

    Args:
        response: Model response text.

    Returns:
        Extracted code string, or None if no code block found.
    """
    # Look for ```python ... ``` blocks
    pattern = re.compile(r'```python\s*\n(.*?)```', re.DOTALL)
    matches = pattern.findall(response)
    if matches:
        # Return the last code block (models sometimes write multiple)
        return matches[-1].strip()

    # Fallback: look for generic ``` ... ``` blocks
    pattern = re.compile(r'```\s*\n(.*?)```', re.DOTALL)
    matches = pattern.findall(response)
    if matches:
        return matches[-1].strip()

    return None


def get_last_output_line(output: str) -> str:
    """Extract the last non-empty line from execution output.

    This is where the model's final answer should be printed.

    Args:
        output: stdout from code execution.

    Returns:
        Last non-empty line, or empty string.
    """
    lines = [line.strip() for line in output.strip().split("\n") if line.strip()]
    return lines[-1] if lines else ""
