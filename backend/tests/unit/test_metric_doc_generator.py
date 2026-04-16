"""Unit tests for MetricDocGenerator and its helper functions."""

import types
from dataclasses import dataclass
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from api.evaluations.eval_pipeline.metric_doc_generator import (
    MetricDescription,
    MetricDocGenerator,
    _describe_corpus_fn,
    _describe_extraction_targets,
    _describe_logprob_normalization,
    _describe_normalizer,
    _describe_sample_level_fn,
    _get_corpus_fn,
    get_metric_names,
)


# ==================== _describe_normalizer ====================


class TestDescribeNormalizer:
    def test_none(self):
        assert _describe_normalizer(None) == "no text normalization"

    def test_helm_normalizer(self):
        fn = MagicMock(__name__="helm_normalizer")
        result = _describe_normalizer(fn)
        assert "lowercase" in result

    def test_harness_triviaqa(self):
        fn = MagicMock(__name__="harness_triviaqa_normalizer")
        assert "TriviaQA" in _describe_normalizer(fn)

    def test_bigbench(self):
        fn = MagicMock(__name__="bigbench_normalizer")
        assert "BigBench" in _describe_normalizer(fn)

    def test_remove_braces(self):
        fn = MagicMock(__name__="remove_braces")
        assert "braces" in _describe_normalizer(fn)

    def test_remove_braces_and_strip(self):
        fn = MagicMock(__name__="remove_braces_and_strip")
        assert "strip" in _describe_normalizer(fn)

    def test_math_normalizer(self):
        fn = MagicMock(__name__="math_normalizer")
        assert "math" in _describe_normalizer(fn).lower()

    def test_gsm8k_normalizer(self):
        fn = MagicMock(__name__="gsm8k_normalizer")
        assert "GSM8K" in _describe_normalizer(fn)

    def test_custom_named(self):
        fn = MagicMock(__name__="my_custom_fn")
        result = _describe_normalizer(fn)
        assert "custom" in result.lower()
        assert "my_custom_fn" in result

    def test_custom_unnamed(self):
        fn = MagicMock(spec=[])
        result = _describe_normalizer(fn)
        assert result == "custom normalization"


# ==================== _describe_logprob_normalization ====================


class TestDescribeLogprobNormalization:
    def test_none(self):
        assert _describe_logprob_normalization(None) == "no logprob normalization"

    def test_char_norm_ignore_space(self):
        from lighteval.metrics.normalizations import LogProbCharNorm
        norm = LogProbCharNorm(ignore_first_space=True)
        result = _describe_logprob_normalization(norm)
        assert "character length" in result
        assert "ignoring" in result

    def test_char_norm_no_ignore(self):
        from lighteval.metrics.normalizations import LogProbCharNorm
        norm = LogProbCharNorm(ignore_first_space=False)
        result = _describe_logprob_normalization(norm)
        assert "character length" in result
        assert "ignoring" not in result

    def test_token_norm(self):
        from lighteval.metrics.normalizations import LogProbTokenNorm
        norm = LogProbTokenNorm()
        assert "token length" in _describe_logprob_normalization(norm)

    def test_pmi_norm(self):
        from lighteval.metrics.normalizations import LogProbPMINorm
        norm = LogProbPMINorm()
        assert "PMI" in _describe_logprob_normalization(norm)

    def test_custom_normalization(self):
        class MyNorm:
            pass
        norm = MyNorm()
        result = _describe_logprob_normalization(norm)
        assert "custom" in result.lower()
        assert "MyNorm" in result


# ==================== _describe_extraction_targets ====================


class TestDescribeExtractionTargets:
    def test_empty(self):
        result = _describe_extraction_targets([])
        assert "task-specific" in result

    def test_expr_config(self):
        from lighteval.metrics.utils.extractive_match_utils import ExprExtractionConfig
        target = ExprExtractionConfig()
        result = _describe_extraction_targets([target])
        assert "numbers" in result or "math" in result

    def test_latex_config(self):
        from lighteval.metrics.utils.extractive_match_utils import LatexExtractionConfig
        target = LatexExtractionConfig()
        result = _describe_extraction_targets([target])
        assert "LaTeX" in result

    def test_indices_config(self):
        from lighteval.metrics.utils.extractive_match_utils import IndicesExtractionConfig
        target = IndicesExtractionConfig(prefix_for_extraction="Letters")
        result = _describe_extraction_targets([target])
        assert "indices" in result

    def test_mixed(self):
        from lighteval.metrics.utils.extractive_match_utils import (
            ExprExtractionConfig,
            LatexExtractionConfig,
        )
        result = _describe_extraction_targets([ExprExtractionConfig(), LatexExtractionConfig()])
        assert "," in result


# ==================== _describe_corpus_fn ====================


class TestDescribeCorpusFn:
    def test_np_mean(self):
        result = _describe_corpus_fn(np.mean, "metric")
        assert "Average" in result

    def test_np_sum(self):
        result = _describe_corpus_fn(np.sum, "metric")
        assert "Sum" in result

    def test_builtin_max(self):
        result = _describe_corpus_fn(max, "metric")
        assert "maximum" in result

    def test_builtin_min(self):
        result = _describe_corpus_fn(min, "metric")
        assert "minimum" in result

    def test_named_callable(self):
        def my_agg(x):
            return x
        result = _describe_corpus_fn(my_agg, "metric")
        assert "my_agg" in result

    def test_agg_inst_level_acc(self):
        fn = MagicMock(__name__="agg_inst_level_acc")
        fn.__call__ = MagicMock()
        result = _describe_corpus_fn(fn, "metric")
        assert "Flatten" in result

    def test_mean_dv_5(self):
        fn = MagicMock(__name__="mean_dv_5")
        fn.__call__ = MagicMock()
        result = _describe_corpus_fn(fn, "metric")
        assert "divide by 5" in result

    def test_has_compute_corpus(self):
        class CorpusObj:
            def compute_corpus(self):
                pass
        obj = CorpusObj()
        result = _describe_corpus_fn(obj, "metric")
        assert "corpus" in result.lower()

    def test_fallback(self):
        result = _describe_corpus_fn(42, "metric")
        assert "Custom" in result


# ==================== get_metric_names ====================


class TestGetMetricNames:
    def test_string_name(self):
        metric = MagicMock()
        metric.metric_name = "accuracy"
        assert get_metric_names(metric) == ["accuracy"]

    def test_list_names(self):
        metric = MagicMock()
        metric.metric_name = ["accuracy", "f1"]
        assert get_metric_names(metric) == ["accuracy", "f1"]


# ==================== _get_corpus_fn ====================


class TestGetCorpusFn:
    def test_dict_with_matching_key(self):
        metric = MagicMock()
        metric.corpus_level_fn = {"acc": np.mean, "f1": np.sum}
        assert _get_corpus_fn(metric, "acc") is np.mean

    def test_dict_without_matching_key(self):
        metric = MagicMock()
        metric.corpus_level_fn = {"acc": np.mean}
        result = _get_corpus_fn(metric, "nonexistent")
        assert result is np.mean

    def test_non_dict(self):
        metric = MagicMock()
        metric.corpus_level_fn = np.mean
        assert _get_corpus_fn(metric, "any") is np.mean


# ==================== MetricDescription ====================


class TestMetricDescription:
    def test_frozen_dataclass(self):
        desc = MetricDescription(
            measure="Exact match",
            sample_level="Compare pred to gold",
            corpus_level="Average",
            source="ExactMatches",
        )
        assert desc.measure == "Exact match"
        assert desc.source == "ExactMatches"
        with pytest.raises(AttributeError):
            desc.measure = "changed"


# ==================== _describe_sample_level_fn ====================


class TestDescribeSampleLevelFn:
    def test_exact_matches(self):
        from lighteval.metrics.metrics_sample import ExactMatches
        sample_fn = ExactMatches()
        result = _describe_sample_level_fn(sample_fn, "exact_match")
        assert result.source == "ExactMatches"
        assert "match" in result.measure.lower()

    def test_f1_score(self):
        from lighteval.metrics.metrics_sample import F1_score
        sample_fn = F1_score()
        result = _describe_sample_level_fn(sample_fn, "f1")
        assert result.source == "F1_score"
        assert "F1" in result.measure

    def test_loglikelihood_acc(self):
        from lighteval.metrics.metrics_sample import LoglikelihoodAcc
        sample_fn = LoglikelihoodAcc()
        result = _describe_sample_level_fn(sample_fn, "acc")
        assert result.source == "LoglikelihoodAcc"

    def test_recall(self):
        from lighteval.metrics.metrics_sample import Recall
        sample_fn = Recall(k=5)
        result = _describe_sample_level_fn(sample_fn, "recall@5")
        assert result.source == "Recall"

    def test_mrr(self):
        from lighteval.metrics.metrics_sample import MRR
        sample_fn = MRR()
        result = _describe_sample_level_fn(sample_fn, "mrr")
        assert "reciprocal rank" in result.measure.lower()

    def test_acc_gold_likelihood(self):
        from lighteval.metrics.metrics_sample import AccGoldLikelihood
        sample_fn = AccGoldLikelihood()
        result = _describe_sample_level_fn(sample_fn, "acc")
        assert result.source == "AccGoldLikelihood"

    def test_fallback(self):
        class UnknownSampleFn:
            pass
        result = _describe_sample_level_fn(UnknownSampleFn(), "custom")
        assert result.source == "UnknownSampleFn"
        assert "Custom" in result.measure

    def test_generative_preparator(self):
        from lighteval.metrics.sample_preparator import GenerativePreparator
        sample_fn = GenerativePreparator()
        result = _describe_sample_level_fn(sample_fn, "gen")
        assert result.source == "GenerativePreparator"

    def test_loglikelihood_preparator(self):
        from lighteval.metrics.sample_preparator import LoglikelihoodPreparator
        sample_fn = LoglikelihoodPreparator()
        result = _describe_sample_level_fn(sample_fn, "ll")
        assert result.source == "LoglikelihoodPreparator"

    def test_perplexity_preparator(self):
        from lighteval.metrics.sample_preparator import PerplexityPreparator
        sample_fn = PerplexityPreparator(units_type="words")
        result = _describe_sample_level_fn(sample_fn, "ppl")
        assert result.source == "PerplexityPreparator"

    def test_target_perplexity_preparator(self):
        from lighteval.metrics.sample_preparator import TargetPerplexityPreparator
        sample_fn = TargetPerplexityPreparator(units_type="words")
        result = _describe_sample_level_fn(sample_fn, "tppl")
        assert result.source == "TargetPerplexityPreparator"


# ==================== MetricDocGenerator ====================


class TestMetricDocGenerator:
    def test_generate_metric_docs(self):
        metric = MagicMock()
        metric.metric_name = "exact_match"
        metric.corpus_level_fn = np.mean
        metric.sample_level_fn = MagicMock()

        result = MetricDocGenerator.generate_metric_docs([metric])
        assert "exact_match" in result
        assert len(result["exact_match"]) == 1

    def test_multiple_metrics(self):
        metric1 = MagicMock()
        metric1.metric_name = "accuracy"
        metric1.corpus_level_fn = np.mean
        metric1.sample_level_fn = MagicMock()

        metric2 = MagicMock()
        metric2.metric_name = "f1"
        metric2.corpus_level_fn = np.mean
        metric2.sample_level_fn = MagicMock()

        result = MetricDocGenerator.generate_metric_docs([metric1, metric2])
        assert "accuracy" in result
        assert "f1" in result

    def test_multi_name_metric(self):
        metric = MagicMock()
        metric.metric_name = ["acc", "f1"]
        metric.corpus_level_fn = {"acc": np.mean, "f1": np.sum}
        metric.sample_level_fn = MagicMock()

        result = MetricDocGenerator.generate_metric_docs([metric])
        assert "acc" in result
        assert "f1" in result
