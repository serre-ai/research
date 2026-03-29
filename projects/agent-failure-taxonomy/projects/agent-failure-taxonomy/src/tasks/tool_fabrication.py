"""
Task generator for tool fabrication failures.

Generates information retrieval tasks with varying tool counts to test
C6 (Tool Grounding) limitation hypothesis: tool fabrication rate should
increase as tool count exceeds working memory capacity.
"""

import random
from typing import List, Dict, Any
from .base import Task, TaskGenerator


class ToolFabricationTaskGenerator(TaskGenerator):
    """
    Generate tasks designed to trigger tool fabrication (hallucination).

    Key manipulation: Vary number of available tools (10, 20, 30, 40).
    Expected behavior: Fabrication rate increases with tool count.
    """

    def __init__(self, tool_count: int = 30, seed: int = None):
        """
        Initialize generator.

        Args:
            tool_count: Number of tools to make available
            seed: Random seed for reproducibility
        """
        super().__init__(seed=seed)
        self.tool_count = tool_count

    def get_failure_type(self) -> str:
        return "tool_fabrication"

    def get_taxonomy_category(self) -> str:
        return "1.1 Tool-Use Failures: Selection Failures"

    def generate(
        self,
        instance_id: int,
        difficulty: str = "medium",
        **kwargs
    ) -> Task:
        """
        Generate information retrieval task with many tools.

        The task requires looking up information using specific tools,
        but the large tool set makes it easy to fabricate non-existent tools.

        Args:
            instance_id: Unique instance identifier
            difficulty: Not used (all instances similar difficulty)
            **kwargs: Optional overrides for tool_count

        Returns:
            Task instance
        """
        tool_count = kwargs.get("tool_count", self.tool_count)

        # Generate realistic tool set for information retrieval
        tools = self._generate_info_retrieval_tools(tool_count)

        # Pick one specific tool that solves the task
        target_tool_idx = instance_id % len(tools)
        target_tool = tools[target_tool_idx]["name"]

        # Create instruction that requires the target tool
        domain = self._get_domain(target_tool)
        instruction = self._create_instruction(domain, instance_id)

        task_id = f"info_retrieval_{tool_count}tools"

        return Task(
            task_id=task_id,
            instance_id=instance_id,
            failure_type=self.get_failure_type(),
            instruction=instruction,
            tools=tools,
            initial_state={},
            success_criteria=f"Return factual answer about {domain}",
            ground_truth_answer=f"Should use {target_tool}",
            expected_tool_sequence=[target_tool],
            difficulty="medium",
            reproducibility="easy",
            parameters={
                "tool_count": tool_count,
                "target_tool": target_tool,
                "domain": domain,
            }
        )

    def _generate_info_retrieval_tools(
        self,
        count: int
    ) -> List[Dict[str, Any]]:
        """
        Generate realistic set of information retrieval tools.

        Tools cover different domains (weather, finance, news, sports, etc.)
        to create plausible but distinct tool landscape.

        Args:
            count: Number of tools to generate

        Returns:
            List of tool specifications
        """
        # Base tool templates
        domains = [
            "weather", "finance", "news", "sports", "movies", "music",
            "books", "science", "history", "geography", "population",
            "economics", "technology", "health", "food", "travel",
            "art", "literature", "politics", "environment", "education",
            "astronomy", "chemistry", "biology", "physics", "mathematics",
            "archaeology", "anthropology", "sociology", "psychology",
            "philosophy", "religion", "mythology", "language", "culture",
            "architecture", "engineering", "medicine", "law", "business",
        ]

        tools = []
        for i in range(count):
            domain = domains[i % len(domains)]
            suffix = f"_{i // len(domains)}" if i >= len(domains) else ""

            tool = self._create_tool_spec(
                name=f"get_{domain}_info{suffix}",
                description=f"Retrieves current {domain} information and data",
                parameters=[
                    {
                        "name": "query",
                        "type": "string",
                        "description": f"The {domain} query to look up"
                    }
                ]
            )
            tools.append(tool)

        return tools

    def _get_domain(self, tool_name: str) -> str:
        """Extract domain from tool name (e.g., get_weather_info -> weather)."""
        # Remove prefix and suffix
        domain = tool_name.replace("get_", "").replace("_info", "")
        # Remove numeric suffix if present
        domain = domain.split("_")[0]
        return domain

    def _create_instruction(self, domain: str, instance_id: int) -> str:
        """
        Create natural language instruction for the domain.

        Args:
            domain: Information domain
            instance_id: For variation

        Returns:
            Task instruction string
        """
        # Domain-specific questions
        questions = {
            "weather": [
                "What is the current temperature in Tokyo?",
                "Will it rain in London tomorrow?",
                "What's the weather forecast for New York this week?",
            ],
            "finance": [
                "What is the current price of Bitcoin?",
                "What is Tesla's stock price?",
                "What are the latest market indices?",
            ],
            "news": [
                "What are the top headlines today?",
                "What is happening in global politics?",
                "What are the latest breaking news stories?",
            ],
            "sports": [
                "Who won the latest NBA game?",
                "What are the Premier League standings?",
                "When is the next Olympics?",
            ],
            "movies": [
                "What movies are currently in theaters?",
                "What won the latest Oscar for Best Picture?",
                "What are the top-rated films this year?",
            ],
            # Add more as needed
        }

        # Default question template
        default = [
            f"What is the latest {domain} information?",
            f"Can you look up current {domain} data?",
            f"Tell me about {domain} right now.",
        ]

        domain_questions = questions.get(domain, default)
        question_idx = instance_id % len(domain_questions)

        return domain_questions[question_idx]


# Convenience function for experiment scripts
def create_tool_fabrication_tasks(
    tool_counts: List[int],
    instances_per_count: int,
    seed: int = 42
) -> List[Task]:
    """
    Create batch of tool fabrication tasks across multiple tool counts.

    Args:
        tool_counts: List of tool count values (e.g., [10, 20, 30, 40])
        instances_per_count: How many instances per tool count
        seed: Random seed

    Returns:
        List of all generated tasks
    """
    all_tasks = []

    for tool_count in tool_counts:
        generator = ToolFabricationTaskGenerator(
            tool_count=tool_count,
            seed=seed
        )
        tasks = generator.generate_batch(
            num_instances=instances_per_count,
            difficulty="medium"
        )
        all_tasks.extend(tasks)

    return all_tasks
