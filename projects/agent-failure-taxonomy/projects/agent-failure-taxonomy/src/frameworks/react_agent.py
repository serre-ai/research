"""
LangChain ReAct agent implementation.

Implements the ReAct (Reasoning + Acting) architecture for controlled failure reproduction.
"""

import re
from typing import Any, Dict, List, Optional
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI

from frameworks.base import (
    AgentFramework,
    AgentArchitecture,
    AgentTrace,
    AgentStep,
    ToolCall
)


class ReActAgent(AgentFramework):
    """
    LangChain ReAct agent wrapper.

    ReAct architecture: Observation → Thought → Action loop
    High risk for: Progress monitoring failures, tool hallucination, infinite loops
    """

    @property
    def architecture(self) -> AgentArchitecture:
        return AgentArchitecture.REACT

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._setup_llm()

    def _setup_llm(self):
        """Initialize LLM client based on model name."""
        if "claude" in self.model_name.lower():
            self.llm = ChatAnthropic(
                model=self.model_name,
                temperature=self.temperature
            )
        elif "gpt" in self.model_name.lower():
            self.llm = ChatOpenAI(
                model=self.model_name,
                temperature=self.temperature
            )
        else:
            raise ValueError(f"Unsupported model: {self.model_name}")

    def run_task(
        self,
        task: str,
        tools: List[Any],
        context: Optional[Dict[str, Any]] = None
    ) -> AgentTrace:
        """
        Run ReAct agent on task with given tools.

        Args:
            task: Natural language task description
            tools: List of LangChain tools
            context: Optional initial context (unused in basic ReAct)

        Returns:
            AgentTrace with complete execution history
        """
        # Create ReAct prompt template
        template = """Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}"""

        prompt = PromptTemplate.from_template(template)

        # Create agent
        agent = create_react_agent(self.llm, tools, prompt)
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            max_iterations=self.max_iterations,
            handle_parsing_errors=True,
            return_intermediate_steps=True
        )

        # Execute with error handling
        steps = []
        final_output = ""
        completed = False
        timeout = False
        error = None

        try:
            result = agent_executor.invoke({"input": task})
            intermediate_steps = result.get("intermediate_steps", [])
            final_output = result.get("output", "")
            completed = True

            # Convert intermediate steps to our format
            for i, (action, observation) in enumerate(intermediate_steps):
                tool_calls = self._extract_tool_calls(action, observation)

                step = AgentStep(
                    step_number=i + 1,
                    observation=str(observation),
                    thought=action.log if hasattr(action, 'log') else "",
                    action=action.tool if hasattr(action, 'tool') else str(action),
                    action_input=action.tool_input if hasattr(action, 'tool_input') else {},
                    tool_calls=tool_calls,
                    tokens_used=self._estimate_tokens(action, observation),
                    cost_usd=0.0  # Updated below
                )
                steps.append(step)

        except Exception as e:
            error = str(e)
            if "timeout" in error.lower() or "max_iterations" in error.lower():
                timeout = True

        # Calculate costs
        total_tokens = sum(s.tokens_used for s in steps)
        total_cost = self._estimate_cost(total_tokens)

        for step in steps:
            step.cost_usd = total_cost / len(steps) if steps else 0.0

        self._current_cost += total_cost

        return AgentTrace(
            task=task,
            steps=steps,
            final_output=final_output,
            completed=completed,
            total_tokens=total_tokens,
            total_cost_usd=total_cost,
            timeout=timeout,
            error=error
        )

    def _extract_tool_calls(self, action: Any, observation: Any) -> List[ToolCall]:
        """Extract tool calls from LangChain action/observation."""
        tool_calls = []

        if hasattr(action, 'tool') and hasattr(action, 'tool_input'):
            tool_call = ToolCall(
                tool_name=action.tool,
                parameters=action.tool_input if isinstance(action.tool_input, dict) else {"input": action.tool_input},
                result=observation,
                error=None if not isinstance(observation, Exception) else str(observation),
                hallucinated=False  # Detect this in detect_failure()
            )
            tool_calls.append(tool_call)

        return tool_calls

    def _estimate_tokens(self, action: Any, observation: Any) -> int:
        """Rough token count estimate for step."""
        text = ""
        if hasattr(action, 'log'):
            text += action.log
        text += str(observation)

        # Rough estimate: ~4 chars per token
        return len(text) // 4

    def detect_failure(self, trace: AgentTrace) -> Optional[str]:
        """
        Detect if expected failure occurred in trace.

        Failure types:
        - tool_fabrication: Calls non-existent tool
        - infinite_loop: Repeats same action >3 times
        - progress_stagnation: No progress for >5 steps
        - false_completion: Claims completion but task not done
        """
        if not trace.steps:
            return None

        # Detect tool fabrication
        # (This requires knowing which tools are actually available - passed separately)

        # Detect infinite loop (same action repeated)
        actions = [step.action for step in trace.steps]
        if len(actions) >= 4:
            for i in range(len(actions) - 3):
                if actions[i] == actions[i+1] == actions[i+2] == actions[i+3]:
                    return "infinite_loop"

        # Detect progress stagnation (same observation repeated)
        observations = [step.observation for step in trace.steps]
        if len(observations) >= 6:
            repeated = sum(1 for i in range(len(observations) - 1)
                          if observations[i] == observations[i+1])
            if repeated >= 5:
                return "progress_stagnation"

        # Detect early/false completion
        if trace.completed and len(trace.steps) < 3:
            return "false_completion"  # Suspiciously quick

        return None
