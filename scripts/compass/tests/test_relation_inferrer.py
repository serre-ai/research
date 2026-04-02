"""Tests for the relation_inferrer module (classify_relation + polarity)."""

from scripts.compass.relation_inferrer import classify_relation, _effective_polarity


class TestEffectivePolarity:
    """Test negation-aware polarity detection."""

    def test_simple_positive(self):
        pos, neg = _effective_polarity("We demonstrate significant improvements.")
        assert pos is True
        assert neg is False

    def test_simple_negative(self):
        pos, neg = _effective_polarity("The method fails on all benchmarks.")
        assert pos is False
        assert neg is True

    def test_negated_positive_cannot(self):
        """'show' is positive but 'cannot solve' makes it negative."""
        pos, neg = _effective_polarity(
            "We show that transformers cannot solve this problem."
        )
        assert pos is False
        assert neg is True

    def test_negated_positive_does_not(self):
        pos, neg = _effective_polarity(
            "We demonstrate that this approach does not improve accuracy."
        )
        assert pos is False
        assert neg is True

    def test_limitation_phrase(self):
        pos, neg = _effective_polarity(
            "We prove the limitations of current approaches."
        )
        assert pos is False
        assert neg is True

    def test_neutral_text(self):
        pos, neg = _effective_polarity("The sky is blue and water is wet.")
        assert pos is False
        assert neg is False

    def test_fails_to(self):
        pos, neg = _effective_polarity(
            "The model fails to achieve competitive results."
        )
        assert pos is False
        assert neg is True


class TestClassifyRelation:
    """Test relation classification between claim pairs."""

    def test_both_positive_supports(self):
        a = "We demonstrate improved performance on reasoning tasks."
        b = "Our method achieves state-of-the-art accuracy."
        assert classify_relation(a, b) == "supports"

    def test_mixed_polarity_contradicts(self):
        a = "Our method outperforms all baselines."
        b = "The approach fails to generalize."
        assert classify_relation(a, b) == "contradicts"

    def test_neutral_related_to(self):
        a = "We study the properties of attention mechanisms."
        b = "The dataset contains 1 million examples."
        assert classify_relation(a, b) == "related_to"

    def test_limitation_vs_positive_contradicts(self):
        """A limitation claim should contradict a positive claim."""
        a = "We show that transformers cannot solve parity."
        b = "Transformers achieve strong performance on all tasks."
        assert classify_relation(a, b) == "contradicts"

    def test_both_negative_not_contradicts(self):
        """Two negative claims should not contradict each other."""
        a = "The method fails on long sequences."
        b = "This approach cannot handle noisy data."
        result = classify_relation(a, b)
        assert result != "contradicts"


class TestEdgeCases:
    def test_empty_strings(self):
        result = classify_relation("", "")
        assert result == "related_to"

    def test_single_word(self):
        result = classify_relation("improve", "fail")
        assert result == "contradicts"
