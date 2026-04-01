"""Shared fixtures for Compass research intelligence engine tests."""

import pytest
from datetime import datetime, timedelta, timezone


@pytest.fixture
def synthetic_papers():
    """15 papers with known properties for testing all detectors."""
    now = datetime.now(timezone.utc)
    return [
        # Theory paper WITHOUT empirical validation (gap: missing_empirical)
        {
            "id": "p1",
            "title": "Formal Bounds on Transformer Depth Complexity",
            "abstract": (
                "We prove a theorem showing that fixed-depth transformers have a formal "
                "upper bound on computation. This theoretical framework provides a proof "
                "of complexity limitations. The practical utility of these bounds remains "
                "to be tested in future work."
            ),
            "categories": ["cs.CC", "cs.CL"],
            "authors": [{"name": "Alice Smith"}],
            "discovered_at": (now - timedelta(days=2)).isoformat(),
        },
        # Empirical paper WITHOUT theory (gap: missing_theory)
        {
            "id": "p2",
            "title": "Benchmarking Chain-of-Thought on 50 Tasks",
            "abstract": (
                "We evaluate performance across 50 benchmark tasks using dataset evaluation. "
                "Our experiment shows accuracy improves with chain-of-thought. Results show "
                "significant improvement but lacks formal theoretical explanation for why "
                "this works."
            ),
            "categories": ["cs.CL", "cs.AI"],
            "authors": [{"name": "Bob Jones"}],
            "discovered_at": (now - timedelta(days=3)).isoformat(),
        },
        # Two papers with HIGH topic overlap by DIFFERENT authors (gap: uncovered_connection)
        {
            "id": "p3",
            "title": "Scaling Laws for Language Model Reasoning",
            "abstract": (
                "We study how reasoning capability scales with model parameters and "
                "compute budget in language models. Our analysis reveals predictable "
                "scaling curves for reasoning tasks and benchmarks."
            ),
            "categories": ["cs.CL", "cs.LG"],
            "authors": [{"name": "Carol White"}],
            "discovered_at": (now - timedelta(days=1)).isoformat(),
        },
        {
            "id": "p4",
            "title": "Compute-Optimal Reasoning in Large Language Models",
            "abstract": (
                "We investigate reasoning performance as a function of compute scaling "
                "in language models. Our results demonstrate optimal compute allocation "
                "for reasoning tasks and benchmarks."
            ),
            "categories": ["cs.CL", "cs.LG"],
            "authors": [{"name": "Dave Black"}],
            "discovered_at": (now - timedelta(days=1)).isoformat(),
        },
        # Paper with contradiction signal (contrarian)
        {
            "id": "p5",
            "title": "Chain-of-Thought Does Not Reliably Improve Reasoning",
            "abstract": (
                "Contrary to prior claims, we find that chain-of-thought prompting does "
                "not consistently improve reasoning performance. Our results challenge "
                "the assumption that CoT universally helps."
            ),
            "categories": ["cs.CL"],
            "authors": [{"name": "Eve Green"}],
            "discovered_at": (now - timedelta(days=2)).isoformat(),
        },
        # Paper with benchmark score (frontier)
        {
            "id": "p6",
            "title": "GPT-5 Achieves Human-Level Mathematical Reasoning",
            "abstract": (
                "We report that GPT-5 achieves 95.2% accuracy on GSM8K, a "
                "state-of-the-art result. This represents the first model to reach "
                "human-level performance on mathematical reasoning benchmarks."
            ),
            "categories": ["cs.AI", "cs.CL"],
            "authors": [{"name": "Frank Blue"}],
            "discovered_at": (now - timedelta(days=1)).isoformat(),
        },
        # Papers for trend detection (burst in cs.AI)
        {
            "id": "p7",
            "title": "AI Safety via Debate",
            "abstract": "We propose debate as a mechanism for AI safety oversight verification.",
            "categories": ["cs.AI"],
            "authors": [{"name": "G1"}],
            "discovered_at": (now - timedelta(days=1)).isoformat(),
        },
        {
            "id": "p8",
            "title": "Scalable Oversight Methods",
            "abstract": "Novel approaches to oversight of AI systems for safety.",
            "categories": ["cs.AI"],
            "authors": [{"name": "G2"}],
            "discovered_at": (now - timedelta(days=2)).isoformat(),
        },
        {
            "id": "p9",
            "title": "Constitutional AI Improvements",
            "abstract": "Improved methods for constitutional AI training.",
            "categories": ["cs.AI"],
            "authors": [{"name": "G3"}],
            "discovered_at": (now - timedelta(days=3)).isoformat(),
        },
        {
            "id": "p10",
            "title": "Reward Model Verification",
            "abstract": "Verifying reward models for alignment.",
            "categories": ["cs.AI"],
            "authors": [{"name": "G4"}],
            "discovered_at": (now - timedelta(days=4)).isoformat(),
        },
        # Older papers for baseline
        {
            "id": "p11",
            "title": "Old AI Paper",
            "abstract": "Standard AI research.",
            "categories": ["cs.AI"],
            "authors": [{"name": "H1"}],
            "discovered_at": (now - timedelta(days=25)).isoformat(),
        },
        {
            "id": "p12",
            "title": "Another Old Paper",
            "abstract": "More standard research on machine learning.",
            "categories": ["cs.LG"],
            "authors": [{"name": "H2"}],
            "discovered_at": (now - timedelta(days=28)).isoformat(),
        },
        # Papers that make similar claims (for consensus clustering in contrarian)
        {
            "id": "p13",
            "title": "CoT Improves Math Reasoning",
            "abstract": (
                "We show that chain-of-thought improves performance on mathematical "
                "reasoning. Our results demonstrate significant gains across multiple "
                "benchmarks."
            ),
            "categories": ["cs.CL"],
            "authors": [{"name": "I1"}],
            "discovered_at": (now - timedelta(days=5)).isoformat(),
        },
        {
            "id": "p14",
            "title": "Chain of Thought Helps Arithmetic",
            "abstract": (
                "We find that chain-of-thought prompting outperforms direct prompting "
                "on arithmetic reasoning. Results show clear improvement."
            ),
            "categories": ["cs.CL"],
            "authors": [{"name": "I1"}],
            "discovered_at": (now - timedelta(days=6)).isoformat(),
        },
        # Paper with no abstract (edge case)
        {
            "id": "p15",
            "title": "Paper With No Abstract",
            "abstract": None,
            "categories": ["cs.AI"],
            "authors": [],
            "discovered_at": (now - timedelta(days=10)).isoformat(),
        },
    ]
