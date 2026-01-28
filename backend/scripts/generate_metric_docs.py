#!/usr/bin/env python3
import json
import re
import types
from dataclasses import dataclass
from typing import Any

import numpy as np

from lighteval.metrics.dynamic_metrics import MultilingualExtractiveMatchMetric
from lighteval.metrics.harness_compatibility.drop import DropMetrics
from lighteval.metrics.harness_compatibility.truthful_qa import TruthfulqaMCMetrics
from lighteval.metrics.metrics_corpus import (
    CorpusLevelComputation,
    CorpusLevelF1Score,
    CorpusLevelPerplexityMetric,
    CorpusLevelTranslationMetric,
    MatthewsCorrCoef,
)
from lighteval.metrics.metrics_sample import (
    AccGoldLikelihood,
    AvgAtN,
    BertScore,
    BLEU,
    BLEURT,
    ExactMatches,
    Extractiveness,
    Faithfulness,
    F1_score,
    GPassAtK,
    JudgeLLM,
    JudgeLLMMixEval,
    JudgeLLMMTBench,
    JudgeLLMSimpleQA,
    LoglikelihoodAcc,
    MRR,
    MajAtN,
    NormalizedMultiChoiceProbability,
    PassAtK,
    Probability,
    Recall,
    ROUGE,
    SampleLevelComputation,
    SamplingMetric,
    StringDistance,
)
from lighteval.metrics.normalizations import (
    LogProbCharNorm,
    LogProbPMINorm,
    LogProbTokenNorm,
)
from lighteval.metrics.sample_preparator import (
    GenerativePreparator,
    LoglikelihoodPreparator,
    PerplexityPreparator,
    TargetPerplexityPreparator,
)
from lighteval.metrics.utils.extractive_match_utils import (
    ExprExtractionConfig,
    IndicesExtractionConfig,
    LatexExtractionConfig,
)
from lighteval.metrics.utils.metric_utils import MetricGrouping
from lighteval.tasks.registry import Registry


@dataclass(frozen=True)
class MetricDescription:
    measure: str
    sample_level: str
    corpus_level: str
    source: str


def _describe_normalizer(fn: Any) -> str:
    if fn is None:
        return "no text normalization"
    name = getattr(fn, "__name__", "")
    if name == "helm_normalizer":
        return (
            "lowercase, remove punctuation/articles, normalize whitespace and numbers"
        )
    if name == "harness_triviaqa_normalizer":
        return "lowercase and remove punctuation (TriviaQA normalization)"
    if name == "bigbench_normalizer":
        return "BigBench normalization (replace ' . ' with '.\\n')"
    if name == "remove_braces":
        return "strip leading/trailing braces"
    if name == "remove_braces_and_strip":
        return "strip whitespace and leading/trailing braces"
    if name == "math_normalizer":
        return "math normalization (LaTeX cleanup, boxed extraction, fraction/number normalization)"
    if name == "gsm8k_normalizer":
        return "GSM8K normalization (extract final numeric answer)"
    if name:
        return f"custom normalization ({name})"
    return "custom normalization"


def _describe_logprob_normalization(norm: Any) -> str:
    if norm is None:
        return "no logprob normalization"
    if isinstance(norm, LogProbCharNorm):
        if norm.ignore_first_space:
            return "divide logprobs by character length (ignoring leading space)"
        return "divide logprobs by character length"
    if isinstance(norm, LogProbTokenNorm):
        return "divide logprobs by token length"
    if isinstance(norm, LogProbPMINorm):
        return "PMI normalization (conditioned logprob minus unconditioned logprob)"
    name = getattr(norm, "__class__", type(norm)).__name__
    return f"custom normalization ({name})"


def _describe_extraction_targets(targets: list[Any] | tuple[Any, ...]) -> str:
    parts = []
    for target in targets:
        if isinstance(target, ExprExtractionConfig):
            parts.append("numbers and math expressions")
        elif isinstance(target, LatexExtractionConfig):
            parts.append("LaTeX math (including boxed expressions)")
        elif isinstance(target, IndicesExtractionConfig):
            parts.append("multiple-choice indices")
    if not parts:
        return "answers extracted via task-specific regexes"
    return ", ".join(sorted(set(parts)))


def _describe_sampling_score_fn(metric: SamplingMetric) -> str:
    if getattr(metric, "type_exact_match", None):
        match_type = metric.type_exact_match
        if match_type == "prefix":
            return "exact match on prefix"
        if match_type == "suffix":
            return "exact match on suffix"
        return "exact match on full string"

    score_fn = getattr(metric, "compute_score", None)
    if isinstance(score_fn, types.MethodType) and isinstance(
        score_fn.__self__, SampleLevelComputation
    ):
        sample_desc = _describe_sample_level_fn(score_fn.__self__, "")
        return sample_desc.measure

    return "custom scoring function"


def _describe_sampling_normalization(metric: SamplingMetric) -> str:
    parts = []
    if metric.strip_strings:
        parts.append("strip whitespace")
    if metric.normalize is not None:
        parts.append(_describe_normalizer(metric.normalize))
    if not parts:
        return "no string preprocessing"
    return "; ".join(parts)


def _describe_sample_level_fn(sample_fn: Any, metric_name: str) -> MetricDescription:
    # Exact match
    if isinstance(sample_fn, ExactMatches):
        normalization = _describe_normalizer(sample_fn.normalize_gold)
        match_type = sample_fn.type_exact_match
        measure = "Exact match between prediction and reference"
        if match_type != "full":
            measure += f" ({match_type} match)"
        sample_level = (
            "Compare each prediction to each gold after optional stripping and normalization; "
            f"compute a binary match (type: {match_type}) and aggregate with {sample_fn.aggregation_function.__name__}. "
            f"Normalization: {normalization}."
        )
        corpus_level = "Aggregate sample scores with the configured corpus function."
        return MetricDescription(measure, sample_level, corpus_level, "ExactMatches")

    if isinstance(sample_fn, F1_score):
        normalization = _describe_normalizer(sample_fn.normalize_gold)
        measure = "Token-overlap F1 between prediction and reference"
        sample_level = (
            "Split prediction and gold into whitespace tokens, compute bag-of-words precision/recall, "
            "and return F1. For multiple golds/preds, aggregate with the configured function. "
            f"Normalization: {normalization}."
        )
        corpus_level = "Aggregate sample F1 scores with the configured corpus function."
        return MetricDescription(measure, sample_level, corpus_level, "F1_score")

    if isinstance(sample_fn, LoglikelihoodAcc):
        normalization = _describe_logprob_normalization(sample_fn.logprob_normalization)
        measure = "Multiple-choice accuracy from log-probabilities"
        sample_level = (
            "Select the choice with the highest logprob (optionally normalized) and return 1 if it is in the gold indices, "
            f"else 0. Normalization: {normalization}."
        )
        corpus_level = "Average accuracy over samples."
        return MetricDescription(
            measure, sample_level, corpus_level, "LoglikelihoodAcc"
        )

    if isinstance(sample_fn, NormalizedMultiChoiceProbability):
        normalization = _describe_logprob_normalization(
            sample_fn.log_prob_normalization
        )
        measure = "Normalized gold-choice probability"
        sample_level = (
            "Exponentiate (optionally normalized) logprobs, normalize by the sum over all choices, "
            "then aggregate probabilities for gold choices (default max). "
            f"Normalization: {normalization}."
        )
        corpus_level = "Average normalized probabilities over samples."
        return MetricDescription(
            measure, sample_level, corpus_level, "NormalizedMultiChoiceProbability"
        )

    if isinstance(sample_fn, Probability):
        normalization = _describe_logprob_normalization(
            sample_fn.log_prob_normalization
        )
        measure = "Gold-choice probability"
        sample_level = (
            "Exponentiate (optionally normalized) logprobs and aggregate probabilities for gold choices "
            f"(default max). Normalization: {normalization}."
        )
        corpus_level = "Average probabilities over samples."
        return MetricDescription(measure, sample_level, corpus_level, "Probability")

    if isinstance(sample_fn, Recall):
        measure = f"Recall@{sample_fn.recall_depth} over ranked choices"
        sample_level = "Rank choices by logprob and return 1 if any gold index appears in the top-k, else 0."
        corpus_level = "Average recall over samples."
        return MetricDescription(measure, sample_level, corpus_level, "Recall")

    if isinstance(sample_fn, MRR):
        measure = "Mean reciprocal rank of the best gold choice"
        sample_level = "Rank choices by logprob (optionally length-normalized) and return 1/(rank of best gold + 1)."
        corpus_level = "Average reciprocal rank over samples."
        return MetricDescription(measure, sample_level, corpus_level, "MRR")

    if isinstance(sample_fn, AccGoldLikelihood):
        measure = "Argmax-logit accuracy over gold targets"
        sample_level = "Return 1 if any gold target is the argmax of logits, else 0."
        corpus_level = "Average accuracy over samples."
        return MetricDescription(
            measure, sample_level, corpus_level, "AccGoldLikelihood"
        )

    if isinstance(sample_fn, ROUGE):
        measure = f"ROUGE-{metric_name.replace('rouge', '')} overlap score"
        if metric_name == "rougeLsum":
            measure = "ROUGE-Lsum overlap score"
        sample_level = (
            "Compute ROUGE F-measure between each prediction and gold using rouge-score, with optional normalization. "
            "Supports bootstrapped scoring for T5-style ROUGE and aggregation across multiple golds/preds."
        )
        corpus_level = "Aggregate ROUGE scores with the configured corpus function."
        return MetricDescription(measure, sample_level, corpus_level, "ROUGE")

    if isinstance(sample_fn, BertScore):
        if metric_name.endswith("-P"):
            measure = "BERTScore precision"
        elif metric_name.endswith("-R"):
            measure = "BERTScore recall"
        else:
            measure = "BERTScore F1"
        sample_level = "Compute BERTScore using a DeBERTa-based scorer, comparing token embeddings between prediction and gold."
        corpus_level = "Average BERTScore across samples."
        return MetricDescription(measure, sample_level, corpus_level, "BertScore")

    if isinstance(sample_fn, Extractiveness):
        if metric_name == "summarization_coverage":
            measure = "Extractive coverage of summary from source"
        elif metric_name == "summarization_density":
            measure = "Extractive density of summary from source"
        else:
            measure = "Compression ratio of summary relative to source"
        sample_level = "Compute extractive statistics (coverage, density, compression) by aligning summary fragments to the source text."
        corpus_level = "Average extractiveness statistics over samples."
        return MetricDescription(measure, sample_level, corpus_level, "Extractiveness")

    if isinstance(sample_fn, Faithfulness):
        measure = "Summary faithfulness (SummaCZS)"
        sample_level = "Use the SummaCZS model to score whether the summary is supported by the source text."
        corpus_level = "Average faithfulness scores over samples."
        return MetricDescription(measure, sample_level, corpus_level, "Faithfulness")

    if isinstance(sample_fn, BLEURT):
        measure = "BLEURT semantic similarity score"
        sample_level = "Score prediction vs gold using the BLEURT-tiny model; if only one prediction is given, it is paired with each gold."
        corpus_level = "Average BLEURT scores over samples."
        return MetricDescription(measure, sample_level, corpus_level, "BLEURT")

    if isinstance(sample_fn, BLEU):
        measure = f"Sentence-level BLEU-{sample_fn.n_gram}"
        sample_level = "Compute sentence BLEU against all golds using NLTK, then average across predictions."
        corpus_level = "Average BLEU scores over samples."
        return MetricDescription(measure, sample_level, corpus_level, "BLEU")

    if isinstance(sample_fn, StringDistance):
        if metric_name == "longest_common_prefix_length":
            measure = "Longest common prefix length"
        elif metric_name == "edit_distance":
            measure = "Token-level edit distance"
        else:
            measure = "Normalized edit similarity"
        sample_level = "Tokenize prediction and reference, truncate reference to prediction length, then compute the requested string distance."
        corpus_level = (
            "Aggregate string distance scores with the configured corpus function."
        )
        return MetricDescription(measure, sample_level, corpus_level, "StringDistance")

    if isinstance(sample_fn, DropMetrics):
        if metric_name == "em":
            measure = "DROP exact match (normalized span match)"
        else:
            measure = "DROP F1 (bag-of-words with numeric consistency)"
        sample_level = (
            "Normalize spans, align predicted and gold spans with optimal matching, and compute exact match or F1. "
            "Numeric mismatches zero out F1."
        )
        corpus_level = "Aggregate DROP scores with the configured corpus function."
        return MetricDescription(measure, sample_level, corpus_level, "DropMetrics")

    if isinstance(sample_fn, TruthfulqaMCMetrics):
        if metric_name == "truthfulqa_mc1":
            measure = "TruthfulQA MC1 accuracy"
        else:
            measure = "TruthfulQA MC2 normalized probability"
        sample_level = (
            "For MC1, check if the highest-logprob choice is the designated correct answer. "
            "For MC2, sum normalized probabilities assigned to all true answers."
        )
        corpus_level = "Average TruthfulQA scores over samples."
        return MetricDescription(
            measure, sample_level, corpus_level, "TruthfulqaMCMetrics"
        )

    if isinstance(sample_fn, MultilingualExtractiveMatchMetric):
        measure = "Extractive match after answer extraction"
        sample_level = (
            "Extract answers from predictions and golds using regexes for "
            f"{_describe_extraction_targets(sample_fn.pred_extraction_target)}; "
            "compare extracted values with symbolic/numeric matching (SymPy) and count a match if any gold matches."
        )
        corpus_level = "Average extractive-match scores over samples."
        return MetricDescription(
            measure, sample_level, corpus_level, "MultilingualExtractiveMatchMetric"
        )

    if isinstance(sample_fn, SamplingMetric):
        normalization = _describe_sampling_normalization(sample_fn)
        scoring = _describe_sampling_score_fn(sample_fn)
        if isinstance(sample_fn, AvgAtN):
            measure = f"Average accuracy over n={sample_fn.n} samples"
            sample_level = (
                "Compute correctness for each of n generations using the configured scoring function, then average. "
                f"Scoring: {scoring}. Preprocessing: {normalization}."
            )
            corpus_level = "Average sample scores over the dataset."
            return MetricDescription(measure, sample_level, corpus_level, "AvgAtN")

        if isinstance(sample_fn, MajAtN):
            measure = f"Majority-vote accuracy over n={sample_fn.n} samples"
            sample_level = (
                "Normalize each of the n generations, pick the most frequent answer, and score it against the gold. "
                f"Scoring: {scoring}. Preprocessing: {normalization}."
            )
            corpus_level = "Average majority-vote accuracy over samples."
            return MetricDescription(measure, sample_level, corpus_level, "MajAtN")

        if isinstance(sample_fn, PassAtK):
            measure = f"Pass@k (k={sample_fn.k}, n={sample_fn.n or 'auto'})"
            sample_level = (
                "Score each of n generations for correctness, then estimate pass@k using the unbiased estimator "
                "from Chen et al. (2021). "
                f"Scoring: {scoring}. Preprocessing: {normalization}."
            )
            corpus_level = "Average pass@k over samples."
            return MetricDescription(measure, sample_level, corpus_level, "PassAtK")

        if isinstance(sample_fn, GPassAtK):
            measure = "G-Pass@k (hypergeometric estimator)"
            sample_level = (
                "Score each of n generations for correctness, then compute G-Pass@k across thresholds using a "
                "hypergeometric survival function. Returns multiple submetrics (thresholded and mean variants). "
                f"Scoring: {scoring}. Preprocessing: {normalization}."
            )
            corpus_level = "Average G-Pass@k values over samples."
            return MetricDescription(measure, sample_level, corpus_level, "GPassAtK")

    if isinstance(sample_fn, JudgeLLMSimpleQA):
        measure = "LLM-judge score for SimpleQA"
        sample_level = "Use a judge LLM to compare the model answer against gold and options; return the judge score and metadata."
        corpus_level = "Average judge scores over samples."
        return MetricDescription(
            measure, sample_level, corpus_level, "JudgeLLMSimpleQA"
        )

    if isinstance(sample_fn, JudgeLLMMTBench):
        measure = "LLM-judge score for MT-Bench turns"
        sample_level = "Use a judge LLM to score the model response for turn 1 (turn 2 is currently a placeholder)."
        corpus_level = "Average judge scores over samples."
        return MetricDescription(measure, sample_level, corpus_level, "JudgeLLMMTBench")

    if isinstance(sample_fn, JudgeLLMMixEval):
        measure = "LLM-judge score for MixEval"
        sample_level = "Use a judge LLM to score the response against the prompt and options; output a judge score per sample."
        corpus_level = "Aggregate judge scores with the configured corpus function."
        return MetricDescription(measure, sample_level, corpus_level, "JudgeLLMMixEval")

    class_name = getattr(sample_fn, "__class__", type(sample_fn)).__name__
    if class_name == "IFBench":
        measure = "Instruction-following accuracy (IFBench)"
        sample_level = (
            "Evaluate strict and loose instruction-following for each prompt and each instruction, "
            "returning prompt-level and instruction-level accuracy indicators."
        )
        corpus_level = "Aggregate prompt-level accuracy by mean and instruction-level accuracy by flattening."
        return MetricDescription(measure, sample_level, corpus_level, class_name)

    if class_name == "IFEvalMetrics":
        measure = "Instruction-following accuracy (IFEval)"
        sample_level = (
            "Check instruction compliance for strict and relaxed response variants, "
            "returning prompt-level and instruction-level accuracy indicators."
        )
        corpus_level = "Aggregate prompt-level accuracy by mean and instruction-level accuracy by flattening."
        return MetricDescription(measure, sample_level, corpus_level, class_name)

    if class_name == "VerifiableRewardMetric":
        measure = "Verifiable reward accuracy"
        sample_level = (
            "Use a symbolic judge to validate the generated program against a reference validation program "
            "and return a binary accuracy for the sample."
        )
        corpus_level = "Average accuracy over samples."
        return MetricDescription(measure, sample_level, corpus_level, class_name)

    if class_name == "CodegenMetric":
        measure = "Code generation pass@1"
        sample_level = (
            "Extract code from the model output, execute it against public and private tests, "
            "and return pass@1 for the sample."
        )
        corpus_level = "Average pass@1 over samples."
        return MetricDescription(measure, sample_level, corpus_level, class_name)

    if class_name == "EmotionClassificationMetric":
        measure = "Emotion classification exact match"
        sample_level = (
            "Parse the model output into an emotion label, compare against the gold label, "
            "and emit exact-match plus parsing-failure indicators."
        )
        corpus_level = (
            "Aggregate accuracy and failure rates with the configured corpus function."
        )
        return MetricDescription(measure, sample_level, corpus_level, class_name)

    if class_name == "TinyCorpusAggregator":
        measure = "TinyBenchmarks IRT-based score"
        sample_level = (
            "Compute per-sample accuracy or exact match to feed the IRT model."
        )
        corpus_level = "Fit an item-response-theory model using precomputed parameters and return IRT, PIRt, or GPIrt."
        return MetricDescription(measure, sample_level, corpus_level, class_name)

    if class_name == "JudgeLLMHLE":
        measure = "HLE judge metrics"
        sample_level = "Use a judge LLM to extract the model answer, assess correctness, and estimate confidence."
        corpus_level = "Compute accuracy, confidence interval half-width, and calibration error from judge outputs."
        return MetricDescription(measure, sample_level, corpus_level, class_name)

    if isinstance(sample_fn, JudgeLLM):
        measure = "LLM-judge score"
        sample_level = "Use a judge LLM to score the model response based on a task-specific prompt."
        corpus_level = "Aggregate judge scores with the configured corpus function."
        return MetricDescription(measure, sample_level, corpus_level, "JudgeLLM")

    if isinstance(sample_fn, GenerativePreparator):
        measure = "Corpus-level generative metric"
        sample_level = "Collect predictions and golds into a corpus input object; scoring happens at corpus level."
        corpus_level = "Computed by the corpus-level metric implementation."
        return MetricDescription(
            measure, sample_level, corpus_level, "GenerativePreparator"
        )

    if isinstance(sample_fn, LoglikelihoodPreparator):
        measure = "Corpus-level loglikelihood metric"
        sample_level = "Collect gold indices and the argmax logprob choice into a corpus input object; scoring happens at corpus level."
        corpus_level = "Computed by the corpus-level metric implementation."
        return MetricDescription(
            measure, sample_level, corpus_level, "LoglikelihoodPreparator"
        )

    if isinstance(sample_fn, PerplexityPreparator):
        measure = "Perplexity over prompt"
        sample_level = "Sum logprobs for the prompt and count units (words or bytes) for corpus-level perplexity."
        corpus_level = "Computed by the corpus-level perplexity implementation."
        return MetricDescription(
            measure, sample_level, corpus_level, "PerplexityPreparator"
        )

    if isinstance(sample_fn, TargetPerplexityPreparator):
        measure = "Perplexity over target answers"
        sample_level = "Sum logprobs for the target answers and count units (words or bytes) for corpus-level perplexity."
        corpus_level = "Computed by the corpus-level perplexity implementation."
        return MetricDescription(
            measure, sample_level, corpus_level, "TargetPerplexityPreparator"
        )

    # Fallback
    return MetricDescription(
        "Custom metric",
        "Custom sample-level computation (see implementation)",
        "Custom corpus-level aggregation (see implementation)",
        getattr(sample_fn, "__class__", type(sample_fn)).__name__,
    )


def _describe_corpus_fn(corpus_fn: Any, metric_name: str) -> str:
    if isinstance(corpus_fn, CorpusLevelComputation):
        if isinstance(corpus_fn, CorpusLevelTranslationMetric):
            return (
                f"Compute corpus-level {corpus_fn.metric_type.upper()} via sacrebleu."
            )
        if isinstance(corpus_fn, CorpusLevelPerplexityMetric):
            if corpus_fn.metric_type == "perplexity":
                return "Exponentiate the negative mean logprob."
            if corpus_fn.metric_type == "weighted_perplexity":
                return "Exponentiate the negative weighted mean logprob (weights are word/byte counts)."
            if corpus_fn.metric_type == "bits_per_byte":
                return "Compute average bits per byte from logprobs (normalized by log(2))."
        if isinstance(corpus_fn, CorpusLevelF1Score):
            average = corpus_fn.average
            if corpus_fn.num_classes == 2:
                return f"Compute sklearn F1 with average={average}."
            return f"Compute per-class F1 and average across {corpus_fn.num_classes} classes (average={average})."
        if isinstance(corpus_fn, MatthewsCorrCoef):
            return "Compute Matthews correlation coefficient over gold and predicted labels."
        return "Compute corpus score using the metric's compute_corpus method."

    if callable(corpus_fn):
        if corpus_fn is np.mean:
            return "Average over samples."
        if corpus_fn is np.sum:
            return "Sum over samples."
        if corpus_fn is max:
            return "Take the maximum over samples."
        if corpus_fn is min:
            return "Take the minimum over samples."

        name = getattr(corpus_fn, "__name__", "")
        if name == "agg_inst_level_acc":
            return "Flatten per-instruction scores across samples and average."
        if name == "mean_dv_5":
            return "Average over samples and divide by 5 to rescale judge scores."
        return f"Custom aggregation function ({name or 'callable'})."

    # Some metric groupings use custom objects with compute_corpus
    if hasattr(corpus_fn, "compute_corpus"):
        return "Compute corpus score using the metric's compute_corpus method."

    return "Custom corpus-level aggregation."


def _describe_metric(
    metric: Any, metric_name: str, corpus_fn: Any
) -> MetricDescription:
    base_desc = _describe_sample_level_fn(metric.sample_level_fn, metric_name)
    corpus_desc = _describe_corpus_fn(corpus_fn, metric_name)

    # Adjust measures for common metric names
    if metric_name == "bleu":
        base_desc = base_desc.__class__(
            "Corpus BLEU score", base_desc.sample_level, corpus_desc, base_desc.source
        )
    elif metric_name == "chrf":
        base_desc = base_desc.__class__(
            "Corpus chrF score", base_desc.sample_level, corpus_desc, base_desc.source
        )
    elif metric_name == "chrf++":
        base_desc = base_desc.__class__(
            "Corpus chrF++ score", base_desc.sample_level, corpus_desc, base_desc.source
        )
    elif metric_name == "ter":
        base_desc = base_desc.__class__(
            "Translation edit rate (TER)",
            base_desc.sample_level,
            corpus_desc,
            base_desc.source,
        )
    elif metric_name == "summac":
        base_desc = base_desc.__class__(
            "Summary faithfulness (SummaCZS)",
            base_desc.sample_level,
            corpus_desc,
            base_desc.source,
        )
    elif metric_name == "word_perplexity":
        base_desc = base_desc.__class__(
            "Word-level weighted perplexity",
            base_desc.sample_level,
            corpus_desc,
            base_desc.source,
        )
    elif metric_name == "byte_perplexity":
        base_desc = base_desc.__class__(
            "Byte-level weighted perplexity",
            base_desc.sample_level,
            corpus_desc,
            base_desc.source,
        )
    elif metric_name == "bits_per_byte":
        base_desc = base_desc.__class__(
            "Bits per byte", base_desc.sample_level, corpus_desc, base_desc.source
        )
    elif metric_name == "ppl":
        base_desc = base_desc.__class__(
            "Perplexity", base_desc.sample_level, corpus_desc, base_desc.source
        )
    elif metric_name == "loglikelihood_f1":
        base_desc = base_desc.__class__(
            "Classification F1 from log-likelihoods",
            base_desc.sample_level,
            corpus_desc,
            base_desc.source,
        )
    elif metric_name == "mcc":
        base_desc = base_desc.__class__(
            "Matthews correlation coefficient",
            base_desc.sample_level,
            corpus_desc,
            base_desc.source,
        )
    elif metric_name == "mf1":
        base_desc = base_desc.__class__(
            "Multi-class F1 (micro average)",
            base_desc.sample_level,
            corpus_desc,
            base_desc.source,
        )
    elif metric_name == "accuracy":
        base_desc = base_desc.__class__(
            "Judge accuracy", base_desc.sample_level, corpus_desc, base_desc.source
        )
    elif metric_name == "confidence_half_width":
        base_desc = base_desc.__class__(
            "95% confidence interval half-width",
            base_desc.sample_level,
            corpus_desc,
            base_desc.source,
        )
    elif metric_name == "calibration_error":
        base_desc = base_desc.__class__(
            "Calibration error", base_desc.sample_level, corpus_desc, base_desc.source
        )
    elif metric_name == "exact_match":
        base_desc = base_desc.__class__(
            "Exact-match classification accuracy",
            base_desc.sample_level,
            corpus_desc,
            base_desc.source,
        )
    elif metric_name == "unknown_prediction":
        base_desc = base_desc.__class__(
            "Parsing failure rate (unknown predictions)",
            base_desc.sample_level,
            corpus_desc,
            base_desc.source,
        )
    elif metric_name == "total_samples":
        base_desc = base_desc.__class__(
            "Total samples processed",
            base_desc.sample_level,
            corpus_desc,
            base_desc.source,
        )
    elif metric_name == "verifiable_reward":
        base_desc = base_desc.__class__(
            "Verifiable reward accuracy",
            base_desc.sample_level,
            corpus_desc,
            base_desc.source,
        )
    elif metric_name in {"irt", "pirt", "gpirt"}:
        base_desc = base_desc.__class__(
            f"TinyBenchmarks {metric_name.upper()} score",
            "Compute per-sample accuracy or exact match, then fit an IRT model at corpus level.",
            "Fit item-response theory parameters and derive IRT, PIRt, or GPIrt estimates.",
            base_desc.source,
        )
    elif metric_name.startswith("llm_judge_mixeval"):
        base_desc = base_desc.__class__(
            "MixEval LLM-judge score",
            base_desc.sample_level,
            corpus_desc,
            base_desc.source,
        )
    elif metric_name in {"judge_score_turn_1", "judge_score_turn_2"}:
        base_desc = base_desc.__class__(
            f"MT-Bench {metric_name.replace('_', ' ')}",
            base_desc.sample_level,
            corpus_desc,
            base_desc.source,
        )
    elif metric_name.startswith("pass@k") or metric_name.startswith("gpqa_pass@k"):
        base_desc = base_desc.__class__(
            "Pass@k", base_desc.sample_level, corpus_desc, base_desc.source
        )
    elif metric_name.startswith("avg@n"):
        base_desc = base_desc.__class__(
            "Average over sampled generations",
            base_desc.sample_level,
            corpus_desc,
            base_desc.source,
        )
    elif metric_name.startswith("maj@n"):
        base_desc = base_desc.__class__(
            "Majority-vote accuracy over sampled generations",
            base_desc.sample_level,
            corpus_desc,
            base_desc.source,
        )
    elif metric_name.startswith("em:"):
        base_desc = base_desc.__class__(
            "Exact match (parameterized)",
            base_desc.sample_level,
            corpus_desc,
            base_desc.source,
        )
    elif metric_name == "em":
        base_desc = base_desc.__class__(
            "Exact match", base_desc.sample_level, corpus_desc, base_desc.source
        )
    elif metric_name == "f1":
        if isinstance(corpus_fn, CorpusLevelF1Score):
            avg = corpus_fn.average
            base_desc = base_desc.__class__(
                f"Classification F1 (average={avg})",
                base_desc.sample_level,
                corpus_desc,
                base_desc.source,
            )
        else:
            base_desc = base_desc.__class__(
                "F1 score", base_desc.sample_level, corpus_desc, base_desc.source
            )

    return MetricDescription(
        base_desc.measure, base_desc.sample_level, corpus_desc, base_desc.source
    )


def _get_metric_names(metric: Any) -> list[str]:
    if isinstance(metric.metric_name, list):
        return metric.metric_name
    return [metric.metric_name]


def _get_corpus_fn(metric: Any, name: str) -> Any:
    corpus_fn = metric.corpus_level_fn
    if isinstance(corpus_fn, dict):
        if name in corpus_fn:
            return corpus_fn[name]
        # fallback to any defined function if key mismatch
        return next(iter(corpus_fn.values()))
    return corpus_fn


def _variant_key(desc: MetricDescription) -> tuple[str, str, str, str]:
    return (desc.measure, desc.sample_level, desc.corpus_level, desc.source)


def main() -> int:
    registry = Registry()
    tasks = registry.load_tasks()

    metrics_by_name: dict[str, list[MetricDescription]] = {}

    for task in tasks.values():
        for metric in task.metrics:
            for name in _get_metric_names(metric):
                corpus_fn = _get_corpus_fn(metric, name)
                desc = _describe_metric(metric, name, corpus_fn)
                metrics_by_name.setdefault(name, [])
                metrics_by_name[name].append(desc)

    # Deduplicate and format
    output: dict[str, Any] = {}
    for name, descriptions in metrics_by_name.items():
        deduped = {}
        for desc in descriptions:
            deduped[_variant_key(desc)] = desc

        variants = list(deduped.values())
        if len(variants) == 1:
            desc = variants[0]
            output[name] = {
                "measure": desc.measure,
                "sample_level": desc.sample_level,
                "corpus_level": desc.corpus_level,
            }
        else:
            output[name] = {
                "note": "This metric name is used by multiple implementations; see variants.",
                "variants": [
                    {
                        "measure": desc.measure,
                        "sample_level": desc.sample_level,
                        "corpus_level": desc.corpus_level,
                        "source": desc.source,
                    }
                    for desc in variants
                ],
            }

    output_path = "lighteval/src/lighteval/metrics/metric_docs.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, sort_keys=True, ensure_ascii=True)
        f.write("\n")

    print(f"Wrote {len(output)} metrics to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
