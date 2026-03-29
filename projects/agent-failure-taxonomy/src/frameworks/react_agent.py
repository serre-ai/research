"""
ReAct agent implementation using LangChain.

Wrapper around LangChain's AgentExecutor with custom logging
and failure detection.
"""

import os
from typing import Any, Dict, List, Optional

from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate


REACT_PROMPT = """Answer the following question as best you can. You have access to the following tools:

{tools}

Use the following format:

Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought: {agent_scratchpad}"""


class MockTool:
    """Mock tool for testing - returns canned responses."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def run(self, query: str) -> str:
        """Return mock response."""
        if "weather" in self.name.lower():
            return "The current weather in San Francisco is sunny, 72°F."
        if "search" in self.name.lower():
            return f"Search results for '{query}': No relevant information found."
        if "read" in self.name.lower():
            return f"Page content: This is a sample webpage about {query}."
        if "calculator" in self.name.lower():
            try:
                result = eval(query)
                return f"Calculation result: {result}"
            except:
                return "Error: Invalid calculation"
        return f"Tool {self.name} returned: Sample response for '{query}'"


def create_mock_tools(tool_definitions: List[Dict[str, str]]) -> List[Tool]:
    """Create LangChain tools from tool definitions."""
    tools = []
    for tool_def in tool_definitions:
        mock_tool = MockTool(tool_def["name"], tool_def["description"])
        tool = Tool(
            name=tool_def["name"],
            func=mock_tool.run,
            description=tool_def["description"],
        )
        tools.append(tool)
    return tools


def create_llm(model_name: str, temperature: float = 0.0):
    """Create LLM instance."""
    if "gpt" in model_name.lower():
        return ChatOpenAI(model=model_name, temperature=temperature)
    elif "claude" in model_name.lower():
        return ChatAnthropic(model=model_name, temperature=temperature)
    else:
        raise ValueError(f"Unsupported model: {model_name}")


class ReActAgent:
    """ReAct agent with logging and failure detection."""

    def __init__(
        self,
        model_name: str,
        tools: List[Dict[str, str]],
        temperature: float = 0.0,
        max_iterations: int = 15,
        verbose: bool = True,
    ):
        self.model_name = model_name
        self.temperature = temperature
        self.max_iterations = max_iterations
        self.verbose = verbose

        # Create LLM and tools
        self.llm = create_llm(model_name, temperature)
        self.tools = create_mock_tools(tools)

        # Create agent
        prompt = PromptTemplate.from_template(REACT_PROMPT)
        agent = create_react_agent(self.llm, self.tools, prompt)

        self.executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=verbose,
            max_iterations=max_iterations,
            handle_parsing_errors=True,
            return_intermediate_steps=True,
        )

    def run(self, task_description: str) -> Dict[str, Any]:
        """
        Run agent on task.

        Returns:
            {
                "output": final answer string,
                "intermediate_steps": list of (action, observation) tuples,
                "error": error message if failed,
            }
        """
        try:
            result = self.executor.invoke({"input": task_description})
            return {
                "output": result.get("output"),
                "intermediate_steps": result.get("intermediate_steps", []),
                "error": None,
            }
        except Exception as e:
            return {
                "output": None,
                "intermediate_steps": [],
                "error": str(e),
            }

    def get_trace(self, intermediate_steps: List) -> List[Dict[str, Any]]:
        """
        Convert intermediate steps to structured trace.

        Args:
            intermediate_steps: List of (AgentAction, observation) tuples

        Returns:
            List of step dictionaries
        """
        trace = []
        for i, (action, observation) in enumerate(intermediate_steps):
            step = {
                "step": i + 1,
                "thought": getattr(action, "log", ""),
                "action": action.tool,
                "action_input": action.tool_input,
                "observation": observation,
            }
            trace.append(step)
        return trace


def test_react_agent():
    """Quick test of ReAct agent."""
    tools = [
        {"name": "get_weather", "description": "Get current weather for a location"},
        {"name": "search", "description": "Search for information"},
    ]

    agent = ReActAgent(
        model_name="gpt-4o-mini",
        tools=tools,
        temperature=0.0,
        max_iterations=5,
    )

    result = agent.run("What is the weather in San Francisco?")
    print("Output:", result["output"])
    print("Steps:", len(result["intermediate_steps"]))

    trace = agent.get_trace(result["intermediate_steps"])
    for step in trace:
        print(f"\nStep {step['step']}:")
        print(f"  Action: {step['action']}")
        print(f"  Observation: {step['observation'][:50]}...")


if __name__ == "__main__":
    test_react_agent()
