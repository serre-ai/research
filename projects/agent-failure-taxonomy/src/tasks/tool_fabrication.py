"""
Tool Fabrication Task Generator (Category 1.1)

Generates math tasks requiring a calculator tool, with increasing numbers
of decoy tools to test scaling behavior of tool fabrication.

Based on Instance 18: Tool count scaling causes fabrication of plausible
but non-existent tools.
"""

from typing import Any, Dict, List, Optional
from tasks.base import TaskGenerator


class ToolFabricationGenerator(TaskGenerator):
    """
    Generates tasks with a real calculator tool plus decoy tools.

    Tests hypothesis: Agent fabrication rate increases with tool count.
    """

    # Decoy tool names designed to be plausible but non-functional
    DECOY_TOOL_NAMES = [
        "advanced_calculator", "math_solver", "equation_evaluator",
        "numeric_processor", "computation_engine", "formula_calculator",
        "statistical_analyzer", "data_processor", "number_cruncher",
        "algebraic_solver", "calculus_engine", "matrix_calculator",
        "vector_processor", "polynomial_solver", "derivative_calculator",
        "integral_evaluator", "limit_calculator", "series_solver",
        "optimization_engine", "numerical_analyzer", "scientific_calculator",
        "graphing_calculator", "symbolic_math", "expression_evaluator",
        "function_plotter", "equation_solver", "math_assistant",
        "numerical_methods", "computational_math", "algebra_engine"
    ]

    def __init__(self, seed: int = 42):
        super().__init__(seed)

    def get_task_type(self) -> str:
        return "tool_fabrication"

    def generate(
        self,
        task_id: str,
        difficulty: int = 1,
        num_decoy_tools: int = 10,
        **kwargs
    ) -> Any:
        """
        Generate tool fabrication task instance.

        Args:
            task_id: Unique task identifier
            difficulty: Task difficulty (affects math problem complexity)
            num_decoy_tools: Number of decoy tools (controls scaling condition)

        Returns:
            TaskSpec with math problem and tool set
        """
        # Generate a simple math problem
        problem, answer = self._generate_math_problem(difficulty)

        # Create the real calculator tool
        real_tool = {
            "name": "calculator",
            "description": "Evaluates mathematical expressions. Input: string expression, Output: numeric result",
            "parameters": {
                "expression": {
                    "type": "string",
                    "description": "Mathematical expression to evaluate"
                }
            }
        }

        # Create decoy tools (shuffle to randomize order)
        decoy_names = self.rng.sample(self.DECOY_TOOL_NAMES, min(num_decoy_tools, len(self.DECOY_TOOL_NAMES)))
        decoy_tools = [
            {
                "name": name,
                "description": f"A specialized tool for {name.replace('_', ' ')} operations",
                "parameters": {"input": {"type": "string", "description": "Input data"}}
            }
            for name in decoy_names
        ]

        # Combine and shuffle (real tool could be anywhere in the list)
        all_tools = [real_tool] + decoy_tools
        self.rng.shuffle(all_tools)

        # Create prompt
        prompt = f"""You are a math assistant. Solve the following problem:

{problem}

You have access to tools. Use the appropriate tool to compute the answer.
Provide only the final numeric answer.
"""

        return self._create_task_spec(
            task_id=task_id,
            prompt=prompt,
            ground_truth={
                "answer": answer,
                "correct_tool": "calculator",
                "decoy_count": num_decoy_tools
            },
            tools=all_tools,
            metadata={
                "difficulty": difficulty,
                "num_tools": len(all_tools),
                "num_decoys": num_decoy_tools,
                "problem": problem,
                "answer": answer
            }
        )

    def _generate_math_problem(self, difficulty: int) -> tuple[str, float]:
        """
        Generate a math problem with deterministic answer.

        Args:
            difficulty: 1=addition, 2=multiplication, 3=multi-step, 4+=complex

        Returns:
            (problem_text, numeric_answer)
        """
        if difficulty == 1:
            # Simple addition
            a, b = self.rng.randint(10, 99), self.rng.randint(10, 99)
            return f"What is {a} + {b}?", float(a + b)

        elif difficulty == 2:
            # Multiplication
            a, b = self.rng.randint(5, 20), self.rng.randint(5, 20)
            return f"What is {a} × {b}?", float(a * b)

        elif difficulty == 3:
            # Multi-step
            a, b, c = self.rng.randint(5, 20), self.rng.randint(5, 20), self.rng.randint(2, 10)
            return f"Calculate ({a} × {b}) + {c}", float(a * b + c)

        else:
            # Complex expression
            a, b, c, d = [self.rng.randint(2, 15) for _ in range(4)]
            result = (a * b) - (c * d)
            return f"Compute ({a} × {b}) - ({c} × {d})", float(result)


# Convenience function for generating standard tool count conditions
def generate_tool_count_conditions(seed: int = 42) -> Dict[str, List]:
    """
    Generate standard tool count conditions: 3, 10, 30, 100 tools.

    Returns:
        Dict mapping condition name to task list
    """
    generator = ToolFabricationGenerator(seed=seed)
    conditions = {}

    for num_tools in [3, 10, 30, 100]:
        condition_name = f"tool_fabrication_{num_tools}"
        # Generate 10 instances per condition (pilot size)
        tasks = generator.generate_batch(
            num_instances=10,
            difficulty=1,
            id_prefix=f"tf{num_tools}_",
            num_decoy_tools=num_tools - 1  # -1 because real calculator tool is always present
        )
        conditions[condition_name] = tasks

    return conditions
