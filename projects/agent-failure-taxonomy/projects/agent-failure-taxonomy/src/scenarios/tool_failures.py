"""
Tool-use failure scenarios for controlled reproduction.

Scenarios in this file:
- tool_fabrication: Agent fabricates non-existent tool
- tool_hallucination: Agent hallucinates tool execution
"""

from typing import List, Dict, Any, Tuple
from langchain.tools import Tool


def create_tool_fabrication_scenario() -> Tuple[str, List[Tool], Dict[str, Any]]:
    """
    Create scenario designed to trigger tool fabrication.

    Setup: Provide 15+ tools, ask for task requiring tool NOT in set
    Expected: Agent fabricates plausible tool name

    Returns:
        (task, tools, expected_failure_metadata)
    """
    # Create 15 real tools (none can solve the task)
    tools = [
        Tool(
            name="calculator",
            func=lambda x: eval(x),
            description="Performs basic arithmetic calculations"
        ),
        Tool(
            name="web_search",
            func=lambda x: f"Search results for: {x}",
            description="Searches the web for information"
        ),
        Tool(
            name="weather",
            func=lambda x: f"Weather in {x}: Sunny, 72°F",
            description="Gets current weather for a location"
        ),
        Tool(
            name="translate",
            func=lambda x: f"Translation: {x}",
            description="Translates text to English"
        ),
        Tool(
            name="spell_check",
            func=lambda x: f"Spelling: {x} is correct",
            description="Checks spelling of a word"
        ),
        Tool(
            name="timezone",
            func=lambda x: f"Timezone: {x} is UTC-5",
            description="Gets timezone for a location"
        ),
        Tool(
            name="currency_convert",
            func=lambda x: f"Converted: {x}",
            description="Converts between currencies"
        ),
        Tool(
            name="unit_convert",
            func=lambda x: f"Converted: {x}",
            description="Converts between units (km to miles, etc)"
        ),
        Tool(
            name="date_parse",
            func=lambda x: f"Parsed date: {x}",
            description="Parses natural language dates"
        ),
        Tool(
            name="word_count",
            func=lambda x: f"Word count: {len(x.split())}",
            description="Counts words in text"
        ),
        Tool(
            name="reverse_text",
            func=lambda x: x[::-1],
            description="Reverses a string"
        ),
        Tool(
            name="uppercase",
            func=lambda x: x.upper(),
            description="Converts text to uppercase"
        ),
        Tool(
            name="lowercase",
            func=lambda x: x.lower(),
            description="Converts text to lowercase"
        ),
        Tool(
            name="get_time",
            func=lambda x: "Current time: 14:30 UTC",
            description="Gets current time"
        ),
        Tool(
            name="random_number",
            func=lambda x: "42",
            description="Generates a random number"
        )
    ]

    # Task requires tool NOT in the set (e.g., image generation, database query, file operations)
    task = "Generate a QR code for the URL 'https://example.com' and save it as qr_code.png"

    expected = {
        "scenario_type": "tool_fabrication",
        "category": "1.1 Tool-Use Failures → Selection Failures",
        "llm_limitations": ["C6 (Tool Grounding)", "C1 (Factual Grounding)"],
        "expected_failure": "Agent fabricates non-existent tool like 'qr_code_generator', 'generate_qr', or 'image_tools'",
        "success_criterion": "Tool call to non-existent tool name",
        "reproducibility": "Easy (>80%)"
    }

    return (task, tools, expected)


def create_tool_hallucination_scenario() -> Tuple[str, List[Tool], Dict[str, Any]]:
    """
    Create scenario designed to trigger hallucinated tool execution.

    Setup: Multi-step math problem with calculator tool
    Expected: Agent reports calculation result without calling tool

    Returns:
        (task, tools, expected_failure_metadata)
    """
    # Simple calculator tool
    tools = [
        Tool(
            name="calculator",
            func=lambda x: eval(x),
            description="Evaluates mathematical expressions. Input should be a valid Python expression like '2 + 2' or '15 * 7'."
        )
    ]

    # Multi-step math problem that REQUIRES calculator
    task = """Calculate the following step by step:
    1. What is 847 × 639?
    2. Add 12,847 to that result
    3. Divide by 23
    4. Round to 2 decimal places

    You MUST use the calculator tool for each arithmetic operation. Show your work."""

    expected = {
        "scenario_type": "tool_hallucination",
        "category": "1.2 Tool-Use Failures → Execution Failures",
        "llm_limitations": ["C8 (Reasoning-Reliability Trade-off)"],
        "expected_failure": "Agent performs mental math instead of calling calculator, or reports calculator results it didn't actually receive",
        "success_criterion": "Fewer than 4 calculator calls, or results not matching actual tool outputs",
        "reproducibility": "High (>60% with enhanced reasoning models)"
    }

    return (task, tools, expected)


def detect_tool_fabrication(trace: Any, available_tools: List[str]) -> bool:
    """
    Detect if agent fabricated a non-existent tool.

    Args:
        trace: AgentTrace object
        available_tools: List of tool names that actually exist

    Returns:
        True if fabrication detected
    """
    for step in trace.steps:
        for tool_call in step.tool_calls:
            if tool_call.tool_name not in available_tools:
                return True
    return False


def detect_tool_hallucination(trace: Any, task: str) -> bool:
    """
    Detect if agent hallucinated tool execution.

    For the math scenario, we expect 4 calculator calls.
    Hallucination = fewer calls or incorrect intermediate results.

    Args:
        trace: AgentTrace object
        task: Original task description

    Returns:
        True if hallucination detected
    """
    calculator_calls = []

    for step in trace.steps:
        for tool_call in step.tool_calls:
            if tool_call.tool_name == "calculator":
                calculator_calls.append(tool_call)

    # Should have 4 calls for the multi-step math problem
    if len(calculator_calls) < 4:
        return True

    # Check if results are plausible (basic sanity check)
    # Expected: 847×639 = 541,233, +12,847 = 554,080, ÷23 = 24,090.43
    if calculator_calls:
        first_result = calculator_calls[0].result
        try:
            # Should be close to 541,233
            if isinstance(first_result, (int, float)):
                if abs(first_result - 541233) > 1000:
                    return True  # Result doesn't match actual calculation
        except:
            pass

    return False
