"""Configuration for agent failure taxonomy experiments."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / "src"
EXPERIMENTS_DIR = PROJECT_ROOT / "experiments"
LOGS_DIR = EXPERIMENTS_DIR / "pilot" / "logs"
RESULTS_DIR = EXPERIMENTS_DIR / "pilot"

# Create directories if they don't exist
LOGS_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# API Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Model Configuration
DEFAULT_MODEL = "claude-3-5-sonnet-20241022"
DEFAULT_TEMPERATURE = 0.0
DEFAULT_MAX_TOKENS = 4096

# Experiment Configuration
MAX_ITERATIONS = 10
RUNS_PER_CONDITION = 5

# Cost tracking (per 1M tokens)
CLAUDE_SONNET_INPUT_COST = 3.0  # $3/M input tokens
CLAUDE_SONNET_OUTPUT_COST = 15.0  # $15/M output tokens
GPT4O_INPUT_COST = 2.5  # $2.50/M input tokens
GPT4O_OUTPUT_COST = 10.0  # $10/M output tokens
