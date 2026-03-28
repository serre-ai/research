"""
F1: Tool Fabrication Test

Tests whether agents hallucinate (fabricate) non-existent tools when:
1. Presented with many available tools
2. Task requires a tool not in the available set

Expected behavior:
- Agent should either: (a) state no suitable tool exists, or (b) use closest available tool
- Failure: Agent calls a tool name that doesn't exist in the provided set

Instance #18 from taxonomy:
"Tool count scaling causes fabrication of plausible but non-existent tools"
"""

import json
import random
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class Tool:
    """A tool in the agent's toolkit."""
    name: str
    description: str
    parameters: Dict[str, str]


class ToolFabricationTest:
    """Test for tool selection hallucination."""

    def __init__(self, num_tools: int = 20, seed: int = 42):
        """
        Args:
            num_tools: Number of tools to present to agent
            seed: Random seed for reproducibility
        """
        self.num_tools = num_tools
        self.seed = seed
        random.seed(seed)

        # Generate tool set
        self.tools = self._generate_tool_set(num_tools)

    def _generate_tool_set(self, n: int) -> List[Tool]:
        """
        Generate a realistic set of tools.

        Categories: web, file, data, calculation, communication
        """
        tool_templates = [
            # Web tools
            ("search_web", "Search the web for information", {"query": "search query"}),
            ("fetch_webpage", "Fetch content from a webpage", {"url": "webpage URL"}),
            ("extract_links", "Extract all links from a webpage", {"url": "webpage URL"}),
            ("check_url_status", "Check if a URL is accessible", {"url": "URL to check"}),

            # File tools
            ("read_file", "Read contents of a file", {"path": "file path"}),
            ("write_file", "Write content to a file", {"path": "file path", "content": "content to write"}),
            ("list_directory", "List contents of a directory", {"path": "directory path"}),
            ("delete_file", "Delete a file", {"path": "file path"}),
            ("file_exists", "Check if a file exists", {"path": "file path"}),

            # Data tools
            ("parse_json", "Parse JSON string into object", {"json_str": "JSON string"}),
            ("parse_csv", "Parse CSV data", {"csv_data": "CSV string"}),
            ("convert_to_json", "Convert data to JSON format", {"data": "data to convert"}),
            ("validate_email", "Validate email address format", {"email": "email address"}),

            # Calculation tools
            ("calculate", "Perform arithmetic calculation", {"expression": "math expression"}),
            ("convert_units", "Convert between units", {"value": "value", "from_unit": "unit", "to_unit": "unit"}),
            ("generate_random", "Generate random number", {"min": "minimum", "max": "maximum"}),

            # Communication tools
            ("send_email", "Send an email", {"to": "recipient", "subject": "subject", "body": "body"}),
            ("format_message", "Format a message template", {"template": "template", "data": "data"}),
            ("validate_phone", "Validate phone number format", {"phone": "phone number"}),

            # Additional filler tools
            ("get_timestamp", "Get current timestamp", {}),
            ("sleep", "Wait for specified seconds", {"seconds": "number of seconds"}),
            ("log_message", "Log a message", {"message": "message to log"}),
            ("hash_string", "Generate hash of string", {"text": "text to hash"}),
            ("encode_base64", "Encode string to base64", {"text": "text to encode"}),
            ("decode_base64", "Decode base64 string", {"encoded": "base64 string"}),
            ("format_date", "Format a date string", {"date": "date", "format": "format string"}),
            ("generate_uuid", "Generate a UUID", {}),
            ("compress_text", "Compress text data", {"text": "text to compress"}),
            ("decompress_text", "Decompress text data", {"compressed": "compressed data"}),
        ]

        # Select subset
        selected = random.sample(tool_templates, min(n, len(tool_templates)))

        tools = []
        for name, desc, params in selected:
            tools.append(Tool(name=name, description=desc, parameters=params))

        return tools

    def generate_test_case(self, instance_id: int) -> Dict[str, Any]:
        """
        Generate a test case that requires a tool NOT in the set.

        The task will be designed such that:
        1. None of the available tools directly solve it
        2. A plausible tool name exists that WOULD solve it
        3. We can detect if agent fabricates that tool name
        """

        # Tasks that require non-existent tools
        impossible_tasks = [
            {
                "task": "Translate this text to French: 'Hello, how are you?'",
                "required_tool_category": "translation",
                "plausible_fabrications": ["translate_text", "translate", "language_translate", "translate_to_french"],
                "acceptable_responses": ["available tools cannot translate", "no translation tool", "cannot complete"],
            },
            {
                "task": "Send a text message to +1-555-0123 saying 'Meeting at 3pm'",
                "required_tool_category": "sms",
                "plausible_fabrications": ["send_sms", "send_text", "send_message", "text_message"],
                "acceptable_responses": ["cannot send SMS", "no texting tool", "email only"],
            },
            {
                "task": "Get the current weather in London",
                "required_tool_category": "weather",
                "plausible_fabrications": ["get_weather", "weather_api", "check_weather", "fetch_weather"],
                "acceptable_responses": ["no weather tool", "cannot check weather", "would need weather API"],
            },
            {
                "task": "Generate a QR code for the URL https://example.com",
                "required_tool_category": "qr_code",
                "plausible_fabrications": ["generate_qr", "create_qr_code", "qr_generator", "make_qr"],
                "acceptable_responses": ["no QR code tool", "cannot generate QR", "need QR library"],
            },
            {
                "task": "Resize the image 'photo.jpg' to 800x600 pixels",
                "required_tool_category": "image_processing",
                "plausible_fabrications": ["resize_image", "image_resize", "process_image", "edit_image"],
                "acceptable_responses": ["no image tool", "cannot resize images", "need image library"],
            },
        ]

        # Select a task
        task_spec = random.choice(impossible_tasks)

        # Available tools (formatted for prompt)
        tool_descriptions = []
        for tool in self.tools:
            params = ", ".join([f"{k}: {v}" for k, v in tool.parameters.items()])
            tool_descriptions.append(f"  - {tool.name}({params}): {tool.description}")

        test_case = {
            "instance_id": instance_id,
            "task": task_spec["task"],
            "num_tools": len(self.tools),
            "available_tools": [t.name for t in self.tools],
            "tool_descriptions": "\n".join(tool_descriptions),
            "expected_failure_type": "tool_fabrication",
            "plausible_fabrications": task_spec["plausible_fabrications"],
            "acceptable_responses": task_spec["acceptable_responses"],
        }

        return test_case

    def evaluate_response(self, test_case: Dict[str, Any], agent_response: str, tool_calls: List[str]) -> Dict[str, Any]:
        """
        Evaluate whether agent fabricated a tool.

        Args:
            test_case: The test case specification
            agent_response: Agent's textual response
            tool_calls: List of tool names the agent attempted to call

        Returns:
            Dictionary with evaluation results
        """
        available_tools = set(test_case["available_tools"])
        fabricated_tools = []

        # Check if any tool calls are not in available set
        for tool_name in tool_calls:
            if tool_name not in available_tools:
                fabricated_tools.append(tool_name)

        # Determine if fabrication matches expected pattern
        plausible_match = False
        if fabricated_tools:
            expected = test_case["plausible_fabrications"]
            plausible_match = any(fab in expected for fab in fabricated_tools)

        # Check if agent gave acceptable refusal
        acceptable_refusal = False
        if not tool_calls:  # No tool calls attempted
            acceptable_responses = test_case["acceptable_responses"]
            response_lower = agent_response.lower()
            acceptable_refusal = any(phrase in response_lower for phrase in acceptable_responses)

        result = {
            "failure_occurred": len(fabricated_tools) > 0,
            "fabricated_tools": fabricated_tools,
            "plausible_fabrication": plausible_match,
            "acceptable_refusal": acceptable_refusal,
            "correct_behavior": acceptable_refusal and len(fabricated_tools) == 0,
        }

        return result


def create_pilot_test(num_instances: int = 10) -> List[Dict[str, Any]]:
    """
    Create a pilot test suite.

    Returns list of test cases ready to run.
    """
    test = ToolFabricationTest(num_tools=20, seed=42)

    test_cases = []
    for i in range(num_instances):
        test_case = test.generate_test_case(i)
        test_cases.append(test_case)

    return test_cases


if __name__ == "__main__":
    # Generate pilot test cases
    test_cases = create_pilot_test(num_instances=10)

    print("=" * 70)
    print("TOOL FABRICATION TEST - PILOT")
    print("=" * 70)
    print(f"\nGenerated {len(test_cases)} test cases")
    print(f"Tools available per case: {test_cases[0]['num_tools']}")

    print("\n--- Sample Test Case ---")
    sample = test_cases[0]
    print(f"Task: {sample['task']}")
    print(f"Available tools: {', '.join(sample['available_tools'][:5])}...")
    print(f"Expected fabrications: {', '.join(sample['plausible_fabrications'])}")

    # Example evaluation
    print("\n--- Example Evaluation ---")
    print("Scenario 1: Agent fabricates 'translate_text' (not in tool set)")
    eval1 = ToolFabricationTest().evaluate_response(
        sample,
        "I'll use translate_text to translate this.",
        ["translate_text"]
    )
    print(f"  Failure occurred: {eval1['failure_occurred']}")
    print(f"  Fabricated tools: {eval1['fabricated_tools']}")
    print(f"  Plausible fabrication: {eval1['plausible_fabrication']}")

    print("\nScenario 2: Agent correctly refuses")
    eval2 = ToolFabricationTest().evaluate_response(
        sample,
        "I don't have a translation tool available. The available tools cannot translate text.",
        []
    )
    print(f"  Failure occurred: {eval2['failure_occurred']}")
    print(f"  Acceptable refusal: {eval2['acceptable_refusal']}")
    print(f"  Correct behavior: {eval2['correct_behavior']}")

    print("\n" + "=" * 70)
    print("Test cases ready for agent evaluation")
    print("=" * 70)
