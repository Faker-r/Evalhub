"""Extended tests for metric_doc_generator: more _describe_sample_level_fn branches and _describe_metric name mappings."""

from unittest.mock import MagicMock

import numpy as np
import pytest

from api.evaluations.eval_pipeline.metric_doc_generator import (
    MetricDescription,
    _describe_corpus_fn,
    _describe_metric,
    _describe_sample_level_fn,
    _describe_sampling_normalization,
    _describe_sampling_score_fn,
)


class TestDescribeSampleLevelFnExtended:
    def test_normalized_multi_choice_probability(self):
        from lighteval.metrics.metrics_sample import NormalizedMultiChoiceProbability
        sample_fn = NormalizedMultiChoiceProbability()
        result = _describe_sample_level_fn(sample_fn, "nmc_prob")
        assert result.source == "NormalizedMultiChoiceProbability"
        assert "probability" in result.measure.lower()

    def test_probability(self):
        from lighteval.metrics.metrics_sample import Probability
        sample_fn = Probability()
        result = _describe_sample_level_fn(sample_fn, "prob")
        assert result.source == "Probability"

    def test_bleu(self):
        from lighteval.metrics.metrics_sample import BLEU
        sample_fn = BLEU(n_gram=4)
        result = _describe_sample_level_fn(sample_fn, "bleu4")
        assert result.source == "BLEU"
        assert "4" in result.measure

    def test_rouge(self):
        from lighteval.metrics.metrics_sample import ROUGE
        sample_fn = ROUGE(methods="rougeL")
        result = _describe_sample_level_fn(sample_fn, "rougeL")
        assert result.source == "ROUGE"
        assert "ROUGE" in result.measure

    def test_rouge_lsum(self):
        from lighteval.metrics.metrics_sample import ROUGE
        sample_fn = ROUGE(methods="rougeLsum")
        result = _describe_sample_level_fn(sample_fn, "rougeLsum")
        assert "Lsum" in result.measure

    def test_string_distance_edit(self):
        from lighteval.metrics.metrics_sample import StringDistance
        sample_fn = StringDistance(metric_types="edit_distance")
        result = _describe_sample_level_fn(sample_fn, "edit_distance")
        assert "edit" in result.measure.lower()

    def test_string_distance_lcp(self):
        from lighteval.metrics.metrics_sample import StringDistance
        sample_fn = StringDistance(metric_types="longest_common_prefix_length")
        result = _describe_sample_level_fn(sample_fn, "longest_common_prefix_length")
        assert "prefix" in result.measure.lower()

    def test_string_distance_normalized(self):
        from lighteval.metrics.metrics_sample import StringDistance
        sample_fn = StringDistance(metric_types="edit_similarity")
        result = _describe_sample_level_fn(sample_fn, "normalized_edit_similarity")
        assert "similarity" in result.measure.lower()

    def test_sampling_metric_with_type_exact_match(self):
        from lighteval.metrics.metrics_sample import SamplingMetric
        sample_fn = SamplingMetric(
            strip_strings=True,
            normalize=None,
        )
        sample_fn.type_exact_match = "prefix"
        result = _describe_sampling_score_fn(sample_fn)
        assert "prefix" in result

    def test_sampling_metric_full_exact_match(self):
        from lighteval.metrics.metrics_sample import SamplingMetric
        sample_fn = SamplingMetric(
            strip_strings=True,
            normalize=None,
        )
        sample_fn.type_exact_match = "full"
        result = _describe_sampling_score_fn(sample_fn)
        assert "full" in result

    def test_sampling_normalization_with_strip_and_normalize(self):
        from lighteval.metrics.metrics_sample import SamplingMetric
        sample_fn = SamplingMetric(
            strip_strings=True,
            normalize=MagicMock(__name__="helm_normalizer"),
        )
        result = _describe_sampling_normalization(sample_fn)
        assert "strip" in result
        assert "lowercase" in result

    def test_sampling_normalization_empty(self):
        from lighteval.metrics.metrics_sample import SamplingMetric
        sample_fn = SamplingMetric(
            strip_strings=False,
            normalize=None,
        )
        result = _describe_sampling_normalization(sample_fn)
        assert "no string" in result


class TestDescribeMetricNameMappings:
    def _make_metric_and_describe(self, metric_name, corpus_fn=np.mean):
        metric = MagicMock()
        metric.sample_level_fn = MagicMock()
        result = _describe_metric(metric, metric_name, corpus_fn)
        return result

    def test_bleu_name(self):
        result = self._make_metric_and_describe("bleu")
        assert "Corpus BLEU" in result.measure

    def test_chrf_name(self):
        result = self._make_metric_and_describe("chrf")
        assert "chrF" in result.measure

    def test_chrf_plus_name(self):
        result = self._make_metric_and_describe("chrf++")
        assert "chrF++" in result.measure

    def test_ter_name(self):
        result = self._make_metric_and_describe("ter")
        assert "TER" in result.measure

    def test_summac_name(self):
        result = self._make_metric_and_describe("summac")
        assert "SummaCZS" in result.measure

    def test_word_perplexity_name(self):
        result = self._make_metric_and_describe("word_perplexity")
        assert "Word-level" in result.measure

    def test_byte_perplexity_name(self):
        result = self._make_metric_and_describe("byte_perplexity")
        assert "Byte-level" in result.measure

    def test_bits_per_byte_name(self):
        result = self._make_metric_and_describe("bits_per_byte")
        assert "Bits per byte" in result.measure

    def test_ppl_name(self):
        result = self._make_metric_and_describe("ppl")
        assert "Perplexity" in result.measure

    def test_loglikelihood_f1_name(self):
        result = self._make_metric_and_describe("loglikelihood_f1")
        assert "Classification F1" in result.measure

    def test_mcc_name(self):
        result = self._make_metric_and_describe("mcc")
        assert "Matthews" in result.measure

    def test_mf1_name(self):
        result = self._make_metric_and_describe("mf1")
        assert "Multi-class F1" in result.measure

    def test_accuracy_name(self):
        result = self._make_metric_and_describe("accuracy")
        assert "accuracy" in result.measure.lower()

    def test_confidence_half_width_name(self):
        result = self._make_metric_and_describe("confidence_half_width")
        assert "confidence" in result.measure.lower()

    def test_calibration_error_name(self):
        result = self._make_metric_and_describe("calibration_error")
        assert "Calibration" in result.measure

    def test_exact_match_name(self):
        result = self._make_metric_and_describe("exact_match")
        assert "Exact" in result.measure

    def test_unknown_prediction_name(self):
        result = self._make_metric_and_describe("unknown_prediction")
        assert "failure" in result.measure.lower()

    def test_total_samples_name(self):
        result = self._make_metric_and_describe("total_samples")
        assert "Total" in result.measure

    def test_verifiable_reward_name(self):
        result = self._make_metric_and_describe("verifiable_reward")
        assert "Verifiable" in result.measure

    def test_irt_name(self):
        result = self._make_metric_and_describe("irt")
        assert "IRT" in result.measure

    def test_pirt_name(self):
        result = self._make_metric_and_describe("pirt")
        assert "PIRT" in result.measure

    def test_gpirt_name(self):
        result = self._make_metric_and_describe("gpirt")
        assert "GPIRT" in result.measure

    def test_llm_judge_mixeval_name(self):
        result = self._make_metric_and_describe("llm_judge_mixeval_hard")
        assert "MixEval" in result.measure

    def test_judge_score_turn_1(self):
        result = self._make_metric_and_describe("judge_score_turn_1")
        assert "MT-Bench" in result.measure

    def test_judge_score_turn_2(self):
        result = self._make_metric_and_describe("judge_score_turn_2")
        assert "MT-Bench" in result.measure

    def test_pass_at_k_name(self):
        result = self._make_metric_and_describe("pass@k")
        assert "Pass@k" in result.measure

    def test_avg_at_n_name(self):
        result = self._make_metric_and_describe("avg@n")
        assert "Average" in result.measure

    def test_maj_at_n_name(self):
        result = self._make_metric_and_describe("maj@n")
        assert "Majority" in result.measure

    def test_em_colon_name(self):
        result = self._make_metric_and_describe("em:strict")
        assert "parameterized" in result.measure.lower()

    def test_em_name(self):
        result = self._make_metric_and_describe("em")
        assert "Exact match" in result.measure

    def test_f1_name_with_corpus_f1(self):
        from lighteval.metrics.metrics_corpus import CorpusLevelF1Score
        corpus_fn = CorpusLevelF1Score(average="micro", num_classes=2)
        result = self._make_metric_and_describe("f1", corpus_fn)
        assert "Classification F1" in result.measure

    def test_f1_name_without_corpus_f1(self):
        result = self._make_metric_and_describe("f1", np.mean)
        assert "F1 score" in result.measure

    def test_unmatched_name(self):
        result = self._make_metric_and_describe("some_random_metric")
        assert isinstance(result, MetricDescription)


class TestDescribeSampleLevelFnMocked:
    """Test branches that require mocked instances due to complex init requirements."""

    def test_bert_score_f1(self):
        from lighteval.metrics.metrics_sample import BertScore
        sample_fn = MagicMock(spec=BertScore)
        result = _describe_sample_level_fn(sample_fn, "bertscore-F")
        assert result.source == "BertScore"
        assert "F1" in result.measure

    def test_bert_score_precision(self):
        from lighteval.metrics.metrics_sample import BertScore
        sample_fn = MagicMock(spec=BertScore)
        result = _describe_sample_level_fn(sample_fn, "bertscore-P")
        assert "precision" in result.measure.lower()

    def test_bert_score_recall(self):
        from lighteval.metrics.metrics_sample import BertScore
        sample_fn = MagicMock(spec=BertScore)
        result = _describe_sample_level_fn(sample_fn, "bertscore-R")
        assert "recall" in result.measure.lower()

    def test_extractiveness_coverage(self):
        from lighteval.metrics.metrics_sample import Extractiveness
        sample_fn = MagicMock(spec=Extractiveness)
        result = _describe_sample_level_fn(sample_fn, "summarization_coverage")
        assert "coverage" in result.measure.lower()

    def test_extractiveness_density(self):
        from lighteval.metrics.metrics_sample import Extractiveness
        sample_fn = MagicMock(spec=Extractiveness)
        result = _describe_sample_level_fn(sample_fn, "summarization_density")
        assert "density" in result.measure.lower()

    def test_extractiveness_compression(self):
        from lighteval.metrics.metrics_sample import Extractiveness
        sample_fn = MagicMock(spec=Extractiveness)
        result = _describe_sample_level_fn(sample_fn, "compression")
        assert "Compression" in result.measure

    def test_faithfulness(self):
        from lighteval.metrics.metrics_sample import Faithfulness
        sample_fn = MagicMock(spec=Faithfulness)
        result = _describe_sample_level_fn(sample_fn, "summac")
        assert result.source == "Faithfulness"

    def test_bleurt(self):
        from lighteval.metrics.metrics_sample import BLEURT
        sample_fn = MagicMock(spec=BLEURT)
        result = _describe_sample_level_fn(sample_fn, "bleurt")
        assert result.source == "BLEURT"

    def test_drop_metrics_em(self):
        from lighteval.metrics.harness_compatibility.drop import DropMetrics
        sample_fn = MagicMock(spec=DropMetrics)
        result = _describe_sample_level_fn(sample_fn, "em")
        assert result.source == "DropMetrics"
        assert "exact match" in result.measure.lower()

    def test_drop_metrics_f1(self):
        from lighteval.metrics.harness_compatibility.drop import DropMetrics
        sample_fn = MagicMock(spec=DropMetrics)
        result = _describe_sample_level_fn(sample_fn, "f1")
        assert "F1" in result.measure

    def test_truthfulqa_mc1(self):
        from lighteval.metrics.harness_compatibility.truthful_qa import TruthfulqaMCMetrics
        sample_fn = MagicMock(spec=TruthfulqaMCMetrics)
        result = _describe_sample_level_fn(sample_fn, "truthfulqa_mc1")
        assert "MC1" in result.measure

    def test_truthfulqa_mc2(self):
        from lighteval.metrics.harness_compatibility.truthful_qa import TruthfulqaMCMetrics
        sample_fn = MagicMock(spec=TruthfulqaMCMetrics)
        result = _describe_sample_level_fn(sample_fn, "truthfulqa_mc2")
        assert "MC2" in result.measure

    def test_multilingual_extractive_match(self):
        from lighteval.metrics.dynamic_metrics import MultilingualExtractiveMatchMetric
        sample_fn = MagicMock(spec=MultilingualExtractiveMatchMetric)
        from lighteval.metrics.utils.extractive_match_utils import ExprExtractionConfig
        sample_fn.pred_extraction_target = [ExprExtractionConfig()]
        result = _describe_sample_level_fn(sample_fn, "extractive_match")
        assert result.source == "MultilingualExtractiveMatchMetric"

    def test_judge_llm_simpleqa(self):
        from lighteval.metrics.metrics_sample import JudgeLLMSimpleQA
        sample_fn = MagicMock(spec=JudgeLLMSimpleQA)
        result = _describe_sample_level_fn(sample_fn, "simpleqa")
        assert result.source == "JudgeLLMSimpleQA"

    def test_judge_llm_mtbench(self):
        from lighteval.metrics.metrics_sample import JudgeLLMMTBench
        sample_fn = MagicMock(spec=JudgeLLMMTBench)
        result = _describe_sample_level_fn(sample_fn, "mtbench")
        assert result.source == "JudgeLLMMTBench"

    def test_judge_llm_mixeval(self):
        from lighteval.metrics.metrics_sample import JudgeLLMMixEval
        sample_fn = MagicMock(spec=JudgeLLMMixEval)
        result = _describe_sample_level_fn(sample_fn, "mixeval")
        assert result.source == "JudgeLLMMixEval"

    def test_judge_llm_generic(self):
        from lighteval.metrics.metrics_sample import JudgeLLM
        sample_fn = MagicMock(spec=JudgeLLM)
        result = _describe_sample_level_fn(sample_fn, "judge")
        assert result.source == "JudgeLLM"

    def test_class_name_ifbench(self):
        sample_fn = MagicMock()
        sample_fn.__class__.__name__ = "IFBench"
        result = _describe_sample_level_fn(sample_fn, "ifbench")
        assert "Instruction-following" in result.measure

    def test_class_name_ifeval(self):
        sample_fn = MagicMock()
        sample_fn.__class__.__name__ = "IFEvalMetrics"
        result = _describe_sample_level_fn(sample_fn, "ifeval")
        assert "Instruction-following" in result.measure

    def test_class_name_verifiable_reward(self):
        sample_fn = MagicMock()
        sample_fn.__class__.__name__ = "VerifiableRewardMetric"
        result = _describe_sample_level_fn(sample_fn, "vr")
        assert "Verifiable" in result.measure

    def test_class_name_codegen(self):
        sample_fn = MagicMock()
        sample_fn.__class__.__name__ = "CodegenMetric"
        result = _describe_sample_level_fn(sample_fn, "codegen")
        assert "Code" in result.measure

    def test_class_name_emotion(self):
        sample_fn = MagicMock()
        sample_fn.__class__.__name__ = "EmotionClassificationMetric"
        result = _describe_sample_level_fn(sample_fn, "emotion")
        assert "Emotion" in result.measure

    def test_class_name_tiny_corpus(self):
        sample_fn = MagicMock()
        sample_fn.__class__.__name__ = "TinyCorpusAggregator"
        result = _describe_sample_level_fn(sample_fn, "tiny")
        assert "TinyBenchmarks" in result.measure

    def test_class_name_judge_hle(self):
        sample_fn = MagicMock()
        sample_fn.__class__.__name__ = "JudgeLLMHLE"
        result = _describe_sample_level_fn(sample_fn, "hle")
        assert "HLE" in result.measure

    def test_sampling_metric_suffix_match(self):
        from lighteval.metrics.metrics_sample import SamplingMetric
        sample_fn = SamplingMetric(strip_strings=False, normalize=None)
        sample_fn.type_exact_match = "suffix"
        result = _describe_sampling_score_fn(sample_fn)
        assert "suffix" in result

    def test_sampling_metric_custom_score_fn(self):
        from lighteval.metrics.metrics_sample import SamplingMetric
        sample_fn = SamplingMetric(strip_strings=False, normalize=None)
        sample_fn.type_exact_match = None
        result = _describe_sampling_score_fn(sample_fn)
        assert "custom" in result.lower()


class TestDescribeCorpusFnExtended:
    def test_corpus_level_perplexity_weighted(self):
        from lighteval.metrics.metrics_corpus import CorpusLevelPerplexityMetric
        corpus_fn = CorpusLevelPerplexityMetric(metric_type="weighted_perplexity")
        result = _describe_corpus_fn(corpus_fn, "weighted_ppl")
        assert "weighted" in result.lower()

    def test_corpus_level_perplexity_bits(self):
        from lighteval.metrics.metrics_corpus import CorpusLevelPerplexityMetric
        corpus_fn = CorpusLevelPerplexityMetric(metric_type="bits_per_byte")
        result = _describe_corpus_fn(corpus_fn, "bpb")
        assert "bits per byte" in result.lower()

    def test_corpus_level_perplexity_standard(self):
        from lighteval.metrics.metrics_corpus import CorpusLevelPerplexityMetric
        corpus_fn = CorpusLevelPerplexityMetric(metric_type="perplexity")
        result = _describe_corpus_fn(corpus_fn, "ppl")
        assert "logprob" in result.lower()

    def test_matthews_corr(self):
        from lighteval.metrics.metrics_corpus import MatthewsCorrCoef
        corpus_fn = MatthewsCorrCoef()
        result = _describe_corpus_fn(corpus_fn, "mcc")
        assert "Matthews" in result

    def test_generic_corpus_level_computation(self):
        from lighteval.metrics.metrics_corpus import CorpusLevelComputation
        corpus_fn = MagicMock(spec=CorpusLevelComputation)
        result = _describe_corpus_fn(corpus_fn, "x")
        assert "corpus" in result.lower()
