# Benchmark Compatibility Test Report

**Generated:** 2026-01-21T17:00:05.710083
**Test Duration:** 729.3 seconds

## Summary

| Metric | Count |
|--------|-------|
| Total Benchmarks Tested | 39 |
| ✓ Successful | 1 |
| ✗ Failed | 15 |
| ⚠ Silent Failures | 23 |
| ⏱ Timeouts | 0 |

**Success Rate:** 2.6%

## ✓ Successful Benchmarks

| Dataset | Task | Trace ID | Duration (s) | Scores |
|---------|------|----------|--------------|--------|
| jeopardy | jeopardy | 532 | 30.4 | em: {'std': 0.2, 'mean': 0.2, 'failed': 0} |

## ✗ Failed Benchmarks

### AA-Omniscience-Public

**Task:** `aa_omniscience`
**Trace ID:** 503
**Duration:** 10.9s

**Error Message:**
```
aa_omniscience_prompt() takes 1 positional argument but 2 were given
```

**Full Traceback:**
```python
Traceback (most recent call last):
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 176, in _run_task_evaluation_background
    pipeline_output = service._run_lighteval_task_pipeline(request)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 401, in _run_lighteval_task_pipeline
    pipeline = Pipeline(
               ^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 142, in __init__
    self._init_tasks_and_requests(tasks=tasks)
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 224, in _init_tasks_and_requests
    task.full_name: task.get_docs(self.pipeline_parameters.max_samples) for _, task in self.tasks_dict.items()
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 382, in get_docs
    eval_docs = self.eval_docs()
                ^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 359, in eval_docs
    self._docs = self._get_docs_from_split(self.evaluation_split)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 309, in _get_docs_from_split
    doc = self.formatter(item, self.name)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: aa_omniscience_prompt() takes 1 positional argument but 2 were given

```

### arithmetic

**Task:** `arithmetic:1dc`
**Trace ID:** 504
**Duration:** 6.6s

**Error Message:**
```
Dataset scripts are no longer supported, but found arithmetic.py
```

**Full Traceback:**
```python
Traceback (most recent call last):
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 176, in _run_task_evaluation_background
    pipeline_output = service._run_lighteval_task_pipeline(request)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 401, in _run_lighteval_task_pipeline
    pipeline = Pipeline(
               ^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 142, in __init__
    self._init_tasks_and_requests(tasks=tasks)
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 222, in _init_tasks_and_requests
    LightevalTask.load_datasets(self.tasks_dict, self.pipeline_parameters.dataset_loading_processes)
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 430, in load_datasets
    datasets = [task.download_dataset_worker(task) for task in tasks.values()]
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 457, in download_dataset_worker
    dataset = load_dataset(
              ^^^^^^^^^^^^^
  File "/home/rayhownh/.cache/pypoetry/virtualenvs/evalhub-YMyCob0K-py3.12/lib/python3.12/site-packages/datasets/load.py", line 1492, in load_dataset
    builder_instance = load_dataset_builder(
                       ^^^^^^^^^^^^^^^^^^^^^
  File "/home/rayhownh/.cache/pypoetry/virtualenvs/evalhub-YMyCob0K-py3.12/lib/python3.12/site-packages/datasets/load.py", line 1137, in load_dataset_builder
    dataset_module = dataset_module_factory(
                     ^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/rayhownh/.cache/pypoetry/virtualenvs/evalhub-YMyCob0K-py3.12/lib/python3.12/site-packages/datasets/load.py", line 1036, in dataset_module_factory
    raise e1 from None
  File "/home/rayhownh/.cache/pypoetry/virtualenvs/evalhub-YMyCob0K-py3.12/lib/python3.12/site-packages/datasets/load.py", line 994, in dataset_module_factory
    raise RuntimeError(f"Dataset scripts are no longer supported, but found {filename}")
RuntimeError: Dataset scripts are no longer supported, but found arithmetic.py

```

### story_cloze

**Task:** `storycloze:2016`
**Trace ID:** 505
**Duration:** 8.4s

**Error Message:**
```
BuilderConfig '2016' not found. Available: ['default']
```

**Full Traceback:**
```python
Traceback (most recent call last):
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 176, in _run_task_evaluation_background
    pipeline_output = service._run_lighteval_task_pipeline(request)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 401, in _run_lighteval_task_pipeline
    pipeline = Pipeline(
               ^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 142, in __init__
    self._init_tasks_and_requests(tasks=tasks)
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 222, in _init_tasks_and_requests
    LightevalTask.load_datasets(self.tasks_dict, self.pipeline_parameters.dataset_loading_processes)
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 430, in load_datasets
    datasets = [task.download_dataset_worker(task) for task in tasks.values()]
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 457, in download_dataset_worker
    dataset = load_dataset(
              ^^^^^^^^^^^^^
  File "/home/rayhownh/.cache/pypoetry/virtualenvs/evalhub-YMyCob0K-py3.12/lib/python3.12/site-packages/datasets/load.py", line 1492, in load_dataset
    builder_instance = load_dataset_builder(
                       ^^^^^^^^^^^^^^^^^^^^^
  File "/home/rayhownh/.cache/pypoetry/virtualenvs/evalhub-YMyCob0K-py3.12/lib/python3.12/site-packages/datasets/load.py", line 1171, in load_dataset_builder
    builder_instance: DatasetBuilder = builder_cls(
                                       ^^^^^^^^^^^^
  File "/home/rayhownh/.cache/pypoetry/virtualenvs/evalhub-YMyCob0K-py3.12/lib/python3.12/site-packages/datasets/builder.py", line 343, in __init__
    self.config, self.config_id = self._create_builder_config(
                                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/rayhownh/.cache/pypoetry/virtualenvs/evalhub-YMyCob0K-py3.12/lib/python3.12/site-packages/datasets/builder.py", line 530, in _create_builder_config
    raise ValueError(
ValueError: BuilderConfig '2016' not found. Available: ['default']

```

### IFBench_multi-turn

**Task:** `ifbench_multiturn`
**Trace ID:** 507
**Duration:** 36.7s

**Error Message:**
```
Through the use of Instruction, you requested the use of `syllapy` for this evaluation, but it is not available in your current environment. Please install it using pip.
```

**Full Traceback:**
```python
Traceback (most recent call last):
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 176, in _run_task_evaluation_background
    pipeline_output = service._run_lighteval_task_pipeline(request)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 409, in _run_lighteval_task_pipeline
    pipeline.evaluate()
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 291, in evaluate
    self._compute_metrics(outputs)
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 391, in _compute_metrics
    outputs = apply_metric(
              ^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/metrics/__init__.py", line 54, in apply_metric
    metric.compute_sample(
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/metrics/utils/metric_utils.py", line 58, in compute_sample
    return sample_level_fn(**kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/tasks/ifbench/main.py", line 75, in compute
    strict_result = evaluation_lib.test_instruction_following_strict(inp, prompt_to_response)
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/tasks/ifbench/evaluation_lib.py", line 87, in test_instruction_following_strict
    instruction = instruction_cls(instruction_id)
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/utils/imports.py", line 200, in __init__
    raise_if_package_not_available(backend, object_name=_object.__name__)
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/utils/imports.py", line 118, in raise_if_package_not_available
    raise ImportError(prefix + not_installed_error_message(package)[3:])
ImportError: Through the use of Instruction, you requested the use of `syllapy` for this evaluation, but it is not available in your current environment. Please install it using pip.

```

### lextreme

**Task:** `lextreme:brazilian_court_decisions_judgment`
**Trace ID:** 511
**Duration:** 9.2s

**Error Message:**
```
'validation'
```

**Full Traceback:**
```python
Traceback (most recent call last):
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 176, in _run_task_evaluation_background
    pipeline_output = service._run_lighteval_task_pipeline(request)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 401, in _run_lighteval_task_pipeline
    pipeline = Pipeline(
               ^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 142, in __init__
    self._init_tasks_and_requests(tasks=tasks)
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 224, in _init_tasks_and_requests
    task.full_name: task.get_docs(self.pipeline_parameters.max_samples) for _, task in self.tasks_dict.items()
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 382, in get_docs
    eval_docs = self.eval_docs()
                ^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 359, in eval_docs
    self._docs = self._get_docs_from_split(self.evaluation_split)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 302, in _get_docs_from_split
    for ix, item in enumerate(self.dataset[split]):
                              ~~~~~~~~~~~~^^^^^^^
  File "/home/rayhownh/.cache/pypoetry/virtualenvs/evalhub-YMyCob0K-py3.12/lib/python3.12/site-packages/datasets/dataset_dict.py", line 86, in __getitem__
    return super().__getitem__(k)
           ^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'validation'

```

### SimpleQA

**Task:** `simpleqa`
**Trace ID:** 512
**Duration:** 10.6s

**Error Message:**
```
'question'
```

**Full Traceback:**
```python
Traceback (most recent call last):
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 176, in _run_task_evaluation_background
    pipeline_output = service._run_lighteval_task_pipeline(request)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 401, in _run_lighteval_task_pipeline
    pipeline = Pipeline(
               ^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 142, in __init__
    self._init_tasks_and_requests(tasks=tasks)
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 224, in _init_tasks_and_requests
    task.full_name: task.get_docs(self.pipeline_parameters.max_samples) for _, task in self.tasks_dict.items()
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 382, in get_docs
    eval_docs = self.eval_docs()
                ^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 359, in eval_docs
    self._docs = self._get_docs_from_split(self.evaluation_split)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 309, in _get_docs_from_split
    doc = self.formatter(item, self.name)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/tasks/simpleqa.py", line 35, in simpleqa_prompt
    query = f"Question: {line['question']}\n"
                         ~~~~^^^^^^^^^^^^
KeyError: 'question'

```

### babi_qa

**Task:** `babi_qa`
**Trace ID:** 513
**Duration:** 7.1s

**Error Message:**
```
Dataset scripts are no longer supported, but found babi_qa.py
```

**Full Traceback:**
```python
Traceback (most recent call last):
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 176, in _run_task_evaluation_background
    pipeline_output = service._run_lighteval_task_pipeline(request)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 401, in _run_lighteval_task_pipeline
    pipeline = Pipeline(
               ^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 142, in __init__
    self._init_tasks_and_requests(tasks=tasks)
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 222, in _init_tasks_and_requests
    LightevalTask.load_datasets(self.tasks_dict, self.pipeline_parameters.dataset_loading_processes)
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 430, in load_datasets
    datasets = [task.download_dataset_worker(task) for task in tasks.values()]
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 457, in download_dataset_worker
    dataset = load_dataset(
              ^^^^^^^^^^^^^
  File "/home/rayhownh/.cache/pypoetry/virtualenvs/evalhub-YMyCob0K-py3.12/lib/python3.12/site-packages/datasets/load.py", line 1492, in load_dataset
    builder_instance = load_dataset_builder(
                       ^^^^^^^^^^^^^^^^^^^^^
  File "/home/rayhownh/.cache/pypoetry/virtualenvs/evalhub-YMyCob0K-py3.12/lib/python3.12/site-packages/datasets/load.py", line 1137, in load_dataset_builder
    dataset_module = dataset_module_factory(
                     ^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/rayhownh/.cache/pypoetry/virtualenvs/evalhub-YMyCob0K-py3.12/lib/python3.12/site-packages/datasets/load.py", line 1036, in dataset_module_factory
    raise e1 from None
  File "/home/rayhownh/.cache/pypoetry/virtualenvs/evalhub-YMyCob0K-py3.12/lib/python3.12/site-packages/datasets/load.py", line 994, in dataset_module_factory
    raise RuntimeError(f"Dataset scripts are no longer supported, but found {filename}")
RuntimeError: Dataset scripts are no longer supported, but found babi_qa.py

```

### SLR-Bench

**Task:** `slr_bench_all`
**Trace ID:** 514
**Duration:** 19.4s

**Error Message:**
```
Through the use of prompt_fn, you requested the use of `evaluate` for this evaluation, but it is not available in your current environment. Please install it using pip.
```

**Full Traceback:**
```python
Traceback (most recent call last):
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 176, in _run_task_evaluation_background
    pipeline_output = service._run_lighteval_task_pipeline(request)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 401, in _run_lighteval_task_pipeline
    pipeline = Pipeline(
               ^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 142, in __init__
    self._init_tasks_and_requests(tasks=tasks)
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 224, in _init_tasks_and_requests
    task.full_name: task.get_docs(self.pipeline_parameters.max_samples) for _, task in self.tasks_dict.items()
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 382, in get_docs
    eval_docs = self.eval_docs()
                ^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 359, in eval_docs
    self._docs = self._get_docs_from_split(self.evaluation_split)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 309, in _get_docs_from_split
    doc = self.formatter(item, self.name)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/utils/imports.py", line 211, in wrapper
    raise_if_package_not_available(backend, object_name=_object.__name__)
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/utils/imports.py", line 118, in raise_if_package_not_available
    raise ImportError(prefix + not_installed_error_message(package)[3:])
ImportError: Through the use of prompt_fn, you requested the use of `evaluate` for this evaluation, but it is not available in your current environment. Please install it using pip.

```

### MixEval

**Task:** `mixeval_easy:freeform`
**Trace ID:** 520
**Duration:** 14.8s

**Error Message:**
```
You requested the use of `vllm` for this evaluation, but it is not available in your current environment. Please install it using pip.
```

**Full Traceback:**
```python
Traceback (most recent call last):
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 176, in _run_task_evaluation_background
    pipeline_output = service._run_lighteval_task_pipeline(request)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 409, in _run_lighteval_task_pipeline
    pipeline.evaluate()
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 291, in evaluate
    self._compute_metrics(outputs)
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 391, in _compute_metrics
    outputs = apply_metric(
              ^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/metrics/__init__.py", line 40, in apply_metric
    metric_outputs = metric.compute_sample(responses=responses, docs=docs)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/metrics/utils/metric_utils.py", line 58, in compute_sample
    return sample_level_fn(**kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/metrics/metrics_sample.py", line 1093, in compute
    scores, messages, judgements = self.judge.evaluate_answer_batch(questions, predictions, options, golds)
                                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/metrics/utils/llm_as_judge.py", line 251, in evaluate_answer_batch
    judge_function = self.__lazy_load_client()
                     ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/metrics/utils/llm_as_judge.py", line 168, in __lazy_load_client
    raise_if_package_not_available("vllm")
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/utils/imports.py", line 118, in raise_if_package_not_available
    raise ImportError(prefix + not_installed_error_message(package)[3:])
ImportError: You requested the use of `vllm` for this evaluation, but it is not available in your current environment. Please install it using pip.

```

### summarization

**Task:** `summarization:cnn-dm`
**Trace ID:** 521
**Duration:** 12.9s

**Error Message:**
```
'highlights'
```

**Full Traceback:**
```python
Traceback (most recent call last):
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 176, in _run_task_evaluation_background
    pipeline_output = service._run_lighteval_task_pipeline(request)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 401, in _run_lighteval_task_pipeline
    pipeline = Pipeline(
               ^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 142, in __init__
    self._init_tasks_and_requests(tasks=tasks)
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 224, in _init_tasks_and_requests
    task.full_name: task.get_docs(self.pipeline_parameters.max_samples) for _, task in self.tasks_dict.items()
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 382, in get_docs
    eval_docs = self.eval_docs()
                ^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 359, in eval_docs
    self._docs = self._get_docs_from_split(self.evaluation_split)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 309, in _get_docs_from_split
    doc = self.formatter(item, self.name)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/tasks/summarization.py", line 33, in cnn_dm_prompt
    choices=[line["highlights"]],
             ~~~~^^^^^^^^^^^^^^
KeyError: 'highlights'

```

### lsat_qa

**Task:** `lsat_qa`
**Trace ID:** 522
**Duration:** 16.7s

**Error Message:**
```
'validation'
```

**Full Traceback:**
```python
Traceback (most recent call last):
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 176, in _run_task_evaluation_background
    pipeline_output = service._run_lighteval_task_pipeline(request)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 401, in _run_lighteval_task_pipeline
    pipeline = Pipeline(
               ^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 142, in __init__
    self._init_tasks_and_requests(tasks=tasks)
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 224, in _init_tasks_and_requests
    task.full_name: task.get_docs(self.pipeline_parameters.max_samples) for _, task in self.tasks_dict.items()
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 382, in get_docs
    eval_docs = self.eval_docs()
                ^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 359, in eval_docs
    self._docs = self._get_docs_from_split(self.evaluation_split)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 302, in _get_docs_from_split
    for ix, item in enumerate(self.dataset[split]):
                              ~~~~~~~~~~~~^^^^^^^
  File "/home/rayhownh/.cache/pypoetry/virtualenvs/evalhub-YMyCob0K-py3.12/lib/python3.12/site-packages/datasets/dataset_dict.py", line 86, in __getitem__
    return super().__getitem__(k)
           ^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'validation'

```

### legal_summarization

**Task:** `legal_summarization:billsum`
**Trace ID:** 525
**Duration:** 13.9s

**Error Message:**
```
'text'
```

**Full Traceback:**
```python
Traceback (most recent call last):
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 176, in _run_task_evaluation_background
    pipeline_output = service._run_lighteval_task_pipeline(request)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 401, in _run_lighteval_task_pipeline
    pipeline = Pipeline(
               ^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 142, in __init__
    self._init_tasks_and_requests(tasks=tasks)
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 224, in _init_tasks_and_requests
    task.full_name: task.get_docs(self.pipeline_parameters.max_samples) for _, task in self.tasks_dict.items()
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 382, in get_docs
    eval_docs = self.eval_docs()
                ^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 359, in eval_docs
    self._docs = self._get_docs_from_split(self.evaluation_split)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 309, in _get_docs_from_split
    doc = self.formatter(item, self.name)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/tasks/legal_summarization.py", line 30, in legal_summarization_prompt
    query=f"###\nArticle:{line['text']}\n\nSummarize the above article in 3 sentences.\n",
                          ~~~~^^^^^^^^
KeyError: 'text'

```

### mt-bench

**Task:** `mt_bench`
**Trace ID:** 529
**Duration:** 24.1s

**Error Message:**
```
list index out of range
```

**Full Traceback:**
```python
Traceback (most recent call last):
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 176, in _run_task_evaluation_background
    pipeline_output = service._run_lighteval_task_pipeline(request)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 409, in _run_lighteval_task_pipeline
    pipeline.evaluate()
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 291, in evaluate
    self._compute_metrics(outputs)
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 391, in _compute_metrics
    outputs = apply_metric(
              ^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/metrics/__init__.py", line 54, in apply_metric
    metric.compute_sample(
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/metrics/utils/metric_utils.py", line 58, in compute_sample
    return sample_level_fn(**kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/metrics/metrics_sample.py", line 1064, in compute
    query_context_2 = {"query": questions[1], "context": predictions[0]}
                                ~~~~~~~~~^^^
IndexError: list index out of range

```

### narrative_qa_helm

**Task:** `narrativeqa`
**Trace ID:** 535
**Duration:** 15.8s

**Error Message:**
```
list index out of range
```

**Full Traceback:**
```python
Traceback (most recent call last):
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 176, in _run_task_evaluation_background
    pipeline_output = service._run_lighteval_task_pipeline(request)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 409, in _run_lighteval_task_pipeline
    pipeline.evaluate()
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 291, in evaluate
    self._compute_metrics(outputs)
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 391, in _compute_metrics
    outputs = apply_metric(
              ^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/metrics/__init__.py", line 54, in apply_metric
    metric.compute_sample(
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/metrics/utils/metric_utils.py", line 59, in compute_sample
    return {self.metric_name: sample_level_fn(**kwargs)}
                              ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/metrics/metrics_sample.py", line 131, in compute
    golds = doc.get_golds()
            ^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/requests.py", line 222, in get_golds
    golds.extend(as_list(self.choices[gold_ix]))
                         ~~~~~~~~~~~~^^^^^^^^^
IndexError: list index out of range

```

### IMDB_helm

**Task:** `imdb`
**Trace ID:** 538
**Duration:** 14.0s

**Error Message:**
```
'LightevalTaskConfig' object is not callable
```

**Full Traceback:**
```python
Traceback (most recent call last):
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 176, in _run_task_evaluation_background
    pipeline_output = service._run_lighteval_task_pipeline(request)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 401, in _run_lighteval_task_pipeline
    pipeline = Pipeline(
               ^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 142, in __init__
    self._init_tasks_and_requests(tasks=tasks)
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 224, in _init_tasks_and_requests
    task.full_name: task.get_docs(self.pipeline_parameters.max_samples) for _, task in self.tasks_dict.items()
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 382, in get_docs
    eval_docs = self.eval_docs()
                ^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 359, in eval_docs
    self._docs = self._get_docs_from_split(self.evaluation_split)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 309, in _get_docs_from_split
    doc = self.formatter(item, self.name)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/tasks/imdb.py", line 38, in imdb_contrastset_prompt
    return imdb(line)
           ^^^^^^^^^^
TypeError: 'LightevalTaskConfig' object is not callable

```


## ⏱ Timeouts

_No timeouts_

## ⚠ Silent Failures

_These benchmarks completed but returned suspicious results (e.g., all zeros)_

### asdiv

**Task:** `asdiv`
**Trace ID:** 506
**Issue:** All scores are zero: {'em': {'std': 0.0, 'mean': 0.0, 'failed': 0}}

**Scores:**
```json
{
  "em": {
    "std": 0.0,
    "mean": 0.0,
    "failed": 0
  }
}
```

### drop_harness

**Task:** `drop`
**Trace ID:** 508
**Issue:** All scores are zero: {'em': {'std': 0.0, 'mean': 0.0, 'failed': 0}}

**Scores:**
```json
{
  "em": {
    "std": 0.0,
    "mean": 0.0,
    "failed": 0
  }
}
```

### lexglue

**Task:** `lexglue:case_hold`
**Trace ID:** 509
**Issue:** All scores are zero: {'em': {'std': 0.0, 'mean': 0.0, 'failed': 0}}

**Scores:**
```json
{
  "em": {
    "std": 0.0,
    "mean": 0.0,
    "failed": 0
  }
}
```

### wikifact

**Task:** `wikifact:applies_to_jurisdiction`
**Trace ID:** 510
**Issue:** All scores are zero: {'em': {'std': 0.0, 'mean': 0.0, 'failed': 0}}

**Scores:**
```json
{
  "em": {
    "std": 0.0,
    "mean": 0.0,
    "failed": 0
  }
}
```

### boolq_helm

**Task:** `boolq`
**Trace ID:** 515
**Issue:** All scores are zero: {'em': {'std': 0.0, 'mean': 0.0, 'failed': 0}}

**Scores:**
```json
{
  "em": {
    "std": 0.0,
    "mean": 0.0,
    "failed": 0
  }
}
```

### small_natural_questions

**Task:** `natural_questions`
**Trace ID:** 516
**Issue:** All scores are zero: {'em': {'std': 0.0, 'mean': 0.0, 'failed': 0}}

**Scores:**
```json
{
  "em": {
    "std": 0.0,
    "mean": 0.0,
    "failed": 0
  }
}
```

### bbq_helm

**Task:** `bbq`
**Trace ID:** 517
**Issue:** All scores are zero: {'em': {'std': 0.0, 'mean': 0.0, 'failed': 0}}

**Scores:**
```json
{
  "em": {
    "std": 0.0,
    "mean": 0.0,
    "failed": 0
  }
}
```

### med_dialog

**Task:** `med_dialog:healthcaremagic`
**Trace ID:** 518
**Issue:** All scores are zero: {'em': {'std': 0.0, 'mean': 0.0, 'failed': 0}}

**Scores:**
```json
{
  "em": {
    "std": 0.0,
    "mean": 0.0,
    "failed": 0
  }
}
```

### med_mcqa

**Task:** `med_mcqa`
**Trace ID:** 519
**Issue:** All scores are zero: {'em': {'std': 0.0, 'mean': 0.0, 'failed': 0}}

**Scores:**
```json
{
  "em": {
    "std": 0.0,
    "mean": 0.0,
    "failed": 0
  }
}
```

### numeracy

**Task:** `numeracy:linear_example`
**Trace ID:** 523
**Issue:** All scores are zero: {'em': {'std': 0.0, 'mean': 0.0, 'failed': 0}}

**Scores:**
```json
{
  "em": {
    "std": 0.0,
    "mean": 0.0,
    "failed": 0
  }
}
```

### DyckLanguage

**Task:** `dyck_language:2`
**Trace ID:** 524
**Issue:** All scores are zero: {'em': {'std': 0.0, 'mean': 0.0, 'failed': 0}}

**Scores:**
```json
{
  "em": {
    "std": 0.0,
    "mean": 0.0,
    "failed": 0
  }
}
```

### arc-agi-2

**Task:** `arc_agi_2`
**Trace ID:** 526
**Issue:** All scores are zero: {'em': {'std': 0.0, 'mean': 0.0, 'failed': 0}}

**Scores:**
```json
{
  "em": {
    "std": 0.0,
    "mean": 0.0,
    "failed": 0
  }
}
```

### EntityMatching

**Task:** `entity_matching:Abt_Buy`
**Trace ID:** 527
**Issue:** All scores are zero: {'em': {'std': 0.0, 'mean': 0.0, 'failed': 0}}

**Scores:**
```json
{
  "em": {
    "std": 0.0,
    "mean": 0.0,
    "failed": 0
  }
}
```

### med_paragraph_simplification

**Task:** `med_paragraph_simplification`
**Trace ID:** 528
**Issue:** All scores are zero: {'em': {'std': 0.0, 'mean': 0.0, 'failed': 0}}

**Scores:**
```json
{
  "em": {
    "std": 0.0,
    "mean": 0.0,
    "failed": 0
  }
}
```

### civil_comments_helm

**Task:** `civil_comments:LGBTQ`
**Trace ID:** 530
**Issue:** All scores are zero: {'em': {'std': 0.0, 'mean': 0.0, 'failed': 0}}

**Scores:**
```json
{
  "em": {
    "std": 0.0,
    "mean": 0.0,
    "failed": 0
  }
}
```

### synthetic_reasoning

**Task:** `synthetic_reasoning:induction`
**Trace ID:** 531
**Issue:** All scores are zero: {'em': {'std': 0.0, 'mean': 0.0, 'failed': 0}}

**Scores:**
```json
{
  "em": {
    "std": 0.0,
    "mean": 0.0,
    "failed": 0
  }
}
```

### covid_dialogue

**Task:** `covid_dialogue`
**Trace ID:** 533
**Issue:** All scores are zero: {'em': {'std': 0.0, 'mean': 0.0, 'failed': 0}}

**Scores:**
```json
{
  "em": {
    "std": 0.0,
    "mean": 0.0,
    "failed": 0
  }
}
```

### synthetic_reasoning_natural

**Task:** `synthetic_reasoning:natural_easy`
**Trace ID:** 534
**Issue:** All scores are zero: {'em': {'std': 0.0, 'mean': 0.0, 'failed': 0}}

**Scores:**
```json
{
  "em": {
    "std": 0.0,
    "mean": 0.0,
    "failed": 0
  }
}
```

### aimo_progress_prize_1

**Task:** `aimo_progress_prize_1`
**Trace ID:** 536
**Issue:** All scores are zero: {'em:normalize_gold=<function math_normalizer at 0x75654cb7b380>&normalize_pred=<function math_normalizer at 0x75654cb7b380>': {'std': 0.0, 'mean': 0.0, 'failed': 0}}

**Scores:**
```json
{
  "em:normalize_gold=<function math_normalizer at 0x75654cb7b380>&normalize_pred=<function math_normalizer at 0x75654cb7b380>": {
    "std": 0.0,
    "mean": 0.0,
    "failed": 0
  }
}
```

### Buy

**Task:** `entity_data_imputation:Buy`
**Trace ID:** 537
**Issue:** All scores are zero: {'em': {'std': 0.0, 'mean': 0.0, 'failed': 0}}

**Scores:**
```json
{
  "em": {
    "std": 0.0,
    "mean": 0.0,
    "failed": 0
  }
}
```

### quac_helm

**Task:** `quac`
**Trace ID:** 539
**Issue:** All scores are zero: {'em': {'std': 0.0, 'mean': 0.0, 'failed': 0}}

**Scores:**
```json
{
  "em": {
    "std": 0.0,
    "mean": 0.0,
    "failed": 0
  }
}
```

### GPT3_unscramble

**Task:** `unscramble:anagrams1`
**Trace ID:** 540
**Issue:** All scores are zero: {'em:strip_strings=False': {'std': 0.0, 'mean': 0.0, 'failed': 0}}

**Scores:**
```json
{
  "em:strip_strings=False": {
    "std": 0.0,
    "mean": 0.0,
    "failed": 0
  }
}
```

### Restaurant

**Task:** `entity_data_imputation:Restaurant`
**Trace ID:** 541
**Issue:** All scores are zero: {'em': {'std': 0.0, 'mean': 0.0, 'failed': 0}}

**Scores:**
```json
{
  "em": {
    "std": 0.0,
    "mean": 0.0,
    "failed": 0
  }
}
```


---

## 📋 Full Error Tracebacks

_Complete stack traces for all failed benchmarks for debugging purposes._

### AA-Omniscience-Public (`aa_omniscience`)

```python
Traceback (most recent call last):
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 176, in _run_task_evaluation_background
    pipeline_output = service._run_lighteval_task_pipeline(request)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 401, in _run_lighteval_task_pipeline
    pipeline = Pipeline(
               ^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 142, in __init__
    self._init_tasks_and_requests(tasks=tasks)
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 224, in _init_tasks_and_requests
    task.full_name: task.get_docs(self.pipeline_parameters.max_samples) for _, task in self.tasks_dict.items()
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 382, in get_docs
    eval_docs = self.eval_docs()
                ^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 359, in eval_docs
    self._docs = self._get_docs_from_split(self.evaluation_split)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 309, in _get_docs_from_split
    doc = self.formatter(item, self.name)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: aa_omniscience_prompt() takes 1 positional argument but 2 were given

```

### arithmetic (`arithmetic:1dc`)

```python
Traceback (most recent call last):
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 176, in _run_task_evaluation_background
    pipeline_output = service._run_lighteval_task_pipeline(request)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 401, in _run_lighteval_task_pipeline
    pipeline = Pipeline(
               ^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 142, in __init__
    self._init_tasks_and_requests(tasks=tasks)
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 222, in _init_tasks_and_requests
    LightevalTask.load_datasets(self.tasks_dict, self.pipeline_parameters.dataset_loading_processes)
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 430, in load_datasets
    datasets = [task.download_dataset_worker(task) for task in tasks.values()]
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 457, in download_dataset_worker
    dataset = load_dataset(
              ^^^^^^^^^^^^^
  File "/home/rayhownh/.cache/pypoetry/virtualenvs/evalhub-YMyCob0K-py3.12/lib/python3.12/site-packages/datasets/load.py", line 1492, in load_dataset
    builder_instance = load_dataset_builder(
                       ^^^^^^^^^^^^^^^^^^^^^
  File "/home/rayhownh/.cache/pypoetry/virtualenvs/evalhub-YMyCob0K-py3.12/lib/python3.12/site-packages/datasets/load.py", line 1137, in load_dataset_builder
    dataset_module = dataset_module_factory(
                     ^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/rayhownh/.cache/pypoetry/virtualenvs/evalhub-YMyCob0K-py3.12/lib/python3.12/site-packages/datasets/load.py", line 1036, in dataset_module_factory
    raise e1 from None
  File "/home/rayhownh/.cache/pypoetry/virtualenvs/evalhub-YMyCob0K-py3.12/lib/python3.12/site-packages/datasets/load.py", line 994, in dataset_module_factory
    raise RuntimeError(f"Dataset scripts are no longer supported, but found {filename}")
RuntimeError: Dataset scripts are no longer supported, but found arithmetic.py

```

### story_cloze (`storycloze:2016`)

```python
Traceback (most recent call last):
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 176, in _run_task_evaluation_background
    pipeline_output = service._run_lighteval_task_pipeline(request)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 401, in _run_lighteval_task_pipeline
    pipeline = Pipeline(
               ^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 142, in __init__
    self._init_tasks_and_requests(tasks=tasks)
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 222, in _init_tasks_and_requests
    LightevalTask.load_datasets(self.tasks_dict, self.pipeline_parameters.dataset_loading_processes)
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 430, in load_datasets
    datasets = [task.download_dataset_worker(task) for task in tasks.values()]
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 457, in download_dataset_worker
    dataset = load_dataset(
              ^^^^^^^^^^^^^
  File "/home/rayhownh/.cache/pypoetry/virtualenvs/evalhub-YMyCob0K-py3.12/lib/python3.12/site-packages/datasets/load.py", line 1492, in load_dataset
    builder_instance = load_dataset_builder(
                       ^^^^^^^^^^^^^^^^^^^^^
  File "/home/rayhownh/.cache/pypoetry/virtualenvs/evalhub-YMyCob0K-py3.12/lib/python3.12/site-packages/datasets/load.py", line 1171, in load_dataset_builder
    builder_instance: DatasetBuilder = builder_cls(
                                       ^^^^^^^^^^^^
  File "/home/rayhownh/.cache/pypoetry/virtualenvs/evalhub-YMyCob0K-py3.12/lib/python3.12/site-packages/datasets/builder.py", line 343, in __init__
    self.config, self.config_id = self._create_builder_config(
                                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/rayhownh/.cache/pypoetry/virtualenvs/evalhub-YMyCob0K-py3.12/lib/python3.12/site-packages/datasets/builder.py", line 530, in _create_builder_config
    raise ValueError(
ValueError: BuilderConfig '2016' not found. Available: ['default']

```

### IFBench_multi-turn (`ifbench_multiturn`)

```python
Traceback (most recent call last):
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 176, in _run_task_evaluation_background
    pipeline_output = service._run_lighteval_task_pipeline(request)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 409, in _run_lighteval_task_pipeline
    pipeline.evaluate()
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 291, in evaluate
    self._compute_metrics(outputs)
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 391, in _compute_metrics
    outputs = apply_metric(
              ^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/metrics/__init__.py", line 54, in apply_metric
    metric.compute_sample(
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/metrics/utils/metric_utils.py", line 58, in compute_sample
    return sample_level_fn(**kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/tasks/ifbench/main.py", line 75, in compute
    strict_result = evaluation_lib.test_instruction_following_strict(inp, prompt_to_response)
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/tasks/ifbench/evaluation_lib.py", line 87, in test_instruction_following_strict
    instruction = instruction_cls(instruction_id)
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/utils/imports.py", line 200, in __init__
    raise_if_package_not_available(backend, object_name=_object.__name__)
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/utils/imports.py", line 118, in raise_if_package_not_available
    raise ImportError(prefix + not_installed_error_message(package)[3:])
ImportError: Through the use of Instruction, you requested the use of `syllapy` for this evaluation, but it is not available in your current environment. Please install it using pip.

```

### lextreme (`lextreme:brazilian_court_decisions_judgment`)

```python
Traceback (most recent call last):
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 176, in _run_task_evaluation_background
    pipeline_output = service._run_lighteval_task_pipeline(request)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 401, in _run_lighteval_task_pipeline
    pipeline = Pipeline(
               ^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 142, in __init__
    self._init_tasks_and_requests(tasks=tasks)
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 224, in _init_tasks_and_requests
    task.full_name: task.get_docs(self.pipeline_parameters.max_samples) for _, task in self.tasks_dict.items()
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 382, in get_docs
    eval_docs = self.eval_docs()
                ^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 359, in eval_docs
    self._docs = self._get_docs_from_split(self.evaluation_split)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 302, in _get_docs_from_split
    for ix, item in enumerate(self.dataset[split]):
                              ~~~~~~~~~~~~^^^^^^^
  File "/home/rayhownh/.cache/pypoetry/virtualenvs/evalhub-YMyCob0K-py3.12/lib/python3.12/site-packages/datasets/dataset_dict.py", line 86, in __getitem__
    return super().__getitem__(k)
           ^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'validation'

```

### SimpleQA (`simpleqa`)

```python
Traceback (most recent call last):
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 176, in _run_task_evaluation_background
    pipeline_output = service._run_lighteval_task_pipeline(request)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 401, in _run_lighteval_task_pipeline
    pipeline = Pipeline(
               ^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 142, in __init__
    self._init_tasks_and_requests(tasks=tasks)
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 224, in _init_tasks_and_requests
    task.full_name: task.get_docs(self.pipeline_parameters.max_samples) for _, task in self.tasks_dict.items()
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 382, in get_docs
    eval_docs = self.eval_docs()
                ^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 359, in eval_docs
    self._docs = self._get_docs_from_split(self.evaluation_split)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 309, in _get_docs_from_split
    doc = self.formatter(item, self.name)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/tasks/simpleqa.py", line 35, in simpleqa_prompt
    query = f"Question: {line['question']}\n"
                         ~~~~^^^^^^^^^^^^
KeyError: 'question'

```

### babi_qa (`babi_qa`)

```python
Traceback (most recent call last):
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 176, in _run_task_evaluation_background
    pipeline_output = service._run_lighteval_task_pipeline(request)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 401, in _run_lighteval_task_pipeline
    pipeline = Pipeline(
               ^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 142, in __init__
    self._init_tasks_and_requests(tasks=tasks)
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 222, in _init_tasks_and_requests
    LightevalTask.load_datasets(self.tasks_dict, self.pipeline_parameters.dataset_loading_processes)
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 430, in load_datasets
    datasets = [task.download_dataset_worker(task) for task in tasks.values()]
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 457, in download_dataset_worker
    dataset = load_dataset(
              ^^^^^^^^^^^^^
  File "/home/rayhownh/.cache/pypoetry/virtualenvs/evalhub-YMyCob0K-py3.12/lib/python3.12/site-packages/datasets/load.py", line 1492, in load_dataset
    builder_instance = load_dataset_builder(
                       ^^^^^^^^^^^^^^^^^^^^^
  File "/home/rayhownh/.cache/pypoetry/virtualenvs/evalhub-YMyCob0K-py3.12/lib/python3.12/site-packages/datasets/load.py", line 1137, in load_dataset_builder
    dataset_module = dataset_module_factory(
                     ^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/rayhownh/.cache/pypoetry/virtualenvs/evalhub-YMyCob0K-py3.12/lib/python3.12/site-packages/datasets/load.py", line 1036, in dataset_module_factory
    raise e1 from None
  File "/home/rayhownh/.cache/pypoetry/virtualenvs/evalhub-YMyCob0K-py3.12/lib/python3.12/site-packages/datasets/load.py", line 994, in dataset_module_factory
    raise RuntimeError(f"Dataset scripts are no longer supported, but found {filename}")
RuntimeError: Dataset scripts are no longer supported, but found babi_qa.py

```

### SLR-Bench (`slr_bench_all`)

```python
Traceback (most recent call last):
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 176, in _run_task_evaluation_background
    pipeline_output = service._run_lighteval_task_pipeline(request)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 401, in _run_lighteval_task_pipeline
    pipeline = Pipeline(
               ^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 142, in __init__
    self._init_tasks_and_requests(tasks=tasks)
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 224, in _init_tasks_and_requests
    task.full_name: task.get_docs(self.pipeline_parameters.max_samples) for _, task in self.tasks_dict.items()
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 382, in get_docs
    eval_docs = self.eval_docs()
                ^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 359, in eval_docs
    self._docs = self._get_docs_from_split(self.evaluation_split)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 309, in _get_docs_from_split
    doc = self.formatter(item, self.name)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/utils/imports.py", line 211, in wrapper
    raise_if_package_not_available(backend, object_name=_object.__name__)
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/utils/imports.py", line 118, in raise_if_package_not_available
    raise ImportError(prefix + not_installed_error_message(package)[3:])
ImportError: Through the use of prompt_fn, you requested the use of `evaluate` for this evaluation, but it is not available in your current environment. Please install it using pip.

```

### MixEval (`mixeval_easy:freeform`)

```python
Traceback (most recent call last):
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 176, in _run_task_evaluation_background
    pipeline_output = service._run_lighteval_task_pipeline(request)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 409, in _run_lighteval_task_pipeline
    pipeline.evaluate()
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 291, in evaluate
    self._compute_metrics(outputs)
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 391, in _compute_metrics
    outputs = apply_metric(
              ^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/metrics/__init__.py", line 40, in apply_metric
    metric_outputs = metric.compute_sample(responses=responses, docs=docs)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/metrics/utils/metric_utils.py", line 58, in compute_sample
    return sample_level_fn(**kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/metrics/metrics_sample.py", line 1093, in compute
    scores, messages, judgements = self.judge.evaluate_answer_batch(questions, predictions, options, golds)
                                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/metrics/utils/llm_as_judge.py", line 251, in evaluate_answer_batch
    judge_function = self.__lazy_load_client()
                     ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/metrics/utils/llm_as_judge.py", line 168, in __lazy_load_client
    raise_if_package_not_available("vllm")
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/utils/imports.py", line 118, in raise_if_package_not_available
    raise ImportError(prefix + not_installed_error_message(package)[3:])
ImportError: You requested the use of `vllm` for this evaluation, but it is not available in your current environment. Please install it using pip.

```

### summarization (`summarization:cnn-dm`)

```python
Traceback (most recent call last):
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 176, in _run_task_evaluation_background
    pipeline_output = service._run_lighteval_task_pipeline(request)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 401, in _run_lighteval_task_pipeline
    pipeline = Pipeline(
               ^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 142, in __init__
    self._init_tasks_and_requests(tasks=tasks)
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 224, in _init_tasks_and_requests
    task.full_name: task.get_docs(self.pipeline_parameters.max_samples) for _, task in self.tasks_dict.items()
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 382, in get_docs
    eval_docs = self.eval_docs()
                ^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 359, in eval_docs
    self._docs = self._get_docs_from_split(self.evaluation_split)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 309, in _get_docs_from_split
    doc = self.formatter(item, self.name)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/tasks/summarization.py", line 33, in cnn_dm_prompt
    choices=[line["highlights"]],
             ~~~~^^^^^^^^^^^^^^
KeyError: 'highlights'

```

### lsat_qa (`lsat_qa`)

```python
Traceback (most recent call last):
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 176, in _run_task_evaluation_background
    pipeline_output = service._run_lighteval_task_pipeline(request)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 401, in _run_lighteval_task_pipeline
    pipeline = Pipeline(
               ^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 142, in __init__
    self._init_tasks_and_requests(tasks=tasks)
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 224, in _init_tasks_and_requests
    task.full_name: task.get_docs(self.pipeline_parameters.max_samples) for _, task in self.tasks_dict.items()
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 382, in get_docs
    eval_docs = self.eval_docs()
                ^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 359, in eval_docs
    self._docs = self._get_docs_from_split(self.evaluation_split)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 302, in _get_docs_from_split
    for ix, item in enumerate(self.dataset[split]):
                              ~~~~~~~~~~~~^^^^^^^
  File "/home/rayhownh/.cache/pypoetry/virtualenvs/evalhub-YMyCob0K-py3.12/lib/python3.12/site-packages/datasets/dataset_dict.py", line 86, in __getitem__
    return super().__getitem__(k)
           ^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'validation'

```

### legal_summarization (`legal_summarization:billsum`)

```python
Traceback (most recent call last):
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 176, in _run_task_evaluation_background
    pipeline_output = service._run_lighteval_task_pipeline(request)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 401, in _run_lighteval_task_pipeline
    pipeline = Pipeline(
               ^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 142, in __init__
    self._init_tasks_and_requests(tasks=tasks)
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 224, in _init_tasks_and_requests
    task.full_name: task.get_docs(self.pipeline_parameters.max_samples) for _, task in self.tasks_dict.items()
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 382, in get_docs
    eval_docs = self.eval_docs()
                ^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 359, in eval_docs
    self._docs = self._get_docs_from_split(self.evaluation_split)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 309, in _get_docs_from_split
    doc = self.formatter(item, self.name)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/tasks/legal_summarization.py", line 30, in legal_summarization_prompt
    query=f"###\nArticle:{line['text']}\n\nSummarize the above article in 3 sentences.\n",
                          ~~~~^^^^^^^^
KeyError: 'text'

```

### mt-bench (`mt_bench`)

```python
Traceback (most recent call last):
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 176, in _run_task_evaluation_background
    pipeline_output = service._run_lighteval_task_pipeline(request)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 409, in _run_lighteval_task_pipeline
    pipeline.evaluate()
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 291, in evaluate
    self._compute_metrics(outputs)
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 391, in _compute_metrics
    outputs = apply_metric(
              ^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/metrics/__init__.py", line 54, in apply_metric
    metric.compute_sample(
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/metrics/utils/metric_utils.py", line 58, in compute_sample
    return sample_level_fn(**kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/metrics/metrics_sample.py", line 1064, in compute
    query_context_2 = {"query": questions[1], "context": predictions[0]}
                                ~~~~~~~~~^^^
IndexError: list index out of range

```

### narrative_qa_helm (`narrativeqa`)

```python
Traceback (most recent call last):
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 176, in _run_task_evaluation_background
    pipeline_output = service._run_lighteval_task_pipeline(request)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 409, in _run_lighteval_task_pipeline
    pipeline.evaluate()
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 291, in evaluate
    self._compute_metrics(outputs)
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 391, in _compute_metrics
    outputs = apply_metric(
              ^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/metrics/__init__.py", line 54, in apply_metric
    metric.compute_sample(
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/metrics/utils/metric_utils.py", line 59, in compute_sample
    return {self.metric_name: sample_level_fn(**kwargs)}
                              ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/metrics/metrics_sample.py", line 131, in compute
    golds = doc.get_golds()
            ^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/requests.py", line 222, in get_golds
    golds.extend(as_list(self.choices[gold_ix]))
                         ~~~~~~~~~~~~^^^^^^^^^
IndexError: list index out of range

```

### IMDB_helm (`imdb`)

```python
Traceback (most recent call last):
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 176, in _run_task_evaluation_background
    pipeline_output = service._run_lighteval_task_pipeline(request)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 401, in _run_lighteval_task_pipeline
    pipeline = Pipeline(
               ^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 142, in __init__
    self._init_tasks_and_requests(tasks=tasks)
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 224, in _init_tasks_and_requests
    task.full_name: task.get_docs(self.pipeline_parameters.max_samples) for _, task in self.tasks_dict.items()
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 382, in get_docs
    eval_docs = self.eval_docs()
                ^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 359, in eval_docs
    self._docs = self._get_docs_from_split(self.evaluation_split)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 309, in _get_docs_from_split
    doc = self.formatter(item, self.name)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/tasks/imdb.py", line 38, in imdb_contrastset_prompt
    return imdb(line)
           ^^^^^^^^^^
TypeError: 'LightevalTaskConfig' object is not callable

```
