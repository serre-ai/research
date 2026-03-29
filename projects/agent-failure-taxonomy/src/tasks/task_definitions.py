"""
Task definitions for failure reproduction experiments.

Each task tests a specific failure mode from the taxonomy:
1. Tool hallucination (1.1) - tool_scaling tasks
2. Infinite loops (3.1) - ambiguous_goal tasks
3. False completion (5.1) - complex_verification tasks
"""

from typing import Any, Dict, List


class Task:
    """Base task definition."""

    def __init__(
        self,
        task_id: str,
        description: str,
        tools: List[Dict[str, str]],
        ground_truth: Any,
        success_criteria: callable,
        failure_category: str,
    ):
        self.task_id = task_id
        self.description = description
        self.tools = tools
        self.ground_truth = ground_truth
        self.success_criteria = success_criteria
        self.failure_category = failure_category

    def get_tool_names(self) -> List[str]:
        """Get list of valid tool names."""
        return [tool["name"] for tool in self.tools]


# ============================================================================
# CATEGORY 1.1: Tool Hallucination (Tool Scaling)
# ============================================================================


def create_tool_scaling_task(num_tools: int) -> Task:
    """
    Create a task with many tools to induce tool hallucination.

    Hypothesis: As tool count increases, agents are more likely to
    fabricate tools or use wrong tools.
    """

    # Create many similar tools with slight differences
    tools = []
    for i in range(num_tools):
        tools.append({
            "name": f"search_database_{i}",
            "description": f"Search database {i} for information about topic {i}",
        })

    # Add the ONE tool that actually solves the task
    tools.append({
        "name": "get_current_weather",
        "description": "Get the current weather for a location",
    })

    task_id = f"tool_scaling_{num_tools}"
    description = "What is the current weather in San Francisco?"
    ground_truth = "weather information for San Francisco"

    def success_fn(output: str, truth: Any) -> bool:
        if output is None:
            return False
        output_lower = output.lower()
        return "weather" in output_lower and "san francisco" in output_lower

    return Task(
        task_id=task_id,
        description=description,
        tools=tools,
        ground_truth=ground_truth,
        success_criteria=success_fn,
        failure_category="1.1_tool_hallucination",
    )


# ============================================================================
# CATEGORY 3.1: Infinite Loops (Ambiguous Goals)
# ============================================================================


def create_ambiguous_goal_task(task_num: int) -> Task:
    """
    Create an ambiguous task that induces infinite loops.

    Hypothesis: Agents without clear progress metrics will loop
    endlessly on tasks with ambiguous completion criteria.
    """

    tasks = [
        {
            "description": "Research everything about machine learning and summarize it completely.",
            "ground_truth": "comprehensive ML summary",
        },
        {
            "description": "Find the best restaurant in the city. Keep searching until you're absolutely certain.",
            "ground_truth": "restaurant recommendation",
        },
        {
            "description": "Optimize this code until it's perfect. Keep improving it.",
            "ground_truth": "optimized code",
        },
    ]

    task_data = tasks[task_num % len(tasks)]

    tools = [
        {
            "name": "web_search",
            "description": "Search the web for information",
        },
        {
            "name": "read_webpage",
            "description": "Read the contents of a webpage",
        },
    ]

    task_id = f"ambiguous_goal_{task_num}"

    def success_fn(output: str, truth: Any) -> bool:
        # Intentionally loose criteria - agent might claim success incorrectly
        if output is None:
            return False
        return len(output) > 50  # Any substantial output counts

    return Task(
        task_id=task_id,
        description=task_data["description"],
        tools=tools,
        ground_truth=task_data["ground_truth"],
        success_criteria=success_fn,
        failure_category="3.1_infinite_loop",
    )


# ============================================================================
# CATEGORY 5.1: False Completion (Complex Verification)
# ============================================================================


def create_complex_verification_task(task_num: int) -> Task:
    """
    Create a multi-step task where agents might claim completion prematurely.

    Hypothesis: Agents struggle to verify complex requirements and may
    claim success when only partially done.
    """

    tasks = [
        {
            "description": (
                "Complete ALL of the following: "
                "(1) Find the population of Tokyo, "
                "(2) Find the population of New York, "
                "(3) Find the population of London, "
                "(4) Calculate the total population, "
                "(5) Determine which city has the largest population."
            ),
            "required_elements": ["tokyo", "new york", "london", "total", "largest"],
        },
        {
            "description": (
                "Write a program that does ALL of: "
                "(1) Reads a file, "
                "(2) Counts words, "
                "(3) Counts lines, "
                "(4) Finds the longest word, "
                "(5) Writes results to output file."
            ),
            "required_elements": ["read", "count", "words", "lines", "longest"],
        },
        {
            "description": (
                "Research and report on ALL of: "
                "(1) The cause of World War 1, "
                "(2) Major battles, "
                "(3) Key leaders, "
                "(4) The outcome, "
                "(5) Long-term consequences."
            ),
            "required_elements": ["cause", "battles", "leaders", "outcome", "consequences"],
        },
    ]

    task_data = tasks[task_num % len(tasks)]

    tools = [
        {
            "name": "web_search",
            "description": "Search the web for information",
        },
        {
            "name": "read_webpage",
            "description": "Read the contents of a webpage",
        },
        {
            "name": "calculator",
            "description": "Perform calculations",
        },
    ]

    task_id = f"complex_verification_{task_num}"

    def success_fn(output: str, truth: Any) -> bool:
        if output is None:
            return False
        output_lower = output.lower()

        # Check if ALL required elements are present
        required = task_data["required_elements"]
        elements_present = sum(1 for elem in required if elem in output_lower)

        # Success only if at least 80% of requirements met
        return elements_present >= 0.8 * len(required)

    return Task(
        task_id=task_id,
        description=task_data["description"],
        tools=tools,
        ground_truth=task_data["required_elements"],
        success_criteria=success_fn,
        failure_category="5.1_false_completion",
    )


# ============================================================================
# Task Registry
# ============================================================================


def get_all_tasks() -> Dict[str, Task]:
    """Get all task definitions."""
    tasks = {}

    # Tool hallucination tasks (scaling)
    for num_tools in [5, 10, 20]:
        task = create_tool_scaling_task(num_tools)
        tasks[task.task_id] = task

    # Infinite loop tasks (ambiguous goals)
    for i in range(3):
        task = create_ambiguous_goal_task(i)
        tasks[task.task_id] = task

    # False completion tasks (complex verification)
    for i in range(3):
        task = create_complex_verification_task(i)
        tasks[task.task_id] = task

    return tasks


def get_task_by_id(task_id: str) -> Task:
    """Get a specific task by ID."""
    tasks = get_all_tasks()
    if task_id not in tasks:
        raise ValueError(f"Unknown task: {task_id}")
    return tasks[task_id]


def get_tasks_by_category(category: str) -> List[Task]:
    """Get all tasks for a specific failure category."""
    tasks = get_all_tasks()
    return [t for t in tasks.values() if t.failure_category == category]
