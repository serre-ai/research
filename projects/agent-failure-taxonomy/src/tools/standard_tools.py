"""Standard tool implementations for agent experiments.

These are simplified, mock implementations designed to test agent behavior,
not production-quality tools.
"""

import random
from datetime import datetime
from typing import Any, Dict


class ToolRegistry:
    """Registry of available tools for agent experiments."""

    def __init__(self):
        self.tools = {
            "calculator": self.calculator,
            "search": self.search,
            "weather": self.weather,
            "file_read": self.file_read,
            "file_write": self.file_write,
            "file_list": self.file_list,
            "current_time": self.current_time,
            "random_number": self.random_number,
            "string_length": self.string_length,
            "uppercase": self.uppercase,
            "lowercase": self.lowercase,
            "reverse_string": self.reverse_string,
        }

    def get_tool_names(self) -> list[str]:
        """Return list of available tool names."""
        return list(self.tools.keys())

    def get_tool_descriptions(self) -> str:
        """Return formatted tool descriptions for agent prompts."""
        descriptions = []
        descriptions.append("calculator(expression: str) -> float: Evaluates a mathematical expression")
        descriptions.append("search(query: str) -> str: Searches the web (mock - returns placeholder)")
        descriptions.append("weather(city: str) -> str: Gets current weather (mock)")
        descriptions.append("file_read(filename: str) -> str: Reads a file")
        descriptions.append("file_write(filename: str, content: str) -> str: Writes to a file")
        descriptions.append("file_list() -> list: Lists files in current directory")
        descriptions.append("current_time() -> str: Returns current time")
        descriptions.append("random_number(min: int, max: int) -> int: Generates random number")
        descriptions.append("string_length(text: str) -> int: Returns length of string")
        descriptions.append("uppercase(text: str) -> str: Converts text to uppercase")
        descriptions.append("lowercase(text: str) -> str: Converts text to lowercase")
        descriptions.append("reverse_string(text: str) -> str: Reverses a string")
        return "\n".join(descriptions)

    def call_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Call a tool and return result with metadata."""
        if tool_name not in self.tools:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found. Available tools: {', '.join(self.get_tool_names())}",
                "tool_name": tool_name,
                "hallucinated": True,
            }

        try:
            result = self.tools[tool_name](**kwargs)
            return {
                "success": True,
                "result": result,
                "tool_name": tool_name,
                "hallucinated": False,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "tool_name": tool_name,
                "hallucinated": False,
            }

    # Tool implementations

    def calculator(self, expression: str) -> float:
        """Evaluate a mathematical expression."""
        try:
            # Safe eval with limited namespace
            result = eval(expression, {"__builtins__": {}}, {})
            return float(result)
        except Exception as e:
            raise ValueError(f"Invalid expression: {e}")

    def search(self, query: str) -> str:
        """Mock web search."""
        return f"Mock search results for: {query}. [This is a placeholder - no real search performed]"

    def weather(self, city: str) -> str:
        """Mock weather lookup."""
        temps = [15, 18, 20, 22, 25, 28]
        conditions = ["Sunny", "Cloudy", "Rainy", "Partly cloudy"]
        return f"Weather in {city}: {random.choice(conditions)}, {random.choice(temps)}°C"

    def file_read(self, filename: str) -> str:
        """Read a file (mock - returns error for most files)."""
        # For testing, only "test.txt" exists
        if filename == "test.txt":
            return "This is test file content."
        else:
            raise FileNotFoundError(f"File '{filename}' not found")

    def file_write(self, filename: str, content: str) -> str:
        """Write to a file (mock - just confirms)."""
        return f"Successfully wrote {len(content)} characters to {filename}"

    def file_list(self) -> list:
        """List files (mock - returns fixed list)."""
        return ["test.txt", "data.json", "notes.md"]

    def current_time(self) -> str:
        """Return current time."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def random_number(self, min: int = 0, max: int = 100) -> int:
        """Generate random number."""
        return random.randint(min, max)

    def string_length(self, text: str) -> int:
        """Return string length."""
        return len(text)

    def uppercase(self, text: str) -> str:
        """Convert to uppercase."""
        return text.upper()

    def lowercase(self, text: str) -> str:
        """Convert to lowercase."""
        return text.lower()

    def reverse_string(self, text: str) -> str:
        """Reverse a string."""
        return text[::-1]
