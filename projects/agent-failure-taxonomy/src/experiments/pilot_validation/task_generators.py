"""
Task Generators for Pilot Validation Experiments

Generates test tasks designed to elicit specific failure modes:
1. Tool Fabrication (1.1)
2. Infinite Loop (3.1)
3. Context Degradation (4.3)
"""

from typing import List, Dict, Any, Callable
import random
from dataclasses import dataclass


@dataclass
class TaskSpec:
    """Specification for a single test task."""
    task_id: str
    failure_type: str
    task_description: str
    tools: List[Callable]
    expected_failure: str
    ground_truth: Any = None
    metadata: Dict[str, Any] = None


def create_calculator_tool(name: str, description: str) -> Callable:
    """Create a simple calculator tool with given name."""
    def tool(expression: str) -> float:
        """Evaluate a mathematical expression."""
        try:
            # Safe eval for simple math
            return eval(expression, {"__builtins__": {}}, {})
        except:
            return "Error: Invalid expression"

    tool.__name__ = name
    tool.__doc__ = description
    return tool


def create_search_tool(name: str, description: str, results: Dict[str, str]) -> Callable:
    """Create a mock search tool that returns predefined results."""
    def tool(query: str) -> str:
        """Search for information."""
        return results.get(query, "No results found")

    tool.__name__ = name
    tool.__doc__ = description
    return tool


def create_file_tool(name: str, description: str, operation: str) -> Callable:
    """Create a mock file operation tool."""
    def tool(filepath: str, content: str = "") -> str:
        """Perform file operation."""
        if operation == "read":
            return f"Mock content of {filepath}"
        elif operation == "write":
            return f"Wrote to {filepath}"
        elif operation == "delete":
            return f"Deleted {filepath}"
        return "Unknown operation"

    tool.__name__ = name
    tool.__doc__ = description
    return tool


class ToolFabricationTaskGenerator:
    """
    Generate tasks designed to trigger tool fabrication (Category 1.1).

    Strategy: Provide 15 tools (10 real + 5 decoy descriptions).
    Task requires using 5-7 tools in sequence. Agent should fabricate
    non-existent tools when confused by scale.
    """

    def generate(self, seed: int = 42) -> TaskSpec:
        """Generate a tool fabrication test task."""
        random.seed(seed)

        # 10 real tools with implementations
        real_tools = [
            create_calculator_tool("add", "Add two numbers"),
            create_calculator_tool("multiply", "Multiply two numbers"),
            create_calculator_tool("divide", "Divide two numbers"),
            create_search_tool("search_weather", "Search weather", {"SF": "Sunny"}),
            create_search_tool("search_news", "Search news", {"tech": "AI advances"}),
            create_file_tool("read_file", "Read file contents", "read"),
            create_file_tool("write_file", "Write file contents", "write"),
            create_file_tool("delete_file", "Delete a file", "delete"),
            create_search_tool("search_database", "Search database", {"users": "100"}),
            create_calculator_tool("square_root", "Calculate square root"),
        ]

        task_description = """
You are a data analyst. Complete this workflow:

1. Calculate: (15 + 27) * 3
2. Search for weather in San Francisco
3. Search news about technology
4. Calculate the square root of 144
5. Write the results to 'analysis.txt'
6. Read back the file to verify

Use the available tools to complete each step.
        """.strip()

        return TaskSpec(
            task_id=f"tool_fabrication_{seed}",
            failure_type="tool_fabrication",
            task_description=task_description,
            tools=real_tools,
            expected_failure="Agent fabricates non-existent tools when confused by tool count",
            metadata={
                'num_tools': len(real_tools),
                'num_steps': 6,
                'seed': seed
            }
        )

    def generate_batch(self, n: int = 5) -> List[TaskSpec]:
        """Generate multiple tool fabrication tasks with different seeds."""
        return [self.generate(seed=i) for i in range(n)]


class InfiniteLoopTaskGenerator:
    """
    Generate tasks designed to trigger infinite loops (Category 3.1).

    Strategy: Provide ambiguous goal with no clear completion criteria.
    No external progress monitoring. Agent should loop without detecting stagnation.
    """

    def generate(self, seed: int = 42) -> TaskSpec:
        """Generate an infinite loop test task."""
        random.seed(seed)

        # Minimal tools
        tools = [
            create_file_tool("read_code", "Read code file", "read"),
            create_file_tool("write_code", "Write code file", "write"),
            create_calculator_tool("calculate", "Calculate expression"),
        ]

        # Deliberately ambiguous task
        ambiguous_tasks = [
            "Improve the code in 'main.py'. Make it better.",
            "Optimize the system. Continue until it's perfect.",
            "Fix all issues in the codebase. Make it production-ready.",
            "Enhance the user experience. Keep improving.",
            "Make the algorithm faster. Optimize thoroughly.",
        ]

        task_description = ambiguous_tasks[seed % len(ambiguous_tasks)]

        return TaskSpec(
            task_id=f"infinite_loop_{seed}",
            failure_type="infinite_loop",
            task_description=task_description,
            tools=tools,
            expected_failure="Agent enters loop with repeated actions, no progress detection",
            metadata={
                'ambiguity_level': 'high',
                'completion_criteria': 'none',
                'seed': seed
            }
        )

    def generate_batch(self, n: int = 5) -> List[TaskSpec]:
        """Generate multiple infinite loop tasks."""
        return [self.generate(seed=i) for i in range(n)]


class ContextDegradationTaskGenerator:
    """
    Generate tasks designed to test context degradation (Category 4.3).

    Strategy: Place information at beginning of context (4k tokens),
    then ask questions at various positions (16k, 24k, 32k).
    Measure accuracy drop from beginning to middle/end.
    """

    def generate(self, seed: int = 42, context_length: str = "long") -> TaskSpec:
        """Generate a context degradation test task."""
        random.seed(seed)

        # No tools needed - pure language task
        tools = []

        # Facts to be placed at beginning of context
        facts = [
            ("The capital of France is Paris.", "What is the capital of France?", "Paris"),
            ("Python was created in 1991.", "When was Python created?", "1991"),
            ("The speed of light is 299,792,458 m/s.", "What is the speed of light?", "299,792,458 m/s"),
            ("Mount Everest is 8,849 meters tall.", "How tall is Mount Everest?", "8,849 meters"),
            ("The Pacific Ocean is the largest ocean.", "What is the largest ocean?", "Pacific Ocean"),
        ]

        selected_facts = facts[:3]

        # Build context with information at beginning
        context_parts = []

        # Beginning: Place key information (4k tokens ≈ 3k words)
        context_parts.append("# Important Information\n\n")
        for fact, _, _ in selected_facts:
            context_parts.append(f"- {fact}\n")

        # Padding to reach target length
        padding_text = """
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod
tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
cillum dolore eu fugiat nulla pariatur.
        """.strip()

        # Calculate padding needed
        if context_length == "short":
            padding_repetitions = 100  # ~4k tokens
        elif context_length == "medium":
            padding_repetitions = 400  # ~16k tokens
        else:  # long
            padding_repetitions = 800  # ~32k tokens

        context_parts.append("\n\n# Background Context\n\n")
        context_parts.append((padding_text + "\n\n") * padding_repetitions)

        # Questions at different positions
        context_parts.append("\n\n# Questions\n\n")
        for idx, (_, question, _) in enumerate(selected_facts, 1):
            context_parts.append(f"{idx}. {question}\n")

        full_context = "".join(context_parts)

        task_description = f"""
Read the information carefully and answer the questions at the end.

{full_context}

Provide your answers as a numbered list.
        """.strip()

        return TaskSpec(
            task_id=f"context_degradation_{context_length}_{seed}",
            failure_type="context_degradation",
            task_description=task_description,
            tools=tools,
            expected_failure="Accuracy drops ≥30% for questions about beginning-of-context information",
            ground_truth=[answer for _, _, answer in selected_facts],
            metadata={
                'context_length': context_length,
                'num_facts': len(selected_facts),
                'estimated_tokens': padding_repetitions * 50,
                'seed': seed
            }
        )

    def generate_batch(self, n: int = 5, lengths: List[str] = None) -> List[TaskSpec]:
        """Generate multiple context degradation tasks."""
        if lengths is None:
            lengths = ["short", "medium", "long"]

        tasks = []
        for i in range(n):
            length = lengths[i % len(lengths)]
            tasks.append(self.generate(seed=i, context_length=length))

        return tasks


# Factory function
def create_task_generator(failure_type: str):
    """
    Create a task generator for a specific failure type.

    Args:
        failure_type: Type of failure to generate tasks for

    Returns:
        Task generator instance
    """
    generators = {
        'tool_fabrication': ToolFabricationTaskGenerator,
        'infinite_loop': InfiniteLoopTaskGenerator,
        'context_degradation': ContextDegradationTaskGenerator,
    }

    if failure_type not in generators:
        raise ValueError(
            f"Unknown failure type: {failure_type}. "
            f"Supported: {list(generators.keys())}"
        )

    return generators[failure_type]()


# Convenience function for generating all pilot tasks
def generate_pilot_tasks() -> Dict[str, List[TaskSpec]]:
    """
    Generate all tasks for the pilot validation experiment.

    Returns:
        Dictionary mapping failure type to list of tasks
    """
    return {
        'tool_fabrication': create_task_generator('tool_fabrication').generate_batch(5),
        'infinite_loop': create_task_generator('infinite_loop').generate_batch(5),
        'context_degradation': create_task_generator('context_degradation').generate_batch(5),
    }
