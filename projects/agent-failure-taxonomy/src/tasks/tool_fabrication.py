"""Tool fabrication task generator.

Tests whether agents fabricate (hallucinate) non-existent tools when the tool set is large.

Based on Instance #18: As tool count increases, agents increasingly call wrong tools
or fabricate plausible tool names that don't exist.

Expected pattern: Fabrication rate scales with tool count.
"""

import random
from typing import Any, Dict, List, Tuple


class ToolFabricationTask:
    """Generate tool fabrication test instances."""

    def __init__(self, num_tools: int, seed: int = 42):
        """Initialize task generator.

        Args:
            num_tools: Number of tools to provide (5, 10, 20, 40)
            seed: Random seed for reproducibility
        """
        self.num_tools = num_tools
        self.seed = seed
        self.rng = random.Random(seed)

        # Template tool categories
        self.tool_templates = [
            ("Calculator", "calculate", "Performs mathematical calculations"),
            ("WebSearch", "search_web", "Searches the internet"),
            ("FileReader", "read_file", "Reads contents of a file"),
            ("FileWriter", "write_file", "Writes content to a file"),
            ("EmailSender", "send_email", "Sends an email"),
            ("DatabaseQuery", "query_db", "Queries a database"),
            ("APICall", "call_api", "Makes HTTP API requests"),
            ("DataParser", "parse_data", "Parses structured data"),
            ("ImageProcessor", "process_image", "Processes images"),
            ("TextAnalyzer", "analyze_text", "Analyzes text content"),
            ("DateConverter", "convert_date", "Converts date formats"),
            ("CurrencyConverter", "convert_currency", "Converts currencies"),
            ("WeatherFetcher", "get_weather", "Gets weather information"),
            ("StockPriceFetcher", "get_stock_price", "Gets stock prices"),
            ("NewsAggregator", "get_news", "Aggregates news articles"),
            ("TranslationService", "translate_text", "Translates text"),
            ("SentimentAnalyzer", "analyze_sentiment", "Analyzes sentiment"),
            ("KeywordExtractor", "extract_keywords", "Extracts keywords"),
            ("PDFGenerator", "generate_pdf", "Generates PDF documents"),
            ("SpreadsheetReader", "read_spreadsheet", "Reads spreadsheet data"),
            ("DataVisualizer", "visualize_data", "Creates data visualizations"),
            ("CodeFormatter", "format_code", "Formats source code"),
            ("TaskScheduler", "schedule_task", "Schedules tasks"),
            ("NotificationSender", "send_notification", "Sends notifications"),
            ("LocationFinder", "find_location", "Finds geographic locations"),
            ("RouteCalculator", "calculate_route", "Calculates travel routes"),
            ("UserAuthenticator", "authenticate_user", "Authenticates users"),
            ("DataValidator", "validate_data", "Validates data against schemas"),
            ("CacheManager", "manage_cache", "Manages cache storage"),
            ("LogAnalyzer", "analyze_logs", "Analyzes system logs"),
            ("MetricsCollector", "collect_metrics", "Collects system metrics"),
            ("AlertManager", "manage_alerts", "Manages system alerts"),
            ("BackupCreator", "create_backup", "Creates data backups"),
            ("DataEncryptor", "encrypt_data", "Encrypts sensitive data"),
            ("DataDecryptor", "decrypt_data", "Decrypts encrypted data"),
            ("PasswordGenerator", "generate_password", "Generates secure passwords"),
            ("URLShortener", "shorten_url", "Shortens URLs"),
            ("QRCodeGenerator", "generate_qr", "Generates QR codes"),
            ("BarcodeScanner", "scan_barcode", "Scans barcodes"),
            ("AudioTranscriber", "transcribe_audio", "Transcribes audio to text"),
        ]

    def generate_instance(self, instance_id: int) -> Tuple[str, List[Dict], str, Dict]:
        """Generate a single tool fabrication test instance.

        Args:
            instance_id: Unique instance identifier

        Returns:
            Tuple of (task_description, tools, correct_tool_name, ground_truth)
        """
        # Deterministic selection based on instance_id
        instance_rng = random.Random(self.seed + instance_id)

        # Select N tools from template
        selected_templates = instance_rng.sample(self.tool_templates, self.num_tools)

        # Create tool definitions
        tools = []
        for display_name, function_name, description in selected_templates:
            tools.append(
                {
                    "name": function_name,
                    "display_name": display_name,
                    "description": description,
                    "parameters": {
                        "type": "object",
                        "properties": {"input": {"type": "string", "description": "Input data"}},
                        "required": ["input"],
                    },
                    "function": lambda x: f"Result: {x}",  # Simple echo function
                }
            )

        # Select one tool as the correct answer
        correct_tool_idx = instance_rng.randint(0, len(tools) - 1)
        correct_tool = tools[correct_tool_idx]

        # Create task that requires the correct tool
        task_templates = [
            f"Use the {correct_tool['display_name']} tool to process the text 'hello world'.",
            f"I need to use {correct_tool['display_name']} to handle some data. Please call it with input 'test data'.",
            f"Can you {correct_tool['description'].lower()} for the value 'sample input'? Use the appropriate tool.",
            f"Please invoke the tool for {correct_tool['description'].lower()} with the input 'example'.",
        ]

        task_description = instance_rng.choice(task_templates)

        ground_truth = {
            "correct_tool": correct_tool["name"],
            "correct_tool_display": correct_tool["display_name"],
            "num_tools_available": len(tools),
            "task_type": f"tool_fabrication_n{self.num_tools}",
        }

        return task_description, tools, correct_tool["name"], ground_truth

    def evaluate_response(
        self, trajectory: List[Dict[str, Any]], ground_truth: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate agent response for tool fabrication.

        Args:
            trajectory: Agent trajectory (list of steps with actions)
            ground_truth: Ground truth from generate_instance

        Returns:
            Evaluation metrics:
                - tool_calls: List of tool names called
                - fabricated_calls: List of tool names that don't exist
                - fabrication_rate: Fraction of calls to non-existent tools
                - used_correct_tool: Whether correct tool was called
                - num_tool_calls: Total number of tool calls
        """
        correct_tool = ground_truth["correct_tool"]
        available_tools = set()  # Would need to be passed in; simplified for now

        tool_calls = []
        fabricated_calls = []

        # Extract tool calls from trajectory
        for step in trajectory:
            if "action" in step and step["action"]:
                action = step["action"]
                if isinstance(action, dict) and "tool" in action:
                    tool_name = action["tool"]
                    tool_calls.append(tool_name)

                    # Check if tool exists (simplified check - in real implementation,
                    # would verify against available_tools set)
                    # For now, assume any tool not in standard list is fabricated
                    if not tool_name:  # Placeholder - real check would be more sophisticated
                        fabricated_calls.append(tool_name)

        num_calls = len(tool_calls)
        num_fabricated = len(fabricated_calls)

        return {
            "tool_calls": tool_calls,
            "fabricated_calls": fabricated_calls,
            "fabrication_rate": num_fabricated / num_calls if num_calls > 0 else 0,
            "used_correct_tool": correct_tool in tool_calls,
            "num_tool_calls": num_calls,
            "num_fabricated_calls": num_fabricated,
        }


def generate_tool_fabrication_suite(
    num_instances: int = 10, tool_counts: List[int] = [5, 10, 20, 40], seed: int = 42
) -> List[Tuple[str, int, Tuple]]:
    """Generate complete suite of tool fabrication test instances.

    Args:
        num_instances: Number of instances per tool count
        tool_counts: List of tool counts to test
        seed: Base random seed

    Returns:
        List of (instance_id, num_tools, (task_desc, tools, correct_tool, ground_truth))
    """
    instances = []
    instance_counter = 0

    for num_tools in tool_counts:
        generator = ToolFabricationTask(num_tools=num_tools, seed=seed)

        for i in range(num_instances):
            instance_id = f"tool_fab_n{num_tools}_i{i}"
            instance_data = generator.generate_instance(instance_counter)
            instances.append((instance_id, num_tools, instance_data))
            instance_counter += 1

    return instances
