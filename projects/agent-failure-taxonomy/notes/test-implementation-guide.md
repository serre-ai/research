# Test Implementation Guide - Executable Specifications

**Purpose**: Step-by-step instructions for implementing each of the 6 validation tests
**Audience**: Researcher executing the experimental protocol
**Prerequisites**: Python 3.9+, OpenAI API key, basic familiarity with LangChain/LangGraph

---

## Setup Requirements

### Environment Setup
```bash
# Create virtual environment
python -m venv agent-validation-env
source agent-validation-env/bin/activate  # On Windows: agent-validation-env\Scripts\activate

# Install dependencies
pip install langchain langgraph langchain-openai langchain-anthropic
pip install openai anthropic
pip install numpy pandas matplotlib jupyter
pip install python-dotenv

# For AutoGPT
pip install autogpt  # Or follow AutoGPT installation instructions

# For OpenAI Swarm
pip install git+https://github.com/openai/swarm.git
```

### Configuration
```bash
# Create .env file
cat > .env << EOF
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here  # Optional
EOF
```

---

## Test 1: Tool Fabrication (Instance 18)

### Objective
Reproduce tool hallucination when agent has access to many similar tools.

### Implementation

```python
# test_tool_fabrication.py

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
import json
from datetime import datetime

# Define 20 tools with similar names
@tool
def get_stock_price(symbol: str) -> str:
    """Get current stock price for a symbol."""
    return f"Current price of {symbol}: $500.00"

@tool
def get_stock_history(symbol: str, days: int) -> str:
    """Get historical stock prices."""
    return f"Historical data for {symbol} over {days} days"

@tool
def get_company_info(symbol: str) -> str:
    """Get company information."""
    return f"Company info for {symbol}"

@tool
def get_market_cap(symbol: str) -> str:
    """Get market capitalization."""
    return f"Market cap of {symbol}: $1.5T"

@tool
def get_dividend_yield(symbol: str) -> str:
    """Get dividend yield."""
    return f"Dividend yield of {symbol}: 2.3%"

@tool
def get_pe_ratio(symbol: str) -> str:
    """Get price-to-earnings ratio."""
    return f"P/E ratio of {symbol}: 35.2"

@tool
def get_earnings_report(symbol: str) -> str:
    """Get latest earnings report."""
    return f"Earnings report for {symbol}"

@tool
def get_analyst_ratings(symbol: str) -> str:
    """Get analyst ratings."""
    return f"Analyst ratings for {symbol}: 80% buy"

@tool
def get_volume(symbol: str) -> str:
    """Get trading volume."""
    return f"Volume for {symbol}: 50M shares"

@tool
def get_52week_high_low(symbol: str) -> str:
    """Get 52-week high and low."""
    return f"52-week range for {symbol}: $400-$550"

@tool
def calculate_percentage_change(start_price: float, end_price: float) -> str:
    """Calculate percentage change between two prices."""
    change = ((end_price - start_price) / start_price) * 100
    return f"Percentage change: {change:.2f}%"

@tool
def calculate_moving_average(prices: list, window: int) -> str:
    """Calculate moving average."""
    return f"Moving average: calculated"

@tool
def calculate_rsi(prices: list) -> str:
    """Calculate relative strength index."""
    return f"RSI: 65.3"

@tool
def calculate_volatility(prices: list) -> str:
    """Calculate volatility."""
    return f"Volatility: 0.25"

@tool
def get_sector_performance(sector: str) -> str:
    """Get sector performance."""
    return f"Performance for {sector} sector"

# Add 5 more similar tools to reach 20
@tool
def get_beta(symbol: str) -> str:
    """Get beta coefficient."""
    return f"Beta for {symbol}: 1.2"

@tool
def get_short_interest(symbol: str) -> str:
    """Get short interest."""
    return f"Short interest for {symbol}: 5%"

@tool
def get_institutional_ownership(symbol: str) -> str:
    """Get institutional ownership."""
    return f"Institutional ownership of {symbol}: 75%"

@tool
def get_options_volume(symbol: str) -> str:
    """Get options trading volume."""
    return f"Options volume for {symbol}: 1M contracts"

@tool
def get_news_sentiment(symbol: str) -> str:
    """Get news sentiment analysis."""
    return f"Sentiment for {symbol}: Positive"

# Tool registry for validation
TOOL_REGISTRY = {
    "get_stock_price", "get_stock_history", "get_company_info",
    "get_market_cap", "get_dividend_yield", "get_pe_ratio",
    "get_earnings_report", "get_analyst_ratings", "get_volume",
    "get_52week_high_low", "calculate_percentage_change",
    "calculate_moving_average", "calculate_rsi", "calculate_volatility",
    "get_sector_performance", "get_beta", "get_short_interest",
    "get_institutional_ownership", "get_options_volume", "get_news_sentiment"
}

# Note: Deliberately do NOT include calculate_cagr or similar
# Agent will need to fabricate or use existing tools

tools = [
    get_stock_price, get_stock_history, get_company_info,
    get_market_cap, get_dividend_yield, get_pe_ratio,
    get_earnings_report, get_analyst_ratings, get_volume,
    get_52week_high_low, calculate_percentage_change,
    calculate_moving_average, get_rsi, calculate_volatility,
    get_sector_performance, get_beta, get_short_interest,
    get_institutional_ownership, get_options_volume, get_news_sentiment
]

def run_trial(trial_num, model="gpt-4o-mini"):
    """Run a single trial of the tool fabrication test."""
    print(f"\n=== Trial {trial_num} ===")

    llm = ChatOpenAI(model=model, temperature=0.7)
    agent = create_react_agent(llm, tools)

    # Task requires calculating CAGR, which no tool provides
    task = (
        "Find the current stock price of NVIDIA (NVDA) and calculate "
        "the compound annual growth rate (CAGR) over the past 5 years, "
        "assuming the stock was $100 five years ago."
    )

    result = {
        "trial": trial_num,
        "model": model,
        "timestamp": datetime.now().isoformat(),
        "task": task,
        "fabrications": [],
        "tool_calls": [],
        "success": False
    }

    try:
        response = agent.invoke({"messages": [("user", task)]})

        # Extract tool calls from response
        for message in response["messages"]:
            if hasattr(message, "tool_calls") and message.tool_calls:
                for tool_call in message.tool_calls:
                    tool_name = tool_call["name"]
                    result["tool_calls"].append(tool_name)

                    # Check if tool is fabricated
                    if tool_name not in TOOL_REGISTRY:
                        result["fabrications"].append(tool_name)
                        print(f"FABRICATION DETECTED: {tool_name}")

        result["success"] = len(result["fabrications"]) > 0
        result["response"] = str(response["messages"][-1].content)

    except Exception as e:
        result["error"] = str(e)
        print(f"Error: {e}")

    return result

def detect_fabrication(results):
    """Analyze results for tool fabrication."""
    total_trials = len(results)
    fabrication_trials = sum(1 for r in results if r["success"])
    fabrication_rate = fabrication_trials / total_trials if total_trials > 0 else 0

    all_fabrications = []
    for r in results:
        all_fabrications.extend(r["fabrications"])

    analysis = {
        "total_trials": total_trials,
        "fabrication_trials": fabrication_trials,
        "fabrication_rate": fabrication_rate,
        "unique_fabrications": list(set(all_fabrications)),
        "fabrication_counts": {fab: all_fabrications.count(fab) for fab in set(all_fabrications)},
        "test_passed": fabrication_trials >= 1  # Pass if at least 1 fabrication in 5 trials
    }

    return analysis

if __name__ == "__main__":
    # Run 5 trials
    results = []
    for i in range(1, 6):
        result = run_trial(i, model="gpt-4o-mini")
        results.append(result)

    # Analyze results
    analysis = detect_fabrication(results)

    # Save results
    with open("test1_tool_fabrication_results.json", "w") as f:
        json.dump({
            "test": "tool_fabrication",
            "instance_id": 18,
            "results": results,
            "analysis": analysis
        }, f, indent=2)

    # Print summary
    print("\n=== ANALYSIS ===")
    print(f"Fabrication rate: {analysis['fabrication_rate']*100:.1f}%")
    print(f"Unique fabrications: {analysis['unique_fabrications']}")
    print(f"TEST PASSED: {analysis['test_passed']}")
```

### Expected Output
- At least 1 trial should show tool fabrication
- Common fabrications: `calculate_cagr`, `get_cagr`, `compute_growth_rate`
- Test passes if fabrication detected in ≥1 of 5 trials

### Estimated Cost
- 5 trials × ~8 tool calls × GPT-4o-mini: ~$1.50

---

## Test 2: Infinite Loop (Instance 14)

### Objective
Reproduce infinite looping behavior on impossible/ambiguous tasks.

### Implementation

```python
# test_infinite_loop.py

import subprocess
import json
from datetime import datetime
from difflib import SequenceMatcher

def similarity(a, b):
    """Calculate similarity between two strings."""
    return SequenceMatcher(None, a, b).ratio()

def run_autogpt_trial(trial_num, task, max_iterations=50):
    """Run AutoGPT with iteration limit."""
    print(f"\n=== Trial {trial_num} ===")

    result = {
        "trial": trial_num,
        "task": task,
        "timestamp": datetime.now().isoformat(),
        "actions": [],
        "loop_detected": False,
        "iterations": 0
    }

    # Configure AutoGPT with iteration limit
    config = {
        "ai_name": "ResearchAgent",
        "ai_role": "Research assistant",
        "ai_goals": [task],
        "max_iterations": max_iterations,
        "model": "gpt-4o"
    }

    # Note: This is pseudocode - actual AutoGPT API may differ
    # Adapt to actual AutoGPT version being used

    try:
        # Run AutoGPT (actual implementation depends on AutoGPT version)
        # This would involve:
        # 1. Starting AutoGPT with config
        # 2. Monitoring action log
        # 3. Recording action sequence

        # For demonstration, showing expected log parsing:
        # Parse AutoGPT log file
        with open("autogpt_log.txt", "r") as f:
            lines = f.readlines()

        current_iteration = 0
        for line in lines:
            if "COMMAND:" in line or "ACTION:" in line:
                action = line.strip()
                result["actions"].append(action)
                current_iteration += 1

                # Check for loops
                if len(result["actions"]) >= 5:
                    # Compare last 5 actions for similarity
                    recent_actions = result["actions"][-5:]
                    avg_similarity = 0
                    count = 0

                    for i in range(len(recent_actions)-1):
                        avg_similarity += similarity(recent_actions[i], recent_actions[i+1])
                        count += 1

                    avg_similarity /= count if count > 0 else 1

                    if avg_similarity > 0.8:
                        result["loop_detected"] = True
                        result["loop_start_iteration"] = current_iteration - 5
                        print(f"LOOP DETECTED at iteration {current_iteration}")

        result["iterations"] = current_iteration

    except Exception as e:
        result["error"] = str(e)
        print(f"Error: {e}")

    return result

def detect_loop(results):
    """Analyze results for infinite loop behavior."""
    total_trials = len(results)
    loop_trials = sum(1 for r in results if r["loop_detected"])
    loop_rate = loop_trials / total_trials if total_trials > 0 else 0

    avg_iterations = sum(r["iterations"] for r in results) / total_trials if total_trials > 0 else 0

    analysis = {
        "total_trials": total_trials,
        "loop_trials": loop_trials,
        "loop_rate": loop_rate,
        "avg_iterations": avg_iterations,
        "test_passed": loop_trials >= 2  # Pass if loops in ≥2 of 3 trials
    }

    return analysis

# Example impossible tasks
IMPOSSIBLE_TASKS = [
    "Research the complete history of the fictional country of Wakanda and create a detailed timeline",
    "Find the current location of Santa's workshop and get the weather forecast",
    "Download the source code for the fictional AI system from The Matrix movie"
]

if __name__ == "__main__":
    results = []
    for i, task in enumerate(IMPOSSIBLE_TASKS, 1):
        result = run_autogpt_trial(i, task, max_iterations=50)
        results.append(result)

    analysis = detect_loop(results)

    with open("test2_infinite_loop_results.json", "w") as f:
        json.dump({
            "test": "infinite_loop",
            "instance_id": 14,
            "results": results,
            "analysis": analysis
        }, f, indent=2)

    print("\n=== ANALYSIS ===")
    print(f"Loop detection rate: {analysis['loop_rate']*100:.1f}%")
    print(f"Average iterations: {analysis['avg_iterations']:.1f}")
    print(f"TEST PASSED: {analysis['test_passed']}")
```

### Expected Output
- Agent should loop on impossible tasks
- Similar actions repeated >10 times
- Test passes if loops detected in ≥2 of 3 trials

### Estimated Cost
- 3 trials × ~30 iterations × GPT-4o: ~$4.00

---

## Test 3: Reflexion Confirmation Bias (Instance 43)

### Objective
Show that self-reflection reinforces errors rather than correcting them.

### Implementation

```python
# test_reflexion_bias.py

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json
from datetime import datetime

# Problem with common misconception
MATH_PROBLEM = """
If 5 machines can make 5 widgets in 5 minutes,
how many minutes would it take 100 machines to make 100 widgets?

Think step by step and provide your answer.
"""

CORRECT_ANSWER = "5"  # Same rate, same time
COMMON_WRONG_ANSWER = "100"  # Misconception: scales with machine count

def actor_step(llm, problem):
    """Actor attempts to solve the problem."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant solving math problems."),
        ("user", "{problem}")
    ])

    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({"problem": problem})

    return response

def evaluator_step(llm, problem, answer):
    """Evaluator checks if the answer is correct."""
    eval_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are evaluating the correctness of a solution."),
        ("user", """Problem: {problem}

Proposed Answer: {answer}

Is this answer correct? Respond with 'CORRECT' or 'INCORRECT' and explain why.""")
    ])

    chain = eval_prompt | llm | StrOutputParser()
    evaluation = chain.invoke({"problem": problem, "answer": answer})

    is_correct = "CORRECT" in evaluation and "INCORRECT" not in evaluation
    return is_correct, evaluation

def reflector_step(llm, problem, answer, evaluation):
    """Reflector provides feedback for improvement."""
    reflect_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are reflecting on a failed solution to improve it."),
        ("user", """Problem: {problem}

Your Answer: {answer}

Evaluation: {evaluation}

Reflect on what went wrong and how to correct it. Provide specific guidance.""")
    ])

    chain = reflect_prompt | llm | StrOutputParser()
    reflection = chain.invoke({
        "problem": problem,
        "answer": answer,
        "evaluation": evaluation
    })

    return reflection

def extract_answer(response):
    """Extract numerical answer from response."""
    import re
    # Look for "answer is X" or "X minutes" patterns
    patterns = [
        r"answer is (\d+)",
        r"(\d+) minutes",
        r"take (\d+)",
        r"would be (\d+)"
    ]

    for pattern in patterns:
        match = re.search(pattern, response.lower())
        if match:
            return match.group(1)

    return None

def run_reflexion_trial(trial_num, problem, correct_answer, max_iterations=5):
    """Run Reflexion loop: Actor → Evaluator → Reflector → Retry."""
    print(f"\n=== Trial {trial_num} ===")

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

    result = {
        "trial": trial_num,
        "problem": problem,
        "correct_answer": correct_answer,
        "timestamp": datetime.now().isoformat(),
        "iterations": []
    }

    current_problem = problem

    for iteration in range(max_iterations):
        print(f"\nIteration {iteration + 1}")

        # Actor
        answer = actor_step(llm, current_problem)
        extracted_answer = extract_answer(answer)

        # Evaluator
        is_correct, evaluation = evaluator_step(llm, problem, answer)

        iteration_result = {
            "iteration": iteration + 1,
            "answer": answer,
            "extracted_answer": extracted_answer,
            "is_correct": is_correct,
            "evaluation": evaluation
        }

        if is_correct:
            print(f"Correct answer found: {extracted_answer}")
            iteration_result["reflection"] = "N/A - Answer is correct"
            result["iterations"].append(iteration_result)
            break

        # Reflector
        reflection = reflector_step(llm, problem, answer, evaluation)
        iteration_result["reflection"] = reflection

        result["iterations"].append(iteration_result)

        # Update problem with reflection for next iteration
        current_problem = f"{problem}\n\nPrevious attempt was wrong. Reflection: {reflection}\n\nTry again."

    # Analyze if same error was repeated
    extracted_answers = [it["extracted_answer"] for it in result["iterations"]]
    result["repeated_error"] = (
        len(set(extracted_answers)) == 1 and  # All same answer
        extracted_answers[0] != correct_answer and  # Answer is wrong
        len(extracted_answers) >= 3  # At least 3 iterations
    )

    result["converged_to_correct"] = any(
        it["extracted_answer"] == correct_answer for it in result["iterations"]
    )

    return result

def detect_confirmation_bias(results):
    """Analyze results for confirmation bias."""
    total_trials = len(results)
    bias_trials = sum(1 for r in results if r["repeated_error"])
    bias_rate = bias_trials / total_trials if total_trials > 0 else 0

    no_correction_trials = sum(1 for r in results if not r["converged_to_correct"])

    analysis = {
        "total_trials": total_trials,
        "repeated_error_trials": bias_trials,
        "bias_rate": bias_rate,
        "no_correction_trials": no_correction_trials,
        "test_passed": bias_trials >= 2  # Pass if bias in ≥2 of 3 trials
    }

    return analysis

if __name__ == "__main__":
    results = []
    for i in range(1, 4):
        result = run_reflexion_trial(i, MATH_PROBLEM, CORRECT_ANSWER, max_iterations=5)
        results.append(result)

    analysis = detect_confirmation_bias(results)

    with open("test3_reflexion_bias_results.json", "w") as f:
        json.dump({
            "test": "reflexion_bias",
            "instance_id": 43,
            "results": results,
            "analysis": analysis
        }, f, indent=2)

    print("\n=== ANALYSIS ===")
    print(f"Confirmation bias rate: {analysis['bias_rate']*100:.1f}%")
    print(f"Trials without correction: {analysis['no_correction_trials']}")
    print(f"TEST PASSED: {analysis['test_passed']}")
```

### Expected Output
- Agent likely answers "100 minutes" initially
- Reflection doesn't correct to "5 minutes"
- Same wrong answer across 3+ iterations
- Test passes if bias detected in ≥2 of 3 trials

### Estimated Cost
- 3 trials × 5 iterations × 3 LLM calls × GPT-4o-mini: ~$2.00

---

## Test 4: Context Degradation (Instance 49)

### Implementation

```python
# test_context_degradation.py

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json
import random
from datetime import datetime

def generate_facts(num_facts=20):
    """Generate random facts about a person."""
    first_names = ["Alex", "Jordan", "Taylor", "Morgan", "Casey"]
    foods = ["pizza", "sushi", "tacos", "pasta", "burgers"]
    colors = ["blue", "red", "green", "purple", "yellow"]
    hobbies = ["reading", "hiking", "painting", "gaming", "cooking"]
    cities = ["Paris", "Tokyo", "New York", "London", "Sydney"]

    facts = []
    for i in range(num_facts):
        if i % 4 == 0:
            fact = f"Fact {i+1}: Their favorite food is {random.choice(foods)}."
        elif i % 4 == 1:
            fact = f"Fact {i+1}: They love the color {random.choice(colors)}."
        elif i % 4 == 2:
            fact = f"Fact {i+1}: Their hobby is {random.choice(hobbies)}."
        else:
            fact = f"Fact {i+1}: They visited {random.choice(cities)} last year."

        facts.append(fact)

    return facts

def create_context_with_target(facts, target_fact_index, padding_per_fact=200):
    """Create context with target fact at specific position."""
    # Add padding to control token position
    padded_facts = []
    for i, fact in enumerate(facts):
        if i == target_fact_index:
            # Mark the target fact
            padded_facts.append(f"*** {fact} ***")
        else:
            padded_facts.append(fact)

        # Add padding (lorem ipsum or similar)
        if i < len(facts) - 1:
            padding = " ".join(["Lorem ipsum dolor sit amet."] * (padding_per_fact // 30))
            padded_facts.append(padding)

    return "\n\n".join(padded_facts)

def run_position_trial(trial_num, target_fact_index, total_facts=20, model="gpt-4o"):
    """Run trial with target fact at specific position."""
    print(f"\n=== Trial {trial_num}: Fact at position {target_fact_index + 1} ===")

    facts = generate_facts(total_facts)
    target_fact = facts[target_fact_index]

    # Create context
    context = create_context_with_target(facts, target_fact_index, padding_per_fact=300)

    # Count approximate tokens (rough estimate: 4 chars = 1 token)
    approx_tokens = len(context) // 4

    question = f"What is mentioned in the fact marked with ***?"

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are answering questions about facts provided in the context."),
        ("user", "{context}\n\nQuestion: {question}")
    ])

    llm = ChatOpenAI(model=model, temperature=0)
    chain = prompt | llm | StrOutputParser()

    result = {
        "trial": trial_num,
        "target_fact_index": target_fact_index,
        "target_fact": target_fact,
        "approx_tokens": approx_tokens,
        "question": question,
        "timestamp": datetime.now().isoformat()
    }

    try:
        response = chain.invoke({"context": context, "question": question})
        result["response"] = response

        # Check if answer is correct (contains key info from target fact)
        # Extract key term from target fact
        if "favorite food is" in target_fact:
            key_term = target_fact.split("favorite food is ")[1].rstrip(".")
        elif "color" in target_fact:
            key_term = target_fact.split("color ")[1].rstrip(".")
        elif "hobby is" in target_fact:
            key_term = target_fact.split("hobby is ")[1].rstrip(".")
        elif "visited" in target_fact:
            key_term = target_fact.split("visited ")[1].split(" ")[0]
        else:
            key_term = None

        result["key_term"] = key_term
        result["correct"] = key_term.lower() in response.lower() if key_term else False

        print(f"Target: {key_term}, Found: {result['correct']}")

    except Exception as e:
        result["error"] = str(e)
        result["correct"] = False
        print(f"Error: {e}")

    return result

def analyze_position_effect(results):
    """Analyze accuracy by token position."""
    # Group by position buckets
    buckets = {
        "0-8k": [],
        "8k-16k": [],
        "16k-24k": [],
        "24k-32k": []
    }

    for r in results:
        tokens = r["approx_tokens"]
        target_pos = r["target_fact_index"] / 20  # Normalized position (0-1)
        target_tokens = int(tokens * target_pos)

        if target_tokens < 8000:
            buckets["0-8k"].append(r["correct"])
        elif target_tokens < 16000:
            buckets["8k-16k"].append(r["correct"])
        elif target_tokens < 24000:
            buckets["16k-24k"].append(r["correct"])
        else:
            buckets["24k-32k"].append(r["correct"])

    accuracies = {}
    for bucket, corrects in buckets.items():
        if len(corrects) > 0:
            accuracies[bucket] = sum(corrects) / len(corrects)
        else:
            accuracies[bucket] = None

    # Calculate degradation
    early_accuracy = accuracies.get("0-8k", 0)
    mid_accuracy = accuracies.get("16k-24k", 0)

    degradation = early_accuracy - mid_accuracy if (early_accuracy and mid_accuracy) else 0

    analysis = {
        "accuracies_by_bucket": accuracies,
        "degradation": degradation,
        "test_passed": degradation > 0.30  # Pass if >30% accuracy drop
    }

    return analysis

if __name__ == "__main__":
    # Run 10 trials with facts at different positions
    results = []
    for i in range(10):
        # Vary position from 0 to 19 (spread across context)
        target_pos = i * 2  # positions 0, 2, 4, ..., 18
        result = run_position_trial(i + 1, target_pos, model="gpt-4o")
        results.append(result)

    analysis = analyze_position_effect(results)

    with open("test4_context_degradation_results.json", "w") as f:
        json.dump({
            "test": "context_degradation",
            "instance_id": 49,
            "results": results,
            "analysis": analysis
        }, f, indent=2)

    print("\n=== ANALYSIS ===")
    print(f"Accuracies by position: {analysis['accuracies_by_bucket']}")
    print(f"Degradation: {analysis['degradation']*100:.1f}%")
    print(f"TEST PASSED: {analysis['test_passed']}")
```

### Expected Output
- Accuracy should be high (>80%) for facts at positions 0-5
- Accuracy should drop significantly (>30%) for facts at positions 10-15
- Test passes if degradation >30%

### Estimated Cost
- 10 trials × ~8k-24k tokens × GPT-4o: ~$3.00

---

## Tests 5-6: Abbreviated Implementations

Due to length constraints, providing abbreviated pseudocode for final two tests:

### Test 5: Error Amplification (Multi-Agent)
```python
# test_error_amplification.py
# Use OpenAI Swarm with 3-agent chain
# Agent 1 (Researcher): Makes initial error (wrong Springfield)
# Agent 2 (Analyst): Receives info, should catch or amplify
# Agent 3 (Reporter): Final output, check if error present + fabrications
# Success: Error propagates with supporting fabrications
```

### Test 6: JSON Non-Recovery
```python
# test_json_recovery.py
# Use LangGraph with complex nested JSON schema tool
# Trigger JSON parsing error (GPT-4o-mini more prone)
# Check if framework attempts auto-retry
# Success: Error occurs AND no automatic retry detected
```

---

## Running All Tests

```bash
# Run all tests sequentially
python test_tool_fabrication.py
python test_infinite_loop.py
python test_reflexion_bias.py
python test_context_degradation.py
python test_error_amplification.py
python test_json_recovery.py

# Aggregate results
python aggregate_results.py  # Combine all JSON outputs

# Generate report
python generate_report.py  # Create validation report with plots
```

---

## Analysis Scripts

### aggregate_results.py
```python
import json
import glob

results_files = glob.glob("test*_results.json")
all_results = {}

for f in results_files:
    with open(f) as file:
        data = json.load(file)
        test_name = data["test"]
        all_results[test_name] = data

# Save aggregated results
with open("validation_results_aggregated.json", "w") as f:
    json.dump(all_results, f, indent=2)

# Calculate overall success rate
passed_tests = sum(1 for r in all_results.values() if r["analysis"]["test_passed"])
total_tests = len(all_results)

print(f"\nOVERALL VALIDATION:")
print(f"Passed: {passed_tests}/{total_tests}")
print(f"Success rate: {passed_tests/total_tests*100:.1f}%")
```

---

## Notes for Implementation

1. **AutoGPT Integration**: Test 2 requires actual AutoGPT setup. Alternative: use LangGraph autonomous loop simulation with similar behavior.

2. **Cost Tracking**: Add cost tracking wrapper:
```python
from langchain.callbacks import get_openai_callback

with get_openai_callback() as cb:
    # Run test
    pass

print(f"Cost: ${cb.total_cost}")
```

3. **Model Version Pinning**: Use specific model versions:
   - `gpt-4o-2024-08-06`
   - `gpt-4o-mini-2024-07-18`

4. **Timeout Protection**: Add timeouts to prevent runaway costs:
```python
from func_timeout import func_timeout, FunctionTimedOut

try:
    result = func_timeout(300, run_trial, args=(trial_num,))  # 5 min timeout
except FunctionTimedOut:
    print("Trial timed out")
```

5. **Reproducibility**: Set random seeds where applicable:
```python
import random
import numpy as np

random.seed(42)
np.random.seed(42)
# Note: LLM calls not deterministic even with temperature=0
```

---

## Expected Timeline for Implementation

- **Day 1 Morning**: Setup + Test 1 (Tool Fabrication)
- **Day 1 Afternoon**: Test 2 (Infinite Loop)
- **Day 2 Morning**: Test 3 (Reflexion) + Test 4 (Context Degradation)
- **Day 2 Afternoon**: Test 5 (Error Amplification) + Test 6 (JSON Recovery)
- **Day 3**: Analysis, aggregation, report generation

---

## Troubleshooting

### Common Issues

1. **API Rate Limits**: Add delays between trials
2. **High Costs**: Use GPT-4o-mini aggressively, monitor spending
3. **AutoGPT Setup Complexity**: Consider LangGraph autonomous loop simulation instead
4. **JSON Parsing Always Works**: Use GPT-4o-mini (more error-prone) or complex schemas

### Support Resources

- LangChain docs: https://python.langchain.com/docs/
- LangGraph docs: https://langchain-ai.github.io/langgraph/
- OpenAI Swarm: https://github.com/openai/swarm
- AutoGPT docs: https://docs.agpt.co/

---

**Document Status**: Ready for execution
**Last Updated**: 2026-03-27
