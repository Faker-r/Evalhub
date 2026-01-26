# Benchmark Compatibility Test Report

**Generated:** 2026-01-25T13:39:07-08:00
**Test Duration:** 1707.3 seconds

## Summary

| Metric                  | Count |
| ----------------------- | ----- |
| Total Benchmarks Tested | 74    |
| ✓ Successful            | 32    |
| ✗ Failed                | 15    |
| ⚠ Silent Failures       | 27    |
| ⏱ Timeouts              | 0     |

**Success Rate:** 43.2%

## ✓ Successful Benchmarks

| Dataset                      | Task                                        | Trace ID | Duration (s) | Scores                                                                                                                                                                                                  |
| ---------------------------- | ------------------------------------------- | -------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| gsm8k                        | gsm8k                                       | 1108     | 26.0         | extractive_match: {'std': 0.24, 'mean': 0.6, 'failed': 0}                                                                                                                                               |
| hellaswag                    | hellaswag                                   | 1109     | 23.9         | em: {'std': 0.2, 'mean': 0.2, 'failed': 0}                                                                                                                                                              |
| MMLU-Pro                     | mmlu_pro                                    | 1112     | 20.4         | extractive_match: {'std': 0.24, 'mean': 0.4, 'failed': 0}                                                                                                                                               |
| trivia_qa                    | triviaqa                                    | 1115     | 22.0         | em: {'std': 0.0, 'mean': 0.0, 'failed': 0}, f1: {'std': 0.04, 'mean': 0.04, 'failed': 0}                                                                                                                |
| piqa                         | piqa                                        | 1116     | 21.4         | em: {'std': 0.2, 'mean': 0.2, 'failed': 0}                                                                                                                                                              |
| IFEval                       | ifeval                                      | 1117     | 20.2         | inst_level_loose_acc: {'std': 0.0, 'mean': 0.86, 'failed': 0}, inst_level_strict_acc: {'std': 0.0, 'mean': 0.86, 'failed': 0}, prompt_level_loose_acc: {'std': 0.2, 'mean': 0.8, 'failed': 0} (+1 more) |
| commonsense_qa               | commonsenseqa                               | 1118     | 22.5         | em: {'std': 0.24, 'mean': 0.4, 'failed': 0}                                                                                                                                                             |
| squad_v2                     | squad_v2                                    | 1120     | 21.3         | em: {'std': 0.0, 'mean': 0.0, 'failed': 0}, f1: {'std': 0.04, 'mean': 0.08, 'failed': 0}                                                                                                                |
| emotion                      | emotion_classification                      | 1122     | 24.3         | exact_match: {'std': 0.2, 'mean': 0.8, 'failed': 0}, total_samples: {'std': 0.0, 'mean': 5.0, 'failed': 0}, unknown_prediction: {'std': 0.0, 'mean': 0.0, 'failed': 0}                                  |
| social_i_qa                  | siqa                                        | 1123     | 19.7         | em: {'std': 0.24, 'mean': 0.4, 'failed': 0}                                                                                                                                                             |
| web_questions                | webqs                                       | 1127     | 23.6         | em: {'std': 0.0, 'mean': 0.0, 'failed': 0}, f1: {'std': 0.04, 'mean': 0.07, 'failed': 0}                                                                                                                |
| med_qa                       | med_qa                                      | 1128     | 20.5         | em: {'std': 0.0, 'mean': 0.0, 'failed': 0}, f1: {'std': 0.07, 'mean': 0.07, 'failed': 0}                                                                                                                |
| coqa                         | coqa                                        | 1130     | 23.1         | f1: {'std': 0.04, 'mean': 0.09, 'failed': 0}                                                                                                                                                            |
| sacrebleu_manual             | wmt14:de-en                                 | 1134     | 27.2         | ter: {'std': 0.56, 'mean': 47.17, 'failed': 0}, bleu: {'std': 0.24, 'mean': 46.1, 'failed': 0}, chrf: {'std': 0.42, 'mean': 60.96, 'failed': 0}                                                         |
| tinyGSM8k                    | tiny:gsm8k                                  | 1137     | 23.2         | irt: {'std': 0, 'mean': 0.0, 'failed': 0}, pirt: {'std': 0, 'mean': 0.02, 'failed': 0}, gpirt: {'std': 0, 'mean': 0.01, 'failed': 0}                                                                    |
| GSM-Plus                     | gsm_plus                                    | 1140     | 22.9         | extractive_match: {'std': 0.2, 'mean': 0.8, 'failed': 0}                                                                                                                                                |
| story_cloze                  | storycloze:2016                             | 1145     | 26.4         | em: {'std': 0.0, 'mean': 0.0, 'failed': 0}, f1: {'std': 0.02, 'mean': 0.09, 'failed': 0}                                                                                                                |
| drop_harness                 | drop                                        | 1148     | 20.7         | em: {'std': 0.0, 'mean': 0.0, 'failed': 0}, f1: {'std': 0.07, 'mean': 0.14, 'failed': 0}                                                                                                                |
| wikifact                     | wikifact:applies_to_jurisdiction            | 1150     | 24.4         | em: {'std': 0.0, 'mean': 0.0, 'failed': 0}, f1: {'std': 0.01, 'mean': 0.23, 'failed': 0}                                                                                                                |
| lextreme                     | lextreme:brazilian_court_decisions_judgment | 1151     | 22.3         | em: {'std': 0.24, 'mean': 0.4, 'failed': 0}                                                                                                                                                             |
| SimpleQA                     | simpleqa                                    | 1152     | 25.5         | em: {'std': 0.0, 'mean': 0.0, 'failed': 0}, f1: {'std': 0.03, 'mean': 0.04, 'failed': 0}                                                                                                                |
| small_natural_questions      | natural_questions                           | 1156     | 21.4         | em: {'std': 0.0, 'mean': 0.0, 'failed': 0}, f1: {'std': 0.06, 'mean': 0.11, 'failed': 0}                                                                                                                |
| med_dialog                   | med_dialog:healthcaremagic                  | 1158     | 26.4         | em: {'std': 0.0, 'mean': 0.0, 'failed': 0}, f1: {'std': 0.06, 'mean': 0.15, 'failed': 0}                                                                                                                |
| med_mcqa                     | med_mcqa                                    | 1159     | 23.6         | em: {'std': 0.0, 'mean': 0.0, 'failed': 0}, f1: {'std': 0.07, 'mean': 0.07, 'failed': 0}                                                                                                                |
| arc-agi-2                    | arc_agi_2                                   | 1166     | 24.2         | em: {'std': 0.0, 'mean': 0.0, 'failed': 0}, f1: {'std': 0.07, 'mean': 0.51, 'failed': 0}                                                                                                                |
| med_paragraph_simplification | med_paragraph_simplification                | 1168     | 26.4         | em: {'std': 0.0, 'mean': 0.0, 'failed': 0}, f1: {'std': 0.05, 'mean': 0.42, 'failed': 0}                                                                                                                |
| jeopardy                     | jeopardy                                    | 1172     | 39.4         | em: {'std': 0.2, 'mean': 0.2, 'failed': 0}                                                                                                                                                              |
| covid_dialogue               | covid_dialogue                              | 1173     | 24.7         | em: {'std': 0.0, 'mean': 0.0, 'failed': 0}, f1: {'std': 0.04, 'mean': 0.18, 'failed': 0}                                                                                                                |
| synthetic_reasoning_natural  | synthetic_reasoning:natural_easy            | 1174     | 25.7         | em: {'std': 0.0, 'mean': 0.0, 'failed': 0}, f1: {'std': 0.04, 'mean': 0.06, 'failed': 0}                                                                                                                |
| narrative_qa_helm            | narrativeqa                                 | 1175     | 26.0         | f1: {'std': 0.09, 'mean': 0.26, 'failed': 0}, rougeL: {'std': 0.08, 'mean': 0.31, 'failed': 0}                                                                                                          |
| Buy                          | entity_data_imputation:Buy                  | 1177     | 25.8         | em: {'std': 0.0, 'mean': 0.0, 'failed': 0}, f1: {'std': 0.07, 'mean': 0.07, 'failed': 0}                                                                                                                |
| quac_helm                    | quac                                        | 1179     | 25.3         | em: {'std': 0.0, 'mean': 0.0, 'failed': 0}, f1: {'std': 0.12, 'mean': 0.26, 'failed': 0}                                                                                                                |

## ✗ Failed Benchmarks

### gpqa

**Task:** `gpqa:diamond`
**Trace ID:** 1113
**Duration:** 6.7s
**Error:** `Dataset 'Idavidrein/gpqa' is a gated dataset on the Hub.`

### hle

**Task:** `hle`
**Trace ID:** 1124
**Duration:** 6.9s
**Error:** `Dataset 'cais/hle' is a gated dataset on the Hub.`

### mgsm

**Task:** `mgsm:bn`
**Trace ID:** 1132
**Duration:** 6.7s
**Error:** `Couldn't find cache for juletxara/mgsm for config 'bn'`

### real-toxicity-prompts

**Task:** `real_toxicity_prompts`
**Trace ID:** 1133
**Duration:** 27.5s
**Error:** `max() iterable argument is empty`

### IFBench_test

**Task:** `ifbench_test`
**Trace ID:** 1138
**Duration:** 20.0s
**Error:** `Requested 'syllapy' but it is not available.`

### qasper

**Task:** `qasper`
**Trace ID:** 1141
**Duration:** 6.8s
**Error:** `Dataset scripts are no longer supported, but found qasper.py`

### raft

**Task:** `raft:ade_corpus_v2`
**Trace ID:** 1142
**Duration:** 6.7s
**Error:** `Dataset scripts are no longer supported, but found raft.py`

### arithmetic

**Task:** `arithmetic:1dc`
**Trace ID:** 1144
**Duration:** 6.6s
**Error:** `Couldn't find cache for EleutherAI/arithmetic for config 'arithmetic_1dc'`

### IFBench_multi-turn

**Task:** `ifbench_multiturn`
**Trace ID:** 1147
**Duration:** 24.8s
**Error:** `Requested 'syllapy' but it is not available.`

### babi_qa

**Task:** `babi_qa`
**Trace ID:** 1153
**Duration:** 6.7s
**Error:** `Couldn't find cache for facebook/babi_qa for config 'en-valid-qa1'`

### SLR-Bench

**Task:** `slr_bench_all`
**Trace ID:** 1154
**Duration:** 4.9s
**Error:** `Requested 'evaluate' but it is not available.`

### MixEval

**Task:** `mixeval_easy:freeform`
**Trace ID:** 1160
**Duration:** 23.9s
**Error:** `Requested 'vllm' but it is not available.`

### summarization

**Task:** `summarization:cnn-dm`
**Trace ID:** 1161
**Duration:** 41.7s
**Error:** `Requires 'lighteval[multilingual]'.`

### legal_summarization

**Task:** `legal_summarization:billsum`
**Trace ID:** 1165
**Duration:** 33.1s
**Error:** `Requires 'lighteval[multilingual]'.`

### mt-bench

**Task:** `mt_bench`
**Trace ID:** 1169
**Duration:** 27.4s
**Error:** `list index out of range`

## ⚠ Silent Failures

_These benchmarks completed but returned suspicious results (e.g., all zeros)_

| Task                                 | Trace ID | Issue               |
| ------------------------------------ | -------- | ------------------- |
| `math_500`                           | 1110     | All scores are zero |
| `openbookqa`                         | 1111     | All scores are zero |
| `truthfulqa:gen`                     | 1114     | All scores are zero |
| `aime24`                             | 1119     | All scores are zero |
| `pubmedqa`                           | 1121     | All scores are zero |
| `aime25`                             | 1125     | All scores are zero |
| `math:algebra`                       | 1126     | All scores are zero |
| `mmmu_pro:standard-10`               | 1129     | All scores are zero |
| `mmlu:abstract_algebra`              | 1131     | All scores are zero |
| `bigbench:mult_data_wrangling`       | 1135     | All scores are zero |
| `lcb:codegeneration`                 | 1136     | All scores are zero |
| `olympiad_bench:OE_TO_maths_en_COMP` | 1139     | All scores are zero |
| `aa_omniscience`                     | 1143     | All scores are zero |
| `asdiv`                              | 1146     | All scores are zero |
| `lexglue:case_hold`                  | 1149     | All scores are zero |
| `boolq`                              | 1155     | All scores are zero |
| `bbq`                                | 1157     | All scores are zero |
| `lsat_qa`                            | 1162     | All scores are zero |
| `numeracy:linear_example`            | 1163     | All scores are zero |
| `dyck_language:2`                    | 1164     | All scores are zero |
| `entity_matching:Abt_Buy`            | 1167     | All scores are zero |
| `civil_comments:LGBTQ`               | 1170     | All scores are zero |
| `synthetic_reasoning:induction`      | 1171     | All scores are zero |
| `aimo_progress_prize_1`              | 1176     | All scores are zero |
| `imdb`                               | 1178     | All scores are zero |
| `unscramble:anagrams1`               | 1180     | All scores are zero |
| `entity_data_imputation:Restaurant`  | 1181     | All scores are zero |

---

## 📋 Full Error Tracebacks

### gpqa (`gpqa:diamond`)

```python
datasets.exceptions.DatasetNotFoundError: Dataset 'Idavidrein/gpqa' is a gated dataset on the Hub. Visit the dataset page at https://huggingface.co/datasets/Idavidrein/gpqa to ask for access.
```

### hle (`hle`)

```python
datasets.exceptions.DatasetNotFoundError: Dataset 'cais/hle' is a gated dataset on the Hub. Visit the dataset page at https://huggingface.co/datasets/cais/hle to ask for access.
```

### mgsm (`mgsm:bn`)

```python
ValueError: Couldn't find cache for juletxara/mgsm for config 'bn'
Available configs in the cache: ['default']
```

### real-toxicity-prompts (`real_toxicity_prompts`)

```python
ValueError: max() iterable argument is empty
```

### IFBench_test (`ifbench_test`)

```python
ImportError: Through the use of Instruction, you requested the use of `syllapy` for this evaluation, but it is not available in your current environment. Please install it using pip.
```

### qasper (`qasper`)

```python
RuntimeError: Dataset scripts are no longer supported, but found qasper.py
```

### raft (`raft:ade_corpus_v2`)

```python
RuntimeError: Dataset scripts are no longer supported, but found raft.py
```

### arithmetic (`arithmetic:1dc`)

```python
ValueError: Couldn't find cache for EleutherAI/arithmetic for config 'arithmetic_1dc'
Available configs in the cache: ['default']
```

### IFBench_multi-turn (`ifbench_multiturn`)

```python
ImportError: Through the use of Instruction, you requested the use of `syllapy` for this evaluation, but it is not available in your current environment. Please install it using pip.
```

### babi_qa (`babi_qa`)

```python
ValueError: Couldn't find cache for facebook/babi_qa for config 'en-valid-qa1'
Available configs in the cache: ['default']
```

### SLR-Bench (`slr_bench_all`)

```python
ImportError: Through the use of prompt_fn, you requested the use of `evaluate` for this evaluation, but it is not available in your current environment. Please install it using pip.
```

### MixEval (`mixeval_easy:freeform`)

```python
ImportError: You requested the use of `vllm` for this evaluation, but it is not available in your current environment. Please install it using pip.
```

### summarization (`summarization:cnn-dm`)

```python
ImportError: Through the use of DataStatsMetric, you are trying to run an evaluation requiring multilingual capabilities. Please install the required extra: `pip install lighteval[multilingual]`
```

### legal_summarization (`legal_summarization:billsum`)

```python
ImportError: Through the use of DataStatsMetric, you are trying to run an evaluation requiring multilingual capabilities. Please install the required extra: `pip install lighteval[multilingual]`
```

### mt-bench (`mt_bench`)

```python
IndexError: list index out of range
```
