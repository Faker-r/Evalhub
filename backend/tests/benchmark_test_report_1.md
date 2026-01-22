# Benchmark Compatibility Test Report

**Generated:** 2026-01-21T16:35:54.955292
**Test Duration:** 543.0 seconds

## Summary

| Metric | Count |
|--------|-------|
| Total Benchmarks Tested | 35 |
| ✓ Successful | 7 |
| ✗ Failed | 17 |
| ⚠ Silent Failures | 11 |
| ⏱ Timeouts | 0 |

**Success Rate:** 20.0%

## ✓ Successful Benchmarks

| Dataset | Task | Trace ID | Duration (s) | Scores |
|---------|------|----------|--------------|--------|
| gsm8k | gsm8k | 466 | 16.0 | extractive_match: {'std': 0.24, 'mean': 0.6, 'failed': 0} |
| hellaswag | hellaswag | 467 | 10.9 | em: {'std': 0.2, 'mean': 0.2, 'failed': 0} |
| MMLU-Pro | mmlu_pro | 470 | 22.5 | extractive_match: {'std': 0.24, 'mean': 0.4, 'failed': 0} |
| commonsense_qa | commonsenseqa | 476 | 10.1 | em: {'std': 0.24, 'mean': 0.4, 'failed': 0} |
| emotion | emotion_classification | 480 | 10.9 | exact_match: {'std': 0.2, 'mean': 0.8, 'failed': 0}, total_samples: {'std': 0.0, 'mean': 5.0, 'failed': 0}, unknown_prediction: {'std': 0.0, 'mean': 0.0, 'failed': 0} |
| sacrebleu_manual | wmt14:de-en | 492 | 15.3 | ter: {'std': 0.56, 'mean': 47.17, 'failed': 0}, bleu: {'std': 0.24, 'mean': 46.1, 'failed': 0}, chrf: {'std': 0.42, 'mean': 60.96, 'failed': 0} |
| GSM-Plus | gsm_plus | 498 | 24.8 | extractive_match: {'std': 0.2, 'mean': 0.8, 'failed': 0} |

## ✗ Failed Benchmarks

### gpqa

**Task:** `gpqa:diamond`
**Trace ID:** 471
**Duration:** 6.6s

**Error Message:**
```
Dataset 'Idavidrein/gpqa' is a gated dataset on the Hub. Visit the dataset page at https://huggingface.co/datasets/Idavidrein/gpqa to ask for access.
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
  File "/home/rayhownh/.cache/pypoetry/virtualenvs/evalhub-YMyCob0K-py3.12/lib/python3.12/site-packages/datasets/load.py", line 1030, in dataset_module_factory
    raise e1 from None
  File "/home/rayhownh/.cache/pypoetry/virtualenvs/evalhub-YMyCob0K-py3.12/lib/python3.12/site-packages/datasets/load.py", line 1016, in dataset_module_factory
    raise DatasetNotFoundError(message) from e
datasets.exceptions.DatasetNotFoundError: Dataset 'Idavidrein/gpqa' is a gated dataset on the Hub. Visit the dataset page at https://huggingface.co/datasets/Idavidrein/gpqa to ask for access.

```

### truthful_qa

**Task:** `truthfulqa:gen`
**Trace ID:** 472
**Duration:** 7.4s

**Error Message:**
```
'mc1_targets'
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
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/tasks/truthfulqa.py", line 54, in truthful_qa_generative_prompt
    specific={"len_mc1": len(line["mc1_targets"]["choices"])},
                             ~~~~^^^^^^^^^^^^^^^
KeyError: 'mc1_targets'

```

### piqa

**Task:** `piqa`
**Trace ID:** 474
**Duration:** 6.9s

**Error Message:**
```
Dataset scripts are no longer supported, but found piqa.py
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
RuntimeError: Dataset scripts are no longer supported, but found piqa.py

```

### IFEval

**Task:** `ifeval`
**Trace ID:** 475
**Duration:** 8.2s

**Error Message:**
```
Through the use of ifeval_prompt, you requested the use of `langdetect` for this evaluation, but it is not available in your current environment. Please install it using pip.
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
ImportError: Through the use of ifeval_prompt, you requested the use of `langdetect` for this evaluation, but it is not available in your current environment. Please install it using pip.

```

### pubmed_qa

**Task:** `pubmedqa`
**Trace ID:** 479
**Duration:** 9.5s

**Error Message:**
```
'QUESTION'
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
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/tasks/pubmedqa.py", line 29, in pubmed_qa_prompt
    query=f"{line['QUESTION']}\n{line['CONTEXTS']}\nAnswer: ",
             ~~~~^^^^^^^^^^^^
KeyError: 'QUESTION'

```

### social_i_qa

**Task:** `siqa`
**Trace ID:** 481
**Duration:** 6.5s

**Error Message:**
```
Dataset scripts are no longer supported, but found social_i_qa.py
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
RuntimeError: Dataset scripts are no longer supported, but found social_i_qa.py

```

### hle

**Task:** `hle`
**Trace ID:** 482
**Duration:** 6.5s

**Error Message:**
```
Dataset 'cais/hle' is a gated dataset on the Hub. Visit the dataset page at https://huggingface.co/datasets/cais/hle to ask for access.
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
  File "/home/rayhownh/.cache/pypoetry/virtualenvs/evalhub-YMyCob0K-py3.12/lib/python3.12/site-packages/datasets/load.py", line 1030, in dataset_module_factory
    raise e1 from None
  File "/home/rayhownh/.cache/pypoetry/virtualenvs/evalhub-YMyCob0K-py3.12/lib/python3.12/site-packages/datasets/load.py", line 1016, in dataset_module_factory
    raise DatasetNotFoundError(message) from e
datasets.exceptions.DatasetNotFoundError: Dataset 'cais/hle' is a gated dataset on the Hub. Visit the dataset page at https://huggingface.co/datasets/cais/hle to ask for access.

```

### med_qa

**Task:** `med_qa`
**Trace ID:** 486
**Duration:** 6.6s

**Error Message:**
```
Dataset scripts are no longer supported, but found med_qa.py
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
RuntimeError: Dataset scripts are no longer supported, but found med_qa.py

```

### coqa

**Task:** `coqa`
**Trace ID:** 488
**Duration:** 7.8s

**Error Message:**
```
'list' object has no attribute 'id'
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
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 314, in _get_docs_from_split
    doc.id = str(ix)
    ^^^^^^
AttributeError: 'list' object has no attribute 'id'

```

### mgsm

**Task:** `mgsm:bn`
**Trace ID:** 490
**Duration:** 6.5s

**Error Message:**
```
Dataset scripts are no longer supported, but found mgsm.py
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
RuntimeError: Dataset scripts are no longer supported, but found mgsm.py

```

### real-toxicity-prompts

**Task:** `real_toxicity_prompts`
**Trace ID:** 491
**Duration:** 17.4s

**Error Message:**
```
'NoneType' object is not subscriptable
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
TypeError: 'NoneType' object is not subscriptable

```

### bigbench

**Task:** `bigbench:mult_data_wrangling`
**Trace ID:** 493
**Duration:** 8.4s

**Error Message:**
```
'default'
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
KeyError: 'default'

```

### tinyGSM8k

**Task:** `tiny:gsm8k`
**Trace ID:** 495
**Duration:** 19.0s

**Error Message:**
```
[Errno 2] No such file or directory: 'extended_tasks/tiny_benchmarks/tinyBenchmarks.pkl'
```

**Full Traceback:**
```python
Traceback (most recent call last):
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 176, in _run_task_evaluation_background
    pipeline_output = service._run_lighteval_task_pipeline(request)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 409, in _run_lighteval_task_pipeline
    pipeline.evaluate()
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 294, in evaluate
    self.evaluation_tracker.metrics_logger.aggregate(
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/logging/info_loggers.py", line 349, in aggregate
    metric_result = aggregation(metric_values)
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/tasks/tiny_benchmarks.py", line 119, in compute_corpus
    with open("extended_tasks/tiny_benchmarks/tinyBenchmarks.pkl", "rb") as handle:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
FileNotFoundError: [Errno 2] No such file or directory: 'extended_tasks/tiny_benchmarks/tinyBenchmarks.pkl'

```

### IFBench_test

**Task:** `ifbench_test`
**Trace ID:** 496
**Duration:** 31.9s

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

### OlympiadBench

**Task:** `olympiad_bench:OE_TO_maths_en_COMP`
**Trace ID:** 497
**Duration:** 43.3s

**Error Message:**
```
Cannot write struct type 'specific' with no child field to Parquet. Consider adding a dummy child field.
```

**Full Traceback:**
```python
Traceback (most recent call last):
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 176, in _run_task_evaluation_background
    pipeline_output = service._run_lighteval_task_pipeline(request)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 410, in _run_lighteval_task_pipeline
    pipeline.save_and_push_results()
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 429, in save_and_push_results
    self.evaluation_tracker.save()
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/logging/evaluation_tracker.py", line 273, in save
    self.save_details(date_id, details_datasets)
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/logging/evaluation_tracker.py", line 361, in save_details
    dataset.to_parquet(f)
  File "/home/rayhownh/.cache/pypoetry/virtualenvs/evalhub-YMyCob0K-py3.12/lib/python3.12/site-packages/datasets/arrow_dataset.py", line 5295, in to_parquet
    ).write()
      ^^^^^^^
  File "/home/rayhownh/.cache/pypoetry/virtualenvs/evalhub-YMyCob0K-py3.12/lib/python3.12/site-packages/datasets/io/parquet.py", line 108, in write
    written = self._write(
              ^^^^^^^^^^^^
  File "/home/rayhownh/.cache/pypoetry/virtualenvs/evalhub-YMyCob0K-py3.12/lib/python3.12/site-packages/datasets/io/parquet.py", line 124, in _write
    writer = pq.ParquetWriter(
             ^^^^^^^^^^^^^^^^^
  File "/home/rayhownh/.cache/pypoetry/virtualenvs/evalhub-YMyCob0K-py3.12/lib/python3.12/site-packages/pyarrow/parquet/core.py", line 1070, in __init__
    self.writer = _parquet.ParquetWriter(
                  ^^^^^^^^^^^^^^^^^^^^^^^
  File "pyarrow/_parquet.pyx", line 2363, in pyarrow._parquet.ParquetWriter.__cinit__
  File "pyarrow/error.pxi", line 155, in pyarrow.lib.pyarrow_internal_check_status
  File "pyarrow/error.pxi", line 92, in pyarrow.lib.check_status
pyarrow.lib.ArrowNotImplementedError: Cannot write struct type 'specific' with no child field to Parquet. Consider adding a dummy child field.

```

### qasper

**Task:** `qasper`
**Trace ID:** 499
**Duration:** 6.6s

**Error Message:**
```
Dataset scripts are no longer supported, but found qasper.py
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
RuntimeError: Dataset scripts are no longer supported, but found qasper.py

```

### raft

**Task:** `raft:ade_corpus_v2`
**Trace ID:** 500
**Duration:** 7.0s

**Error Message:**
```
Dataset scripts are no longer supported, but found raft.py
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
RuntimeError: Dataset scripts are no longer supported, but found raft.py

```


## ⏱ Timeouts

_No timeouts_

## ⚠ Silent Failures

_These benchmarks completed but returned suspicious results (e.g., all zeros)_

### MATH-500

**Task:** `math_500`
**Trace ID:** 468
**Issue:** All scores are zero: {'pass@k:k=1&n=1': {'std': 0.0, 'mean': 0.0, 'failed': 0}}

**Scores:**
```json
{
  "pass@k:k=1&n=1": {
    "std": 0.0,
    "mean": 0.0,
    "failed": 0
  }
}
```

### openbookqa

**Task:** `openbookqa`
**Trace ID:** 469
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

### trivia_qa

**Task:** `triviaqa`
**Trace ID:** 473
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

### aime_2024

**Task:** `aime24`
**Trace ID:** 477
**Issue:** All scores are zero: {'avg@n:n=1': {'std': 0.0, 'mean': 0.0, 'failed': 0}, 'pass@k:k=1': {'std': 0.0, 'mean': 0.0, 'failed': 0}}

**Scores:**
```json
{
  "avg@n:n=1": {
    "std": 0.0,
    "mean": 0.0,
    "failed": 0
  },
  "pass@k:k=1": {
    "std": 0.0,
    "mean": 0.0,
    "failed": 0
  }
}
```

### squad_v2

**Task:** `squad_v2`
**Trace ID:** 478
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

### aime_2025

**Task:** `aime25`
**Trace ID:** 483
**Issue:** All scores are zero: {'avg@n:n=1': {'std': 0.0, 'mean': 0.0, 'failed': 0}, 'pass@k:k=1&n=1': {'std': 0.0, 'mean': 0.0, 'failed': 0}}

**Scores:**
```json
{
  "avg@n:n=1": {
    "std": 0.0,
    "mean": 0.0,
    "failed": 0
  },
  "pass@k:k=1&n=1": {
    "std": 0.0,
    "mean": 0.0,
    "failed": 0
  }
}
```

### MATH-lighteval

**Task:** `math:algebra`
**Trace ID:** 484
**Issue:** All scores are zero: {'maj@n:n=4&strip_strings=True&normalize_pred=<function math_normalizer at 0x7c4e7779b2e0>&normalize_gold=<function math_normalizer at 0x7c4e7779b2e0>': {'std': 0.0, 'mean': 0.0, 'failed': 0}}

**Scores:**
```json
{
  "maj@n:n=4&strip_strings=True&normalize_pred=<function math_normalizer at 0x7c4e7779b2e0>&normalize_gold=<function math_normalizer at 0x7c4e7779b2e0>": {
    "std": 0.0,
    "mean": 0.0,
    "failed": 0
  }
}
```

### web_questions

**Task:** `webqs`
**Trace ID:** 485
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

### MMMU_pro

**Task:** `mmmu_pro:standard-10`
**Trace ID:** 487
**Issue:** All scores are zero: {'extractive_match': {'std': 0.0, 'mean': 0.0, 'failed': 0}}

**Scores:**
```json
{
  "extractive_match": {
    "std": 0.0,
    "mean": 0.0,
    "failed": 0
  }
}
```

### mmlu

**Task:** `mmlu:abstract_algebra`
**Trace ID:** 489
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

### code_generation_lite

**Task:** `lcb:codegeneration`
**Trace ID:** 494
**Issue:** All scores are zero: {'codegen_pass@1:16': {'std': 0.0, 'mean': 0.0, 'failed': 0}}

**Scores:**
```json
{
  "codegen_pass@1:16": {
    "std": 0.0,
    "mean": 0.0,
    "failed": 0
  }
}
```


---

## 📋 Full Error Tracebacks

_Complete stack traces for all failed benchmarks for debugging purposes._

### gpqa (`gpqa:diamond`)

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
  File "/home/rayhownh/.cache/pypoetry/virtualenvs/evalhub-YMyCob0K-py3.12/lib/python3.12/site-packages/datasets/load.py", line 1030, in dataset_module_factory
    raise e1 from None
  File "/home/rayhownh/.cache/pypoetry/virtualenvs/evalhub-YMyCob0K-py3.12/lib/python3.12/site-packages/datasets/load.py", line 1016, in dataset_module_factory
    raise DatasetNotFoundError(message) from e
datasets.exceptions.DatasetNotFoundError: Dataset 'Idavidrein/gpqa' is a gated dataset on the Hub. Visit the dataset page at https://huggingface.co/datasets/Idavidrein/gpqa to ask for access.

```

### truthful_qa (`truthfulqa:gen`)

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
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/tasks/truthfulqa.py", line 54, in truthful_qa_generative_prompt
    specific={"len_mc1": len(line["mc1_targets"]["choices"])},
                             ~~~~^^^^^^^^^^^^^^^
KeyError: 'mc1_targets'

```

### piqa (`piqa`)

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
RuntimeError: Dataset scripts are no longer supported, but found piqa.py

```

### IFEval (`ifeval`)

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
ImportError: Through the use of ifeval_prompt, you requested the use of `langdetect` for this evaluation, but it is not available in your current environment. Please install it using pip.

```

### pubmed_qa (`pubmedqa`)

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
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/tasks/pubmedqa.py", line 29, in pubmed_qa_prompt
    query=f"{line['QUESTION']}\n{line['CONTEXTS']}\nAnswer: ",
             ~~~~^^^^^^^^^^^^
KeyError: 'QUESTION'

```

### social_i_qa (`siqa`)

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
RuntimeError: Dataset scripts are no longer supported, but found social_i_qa.py

```

### hle (`hle`)

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
  File "/home/rayhownh/.cache/pypoetry/virtualenvs/evalhub-YMyCob0K-py3.12/lib/python3.12/site-packages/datasets/load.py", line 1030, in dataset_module_factory
    raise e1 from None
  File "/home/rayhownh/.cache/pypoetry/virtualenvs/evalhub-YMyCob0K-py3.12/lib/python3.12/site-packages/datasets/load.py", line 1016, in dataset_module_factory
    raise DatasetNotFoundError(message) from e
datasets.exceptions.DatasetNotFoundError: Dataset 'cais/hle' is a gated dataset on the Hub. Visit the dataset page at https://huggingface.co/datasets/cais/hle to ask for access.

```

### med_qa (`med_qa`)

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
RuntimeError: Dataset scripts are no longer supported, but found med_qa.py

```

### coqa (`coqa`)

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
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/lighteval_task.py", line 314, in _get_docs_from_split
    doc.id = str(ix)
    ^^^^^^
AttributeError: 'list' object has no attribute 'id'

```

### mgsm (`mgsm:bn`)

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
RuntimeError: Dataset scripts are no longer supported, but found mgsm.py

```

### real-toxicity-prompts (`real_toxicity_prompts`)

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
TypeError: 'NoneType' object is not subscriptable

```

### bigbench (`bigbench:mult_data_wrangling`)

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
KeyError: 'default'

```

### tinyGSM8k (`tiny:gsm8k`)

```python
Traceback (most recent call last):
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 176, in _run_task_evaluation_background
    pipeline_output = service._run_lighteval_task_pipeline(request)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 409, in _run_lighteval_task_pipeline
    pipeline.evaluate()
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 294, in evaluate
    self.evaluation_tracker.metrics_logger.aggregate(
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/logging/info_loggers.py", line 349, in aggregate
    metric_result = aggregation(metric_values)
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/tasks/tasks/tiny_benchmarks.py", line 119, in compute_corpus
    with open("extended_tasks/tiny_benchmarks/tinyBenchmarks.pkl", "rb") as handle:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
FileNotFoundError: [Errno 2] No such file or directory: 'extended_tasks/tiny_benchmarks/tinyBenchmarks.pkl'

```

### IFBench_test (`ifbench_test`)

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

### OlympiadBench (`olympiad_bench:OE_TO_maths_en_COMP`)

```python
Traceback (most recent call last):
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 176, in _run_task_evaluation_background
    pipeline_output = service._run_lighteval_task_pipeline(request)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/c/Projects/Evalhub/backend/api/evaluations/service.py", line 410, in _run_lighteval_task_pipeline
    pipeline.save_and_push_results()
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/pipeline.py", line 429, in save_and_push_results
    self.evaluation_tracker.save()
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/logging/evaluation_tracker.py", line 273, in save
    self.save_details(date_id, details_datasets)
  File "/mnt/c/Projects/Evalhub/backend/lighteval/src/lighteval/logging/evaluation_tracker.py", line 361, in save_details
    dataset.to_parquet(f)
  File "/home/rayhownh/.cache/pypoetry/virtualenvs/evalhub-YMyCob0K-py3.12/lib/python3.12/site-packages/datasets/arrow_dataset.py", line 5295, in to_parquet
    ).write()
      ^^^^^^^
  File "/home/rayhownh/.cache/pypoetry/virtualenvs/evalhub-YMyCob0K-py3.12/lib/python3.12/site-packages/datasets/io/parquet.py", line 108, in write
    written = self._write(
              ^^^^^^^^^^^^
  File "/home/rayhownh/.cache/pypoetry/virtualenvs/evalhub-YMyCob0K-py3.12/lib/python3.12/site-packages/datasets/io/parquet.py", line 124, in _write
    writer = pq.ParquetWriter(
             ^^^^^^^^^^^^^^^^^
  File "/home/rayhownh/.cache/pypoetry/virtualenvs/evalhub-YMyCob0K-py3.12/lib/python3.12/site-packages/pyarrow/parquet/core.py", line 1070, in __init__
    self.writer = _parquet.ParquetWriter(
                  ^^^^^^^^^^^^^^^^^^^^^^^
  File "pyarrow/_parquet.pyx", line 2363, in pyarrow._parquet.ParquetWriter.__cinit__
  File "pyarrow/error.pxi", line 155, in pyarrow.lib.pyarrow_internal_check_status
  File "pyarrow/error.pxi", line 92, in pyarrow.lib.check_status
pyarrow.lib.ArrowNotImplementedError: Cannot write struct type 'specific' with no child field to Parquet. Consider adding a dummy child field.

```

### qasper (`qasper`)

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
RuntimeError: Dataset scripts are no longer supported, but found qasper.py

```

### raft (`raft:ade_corpus_v2`)

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
RuntimeError: Dataset scripts are no longer supported, but found raft.py

```
