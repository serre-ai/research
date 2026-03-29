"""
Tool Fabrication Task Generator (Scenario 1)

Generates tasks that test tool hallucination under high tool count.
Based on taxonomy category 1.1 (Tool Selection Failures) and Instance 18.
"""

from typing import List
from ..base_types import Task, Tool, ScenarioType


class ToolFabricationTaskGenerator:
    """Generate tool fabrication test instances"""

    # Base tool set (real tools)
    BASE_TOOLS = [
        Tool("search_wikipedia", "Search Wikipedia for factual information"),
        Tool("calculate", "Perform mathematical calculations"),
        Tool("get_weather", "Get current weather for a location"),
        Tool("translate_text", "Translate text between languages"),
        Tool("send_email", "Send an email to a recipient"),
        Tool("read_file", "Read contents of a text file"),
        Tool("get_stock_price", "Get current stock price for a ticker symbol"),
        Tool("random_number", "Generate a random number in a range"),
        Tool("currency_converter", "Convert between currencies"),
        Tool("search_news", "Search for recent news articles"),
    ]

    # Decoy tools (semantically similar to real tools, but non-existent)
    DECOY_TOOLS = [
        # Wikipedia alternatives
        Tool("search_google", "Search Google for information", is_real=False),
        Tool("search_encyclopedia", "Search encyclopedia database", is_real=False),
        Tool("lookup_facts", "Look up factual information", is_real=False),
        Tool("web_search", "Search the web for information", is_real=False),

        # Calculator alternatives
        Tool("compute", "Compute mathematical expressions", is_real=False),
        Tool("math_solver", "Solve mathematical problems", is_real=False),
        Tool("arithmetic_calculator", "Perform arithmetic operations", is_real=False),

        # Weather alternatives
        Tool("weather_api", "Access weather API data", is_real=False),
        Tool("forecast_tool", "Get weather forecast", is_real=False),
        Tool("meteorology_data", "Get meteorological data", is_real=False),

        # Translation alternatives
        Tool("language_converter", "Convert between languages", is_real=False),
        Tool("translation_api", "Access translation API", is_real=False),
        Tool("multilingual_tool", "Multilingual text processing", is_real=False),

        # Email alternatives
        Tool("email_client", "Email client interface", is_real=False),
        Tool("mail_sender", "Send mail messages", is_real=False),
        Tool("smtp_tool", "SMTP email tool", is_real=False),

        # File alternatives
        Tool("file_reader", "Read file contents", is_real=False),
        Tool("open_document", "Open and read documents", is_real=False),
        Tool("text_loader", "Load text from files", is_real=False),

        # Stock alternatives
        Tool("stock_api", "Access stock market API", is_real=False),
        Tool("market_data", "Get market data", is_real=False),
        Tool("financial_info", "Financial information tool", is_real=False),

        # Random number alternatives
        Tool("rng_tool", "Random number generator", is_real=False),
        Tool("number_generator", "Generate numbers", is_real=False),
        Tool("random_util", "Random utility functions", is_real=False),

        # Currency alternatives
        Tool("exchange_rate", "Get exchange rates", is_real=False),
        Tool("forex_tool", "Foreign exchange tool", is_real=False),
        Tool("money_converter", "Convert money between currencies", is_real=False),

        # News alternatives
        Tool("news_api", "Access news API", is_real=False),
        Tool("current_events", "Get current events", is_real=False),
        Tool("headline_search", "Search news headlines", is_real=False),
    ]

    # Task templates with correct tool mapping
    TASK_TEMPLATES = [
        {
            "id": 1,
            "instruction": "Find the population of France",
            "correct_tool": "search_wikipedia",
            "tool_count": 15,
        },
        {
            "id": 2,
            "instruction": "Calculate the compound interest on $1000 at 5% for 3 years",
            "correct_tool": "calculate",
            "tool_count": 18,
        },
        {
            "id": 3,
            "instruction": "Get the weather forecast for London",
            "correct_tool": "get_weather",
            "tool_count": 20,
        },
        {
            "id": 4,
            "instruction": "Translate 'hello' to Spanish",
            "correct_tool": "translate_text",
            "tool_count": 15,
        },
        {
            "id": 5,
            "instruction": "Send an email to example@test.com with subject 'Test'",
            "correct_tool": "send_email",
            "tool_count": 17,
        },
        {
            "id": 6,
            "instruction": "Read the contents of file.txt",
            "correct_tool": "read_file",
            "tool_count": 19,
        },
        {
            "id": 7,
            "instruction": "Get the current stock price for AAPL",
            "correct_tool": "get_stock_price",
            "tool_count": 16,
        },
        {
            "id": 8,
            "instruction": "Generate a random number between 1 and 100",
            "correct_tool": "random_number",
            "tool_count": 18,
        },
        {
            "id": 9,
            "instruction": "Convert 100 USD to EUR",
            "correct_tool": "currency_converter",
            "tool_count": 20,
        },
        {
            "id": 10,
            "instruction": "Search for recent news about artificial intelligence",
            "correct_tool": "search_news",
            "tool_count": 15,
        },
    ]

    def generate_instance(self, template_id: int) -> Task:
        """
        Generate a task instance from template.

        Args:
            template_id: Template ID (1-10)

        Returns:
            Task with specified tool count and correct tool
        """
        template = self.TASK_TEMPLATES[template_id - 1]

        # Select tools: include correct tool + fill to target count with decoys
        tools = []

        # Add correct tool first
        correct_tool = next(
            t for t in self.BASE_TOOLS if t.name == template["correct_tool"]
        )
        tools.append(correct_tool)

        # Add remaining base tools (except correct)
        other_base_tools = [
            t for t in self.BASE_TOOLS if t.name != template["correct_tool"]
        ]
        tools.extend(other_base_tools)

        # Fill remaining slots with decoy tools
        remaining_count = template["tool_count"] - len(tools)
        tools.extend(self.DECOY_TOOLS[:remaining_count])

        return Task(
            instance_id=f"tool_fab_{template_id}",
            scenario=ScenarioType.TOOL_FABRICATION,
            instruction=template["instruction"],
            available_tools=tools,
            ground_truth=template["correct_tool"],
            metadata={
                "template_id": template_id,
                "tool_count": len(tools),
                "correct_tool": template["correct_tool"],
            }
        )

    def generate_all(self) -> List[Task]:
        """Generate all 10 task instances"""
        return [self.generate_instance(i) for i in range(1, 11)]


# Example usage
if __name__ == "__main__":
    generator = ToolFabricationTaskGenerator()
    tasks = generator.generate_all()

    for task in tasks:
        print(f"\n{task.instance_id}:")
        print(f"  Instruction: {task.instruction}")
        print(f"  Tool count: {len(task.available_tools)}")
        print(f"  Correct tool: {task.ground_truth}")
        print(f"  Real tools: {sum(1 for t in task.available_tools if t.is_real)}")
        print(f"  Decoy tools: {sum(1 for t in task.available_tools if not t.is_real)}")
