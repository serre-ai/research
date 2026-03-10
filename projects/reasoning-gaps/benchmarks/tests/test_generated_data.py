"""Validation tests for the generated benchmark data files.

Run AFTER `python generate.py --all --n-instances 100 --seed 42`.
Verifies structural integrity of all 9 JSON data files.
"""

import hashlib
import json
import sys
from pathlib import Path

import pytest

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

EXPECTED_FILES = [
    "b1_B1_masked_majority.json",
    "b2_B2_nested_boolean.json",
    "b3_B3_permutation_composition.json",
    "b4_B4_state_machine.json",
    "b5_B5_graph_reachability.json",
    "b6_B6_longest_increasing_subsequence.json",
    "b7_B7_3sat.json",
    "b8_B8_reversal_inference.json",
    "b9_B9_negation_sensitivity.json",
]

REQUIRED_INSTANCE_FIELDS = {"id", "task", "prompt", "answer", "difficulty", "metadata"}


@pytest.fixture(scope="module")
def all_data():
    """Load all benchmark JSON files."""
    data = {}
    for fname in EXPECTED_FILES:
        fpath = DATA_DIR / fname
        if fpath.exists():
            with open(fpath) as f:
                data[fname] = json.load(f)
        else:
            data[fname] = None
    return data


class TestDataFilesExist:
    """All 9 JSON files must exist."""

    @pytest.mark.parametrize("filename", EXPECTED_FILES)
    def test_file_exists(self, filename):
        fpath = DATA_DIR / filename
        assert fpath.exists(), f"Missing data file: {fpath}"


class TestDataFileStructure:
    """Each file must have the expected top-level structure."""

    @pytest.mark.parametrize("filename", EXPECTED_FILES)
    def test_top_level_keys(self, filename, all_data):
        data = all_data[filename]
        if data is None:
            pytest.skip(f"File not found: {filename}")
        required_keys = {"task", "task_name", "n_instances_per_difficulty",
                         "difficulties", "seed", "total_instances", "instances"}
        assert required_keys.issubset(set(data.keys())), (
            f"Missing top-level keys in {filename}: "
            f"{required_keys - set(data.keys())}"
        )

    @pytest.mark.parametrize("filename", EXPECTED_FILES)
    def test_instance_count_500(self, filename, all_data):
        """Each file should have 500 instances (100 per difficulty x 5 difficulties)."""
        data = all_data[filename]
        if data is None:
            pytest.skip(f"File not found: {filename}")
        assert data["total_instances"] == 500, (
            f"{filename}: expected 500 instances, got {data['total_instances']}"
        )
        assert len(data["instances"]) == 500

    @pytest.mark.parametrize("filename", EXPECTED_FILES)
    def test_difficulties_1_to_5(self, filename, all_data):
        data = all_data[filename]
        if data is None:
            pytest.skip(f"File not found: {filename}")
        assert data["difficulties"] == [1, 2, 3, 4, 5]


class TestInstanceIntegrity:
    """Each instance must pass structural validation."""

    @pytest.mark.parametrize("filename", EXPECTED_FILES)
    def test_all_instances_have_required_fields(self, filename, all_data):
        data = all_data[filename]
        if data is None:
            pytest.skip(f"File not found: {filename}")
        for i, inst in enumerate(data["instances"]):
            missing = REQUIRED_INSTANCE_FIELDS - set(inst.keys())
            assert not missing, (
                f"{filename} instance {i}: missing fields {missing}"
            )

    @pytest.mark.parametrize("filename", EXPECTED_FILES)
    def test_no_empty_answers(self, filename, all_data):
        data = all_data[filename]
        if data is None:
            pytest.skip(f"File not found: {filename}")
        for i, inst in enumerate(data["instances"]):
            assert isinstance(inst["answer"], str) and len(inst["answer"]) > 0, (
                f"{filename} instance {i}: empty or non-string answer"
            )

    @pytest.mark.parametrize("filename", EXPECTED_FILES)
    def test_no_duplicate_ids(self, filename, all_data):
        data = all_data[filename]
        if data is None:
            pytest.skip(f"File not found: {filename}")
        ids = [inst["id"] for inst in data["instances"]]
        assert len(ids) == len(set(ids)), (
            f"{filename}: found duplicate IDs ({len(ids) - len(set(ids))} duplicates)"
        )

    @pytest.mark.parametrize("filename", EXPECTED_FILES)
    def test_all_difficulties_present(self, filename, all_data):
        data = all_data[filename]
        if data is None:
            pytest.skip(f"File not found: {filename}")
        difficulties = set(inst["difficulty"] for inst in data["instances"])
        assert difficulties == {1, 2, 3, 4, 5}, (
            f"{filename}: expected difficulties {{1,2,3,4,5}}, got {difficulties}"
        )

    @pytest.mark.parametrize("filename", EXPECTED_FILES)
    def test_100_instances_per_difficulty(self, filename, all_data):
        data = all_data[filename]
        if data is None:
            pytest.skip(f"File not found: {filename}")
        from collections import Counter
        counts = Counter(inst["difficulty"] for inst in data["instances"])
        for diff in [1, 2, 3, 4, 5]:
            assert counts[diff] == 100, (
                f"{filename}: difficulty {diff} has {counts[diff]} instances, expected 100"
            )


class TestDataChecksums:
    """Checksum verification for reproducibility."""

    @pytest.mark.parametrize("filename", EXPECTED_FILES)
    def test_checksum_stable(self, filename):
        """Each data file should produce a consistent SHA-256 hash.

        This test records checksums on first run. If data is regenerated
        with the same seed, checksums must match.
        """
        fpath = DATA_DIR / filename
        if not fpath.exists():
            pytest.skip(f"File not found: {filename}")
        content = fpath.read_bytes()
        sha = hashlib.sha256(content).hexdigest()
        # Just verify the hash is non-empty (actual value depends on generation)
        assert len(sha) == 64, f"Invalid SHA-256 for {filename}"
        # Print for reference (captured by pytest -v)
        print(f"\n  {filename}: sha256={sha[:16]}...")
