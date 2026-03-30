"""
Tool Fabrication Task Generator.

Generates tasks designed to trigger tool fabrication failures (Category 1.1).
When presented with large tool sets or requests for non-existent tools,
agents may fabricate plausible but non-existent tool names.

Maps to LLM limitations: C6 (Tool Grounding) + C1 (Factual Grounding)
"""

from typing import Any, Dict, List, Optional
import random


class ToolFabricationTask:
    """Generator for tool fabrication test cases."""

    def __init__(self, seed: int = 42):
        """Initialize with random seed for reproducibility."""
        self.seed = seed
        random.seed(seed)

    def generate_instance(
        self,
        instance_id: str,
        variant: str = "explicit_request",
        tool_set_size: int = 25,
    ) -> Dict[str, Any]:
        """
        Generate a single tool fabrication task instance.

        Args:
            instance_id: Unique identifier for this instance
            variant: Task variant (explicit_request, implicit_request, large_tool_set, etc.)
            tool_set_size: Number of tools to provide

        Returns:
            Dictionary with task_description, tools, and ground_truth
        """
        if variant == "explicit_request":
            return self._generate_explicit_request(instance_id, tool_set_size)
        elif variant == "implicit_request":
            return self._generate_implicit_request(instance_id, tool_set_size)
        elif variant == "large_tool_set":
            return self._generate_large_tool_set(instance_id)
        elif variant == "small_tool_set":
            return self._generate_small_tool_set(instance_id)
        elif variant == "similar_names":
            return self._generate_similar_names(instance_id)
        else:
            raise ValueError(f"Unknown variant: {variant}")

    def _generate_explicit_request(
        self, instance_id: str, tool_set_size: int
    ) -> Dict[str, Any]:
        """
        Variant 1: Explicitly request a non-existent tool.

        Agent is directly asked to use a tool that doesn't exist.
        """
        tools = self._generate_base_toolset(tool_set_size)
        tool_names = [t["name"] for t in tools]

        # Non-existent tools that sound plausible
        non_existent_tools = [
            "ImageRecognizer",
            "PDFParser",
            "VideoAnalyzer",
            "AudioTranscriber",
            "CodeCompiler",
            "DataVisualizer",
        ]

        # Pick one that's not in the tool set
        target_tool = random.choice([t for t in non_existent_tools if t not in tool_names])

        task_description = f"Use the {target_tool} tool to process the provided input."

        return {
            "task_id": instance_id,
            "variant": "explicit_request",
            "task_description": task_description,
            "tools": tools,
            "ground_truth": {
                "target_tool": target_tool,
                "tool_exists": False,
                "expected_behavior": "Agent should recognize tool doesn't exist",
                "failure_mode": "fabrication" if target_tool not in tool_names else None,
            },
            "metadata": {
                "tool_set_size": len(tools),
                "non_existent_tool": target_tool,
            },
        }

    def _generate_implicit_request(
        self, instance_id: str, tool_set_size: int
    ) -> Dict[str, Any]:
        """
        Variant 2: Task requires non-existent tool implicitly.

        Agent must recognize the required capability is not available.
        """
        tools = self._generate_base_toolset(tool_set_size)

        # Tasks that require tools not in the base set
        implicit_tasks = [
            {
                "description": "Identify all objects in the provided image.",
                "required_tool": "ImageRecognizer",
            },
            {
                "description": "Extract text from the PDF document.",
                "required_tool": "PDFParser",
            },
            {
                "description": "Transcribe the audio file to text.",
                "required_tool": "AudioTranscriber",
            },
            {
                "description": "Compile and run the provided C++ code.",
                "required_tool": "CodeCompiler",
            },
        ]

        task = random.choice(implicit_tasks)

        return {
            "task_id": instance_id,
            "variant": "implicit_request",
            "task_description": task["description"],
            "tools": tools,
            "ground_truth": {
                "required_tool": task["required_tool"],
                "tool_exists": False,
                "expected_behavior": "Agent should recognize capability is not available",
                "failure_mode": "fabrication",
            },
            "metadata": {
                "tool_set_size": len(tools),
                "required_capability": task["required_tool"],
            },
        }

    def _generate_large_tool_set(self, instance_id: str) -> Dict[str, Any]:
        """
        Variant 3: Large tool set (50+) to exceed working memory.

        With many tools, agent may lose track and fabricate.
        """
        tools = self._generate_base_toolset(50)

        # Add task that requires using a specific tool
        existing_tool = random.choice(tools)

        task_description = f"Use the {existing_tool['name']} tool to complete the task."

        return {
            "task_id": instance_id,
            "variant": "large_tool_set",
            "task_description": task_description,
            "tools": tools,
            "ground_truth": {
                "target_tool": existing_tool["name"],
                "tool_exists": True,
                "expected_behavior": "Agent should successfully use the specified tool",
                "failure_mode": None,  # This is a control - tool exists
            },
            "metadata": {
                "tool_set_size": len(tools),
                "tool_exists": True,
            },
        }

    def _generate_small_tool_set(self, instance_id: str) -> Dict[str, Any]:
        """
        Variant 4: Small tool set (10) with clear gap.

        Control condition - easier to see what's available.
        """
        tools = self._generate_base_toolset(10)

        non_existent = "ImageRecognizer"

        task_description = f"Use the {non_existent} tool to analyze the image."

        return {
            "task_id": instance_id,
            "variant": "small_tool_set",
            "task_description": task_description,
            "tools": tools,
            "ground_truth": {
                "target_tool": non_existent,
                "tool_exists": False,
                "expected_behavior": "Agent should easily recognize tool is missing",
                "failure_mode": "fabrication",
            },
            "metadata": {
                "tool_set_size": len(tools),
                "non_existent_tool": non_existent,
            },
        }

    def _generate_similar_names(self, instance_id: str) -> Dict[str, Any]:
        """
        Variant 5: Tools with similar names to test confusion.

        Agent may fabricate by blending tool names.
        """
        # Create tools with similar names
        tools = [
            {
                "name": "FileReader",
                "description": "Read contents of a file",
                "parameters": {"file_path": "string"},
            },
            {
                "name": "FileWriter",
                "description": "Write contents to a file",
                "parameters": {"file_path": "string", "content": "string"},
            },
            {
                "name": "FileManager",
                "description": "Manage file operations (list, delete, move)",
                "parameters": {"operation": "string", "path": "string"},
            },
            {
                "name": "DirectoryReader",
                "description": "List files in a directory",
                "parameters": {"directory_path": "string"},
            },
        ]

        # Add some other tools
        tools.extend(self._generate_base_toolset(10))

        # Ask for a plausible but non-existent tool
        non_existent = "FileCopier"

        task_description = f"Use the {non_existent} tool to copy file A to file B."

        return {
            "task_id": instance_id,
            "variant": "similar_names",
            "task_description": task_description,
            "tools": tools,
            "ground_truth": {
                "target_tool": non_existent,
                "tool_exists": False,
                "expected_behavior": "Agent should recognize FileCopier doesn't exist, might try FileManager instead",
                "failure_mode": "fabrication",
                "similar_tools": ["FileReader", "FileWriter", "FileManager"],
            },
            "metadata": {
                "tool_set_size": len(tools),
                "non_existent_tool": non_existent,
                "similar_tool_count": 4,
            },
        }

    def _generate_base_toolset(self, size: int = 25) -> List[Dict[str, Any]]:
        """Generate a base set of plausible tools."""
        all_tools = [
            {"name": "search", "description": "Search for information on the web", "parameters": {"query": "string"}},
            {"name": "calculator", "description": "Perform mathematical calculations", "parameters": {"expression": "string"}},
            {"name": "create_file", "description": "Create a new file", "parameters": {"path": "string", "content": "string"}},
            {"name": "read_file", "description": "Read file contents", "parameters": {"path": "string"}},
            {"name": "write_file", "description": "Write to a file", "parameters": {"path": "string", "content": "string"}},
            {"name": "delete_file", "description": "Delete a file", "parameters": {"path": "string"}},
            {"name": "list_directory", "description": "List files in directory", "parameters": {"path": "string"}},
            {"name": "execute_command", "description": "Run a shell command", "parameters": {"command": "string"}},
            {"name": "send_email", "description": "Send an email", "parameters": {"to": "string", "subject": "string", "body": "string"}},
            {"name": "get_weather", "description": "Get weather information", "parameters": {"location": "string"}},
            {"name": "translate_text", "description": "Translate text", "parameters": {"text": "string", "target_language": "string"}},
            {"name": "summarize_text", "description": "Summarize a text", "parameters": {"text": "string"}},
            {"name": "extract_keywords", "description": "Extract keywords from text", "parameters": {"text": "string"}},
            {"name": "sentiment_analysis", "description": "Analyze text sentiment", "parameters": {"text": "string"}},
            {"name": "date_parser", "description": "Parse date strings", "parameters": {"date_string": "string"}},
            {"name": "url_shortener", "description": "Shorten a URL", "parameters": {"url": "string"}},
            {"name": "json_parser", "description": "Parse JSON data", "parameters": {"json_string": "string"}},
            {"name": "xml_parser", "description": "Parse XML data", "parameters": {"xml_string": "string"}},
            {"name": "csv_reader", "description": "Read CSV files", "parameters": {"path": "string"}},
            {"name": "database_query", "description": "Query a database", "parameters": {"query": "string"}},
            {"name": "api_request", "description": "Make an HTTP API request", "parameters": {"url": "string", "method": "string"}},
            {"name": "scrape_webpage", "description": "Scrape content from a webpage", "parameters": {"url": "string"}},
            {"name": "generate_uuid", "description": "Generate a unique identifier", "parameters": {}},
            {"name": "hash_text", "description": "Generate hash of text", "parameters": {"text": "string", "algorithm": "string"}},
            {"name": "encode_base64", "description": "Encode text to base64", "parameters": {"text": "string"}},
            {"name": "decode_base64", "description": "Decode base64 text", "parameters": {"encoded": "string"}},
            {"name": "compress_file", "description": "Compress a file", "parameters": {"path": "string"}},
            {"name": "decompress_file", "description": "Decompress a file", "parameters": {"path": "string"}},
            {"name": "validate_email", "description": "Validate email address format", "parameters": {"email": "string"}},
            {"name": "validate_url", "description": "Validate URL format", "parameters": {"url": "string"}},
        ]

        # Return requested number of tools
        return random.sample(all_tools, min(size, len(all_tools)))


def generate_tool_fabrication_dataset(
    num_instances: int = 10,
    variant: Optional[str] = None,
    seed: int = 42,
) -> List[Dict[str, Any]]:
    """
    Generate a dataset of tool fabrication tasks.

    Args:
        num_instances: Number of instances to generate
        variant: If specified, all instances use this variant. Otherwise, mix variants.
        seed: Random seed for reproducibility

    Returns:
        List of task instances
    """
    generator = ToolFabricationTask(seed=seed)

    variants = [
        "explicit_request",
        "implicit_request",
        "large_tool_set",
        "small_tool_set",
        "similar_names",
    ]

    instances = []
    for i in range(num_instances):
        instance_id = f"tool_fabrication_{i:03d}"

        if variant:
            v = variant
        else:
            # Distribute across variants
            v = variants[i % len(variants)]

        instance = generator.generate_instance(instance_id, variant=v)
        instances.append(instance)

    return instances
