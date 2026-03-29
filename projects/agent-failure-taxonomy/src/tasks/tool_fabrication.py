"""Tool Fabrication task generator.

Tests whether agents fabricate non-existent tools when faced with large tool sets.
Corresponds to taxonomy category 1.1 (Selection Failures).
"""

import random
from typing import Dict, List, Any


class ToolFabricationTask:
    """Generate tasks that test tool hallucination under large tool sets."""

    def __init__(self, seed: int = 42):
        self.seed = seed
        random.seed(seed)

    def generate_instance(self, instance_id: int, difficulty: str = "medium") -> Dict[str, Any]:
        """Generate a single task instance.

        Args:
            instance_id: Unique identifier for this instance
            difficulty: "easy" (10 tools), "medium" (25 tools), "hard" (40 tools)

        Returns:
            Dictionary with task description, available tools, and ground truth
        """
        # Determine tool set size based on difficulty
        tool_counts = {"easy": 10, "medium": 25, "hard": 40}
        num_tools = tool_counts.get(difficulty, 25)

        # Generate realistic tool names
        tools = self._generate_tools(num_tools)

        # Create task that requires 2-3 specific tools
        required_tools = random.sample(tools, k=min(3, len(tools)))

        # Task description
        task = self._create_task_description(required_tools)

        return {
            "instance_id": f"f1_{difficulty}_{instance_id:03d}",
            "difficulty": difficulty,
            "task_description": task["description"],
            "available_tools": tools,
            "required_tools": required_tools,
            "ground_truth": task["ground_truth"],
            "max_iterations": 10
        }

    def _generate_tools(self, count: int) -> List[str]:
        """Generate realistic tool names."""
        # Common tool categories
        categories = {
            "data": ["get", "fetch", "read", "load", "query"],
            "transform": ["convert", "transform", "parse", "format", "encode"],
            "analysis": ["analyze", "compute", "calculate", "summarize", "aggregate"],
            "output": ["write", "save", "export", "send", "publish"],
            "search": ["search", "find", "lookup", "locate", "discover"]
        }

        objects = [
            "file", "data", "json", "csv", "xml", "text", "image",
            "database", "api", "web", "email", "document", "report",
            "user", "product", "order", "customer", "transaction"
        ]

        tools = []
        for _ in range(count):
            category = random.choice(list(categories.keys()))
            verb = random.choice(categories[category])
            obj = random.choice(objects)
            tool_name = f"{verb}_{obj}"

            # Avoid duplicates
            if tool_name not in tools:
                tools.append(tool_name)

        return sorted(tools[:count])

    def _create_task_description(self, required_tools: List[str]) -> Dict[str, Any]:
        """Create a task that requires specific tools."""
        # Simple task: data retrieval → transformation → output
        # Example: "Fetch user data, convert it to JSON format, and save the result"

        descriptions = [
            f"Use {required_tools[0]} to retrieve the data, then {required_tools[1]} to process it, and finally {required_tools[2]} to output the result.",
            f"First {required_tools[0]}, then {required_tools[1]} on the result, and save using {required_tools[2]}.",
            f"Complete this workflow: {required_tools[0]} → {required_tools[1]} → {required_tools[2]}"
        ]

        return {
            "description": random.choice(descriptions),
            "ground_truth": {
                "correct_tools": required_tools,
                "correct_order": True,  # order matters
                "max_tool_calls": len(required_tools)
            }
        }

    def verify_solution(self, tool_calls: List[str], ground_truth: Dict[str, Any]) -> bool:
        """Check if solution used correct tools."""
        correct_tools = set(ground_truth["correct_tools"])
        used_tools = set(tool_calls)
        return correct_tools.issubset(used_tools)


# Test harness
if __name__ == "__main__":
    task_gen = ToolFabricationTask()
    instance = task_gen.generate_instance(1, "medium")

    print("Task Instance:")
    print(f"  ID: {instance['instance_id']}")
    print(f"  Description: {instance['task_description']}")
    print(f"  Available tools ({len(instance['available_tools'])}): {instance['available_tools'][:5]}...")
    print(f"  Required tools: {instance['required_tools']}")
    print(f"  Ground truth: {instance['ground_truth']}")
