import json
import tempfile
from pathlib import Path

import numpy as np

from api.evaluations.schemas import (
    JudgeType,
    MultipleChoiceConfig,
    OutputType,
    TextOutputConfig,
)
from lighteval.metrics import Metric
from lighteval.metrics.metrics import Metrics
from lighteval.metrics.metrics_sample import ExactMatches
from lighteval.metrics.utils.metric_utils import SampleLevelMetric
from lighteval.tasks.lighteval_task import (
    LightevalTask,
    LightevalTaskConfig,
    TextGenerationInputGrammarType,
)
from lighteval.tasks.requests import Doc, SamplingMethod


class FlexibleDatasetTask:
    MULTIPLE_CHOICE_PROMPT = """
    Answer the following multiple choice question:
    Question: {query}
    Choices (index: text):
    {choices}
    Answer:
    """

    def __init__(
        self,
        dataset_name: str,
        dataset_content: str,
        input_field: str,
        output_type: OutputType,
        judge_type: JudgeType,
        text_config: TextOutputConfig | None = None,
        mc_config: MultipleChoiceConfig | None = None,
        guideline_metrics: list[Metric] | None = None,
    ):
        self.dataset_name = dataset_name
        self.dataset_content = dataset_content
        self.input_field = input_field
        self.output_type = output_type
        self.judge_type = judge_type
        self.text_config = text_config
        self.mc_config = mc_config
        self.guideline_metrics = guideline_metrics or []
        self.temp_file = None

    def _get_metrics(self) -> list[Metric]:
        if self.judge_type == JudgeType.LLM_AS_JUDGE:
            return self.guideline_metrics
        elif self.judge_type == JudgeType.F1_SCORE:
            return [Metrics.f1_score]
        elif (
            self.judge_type == JudgeType.EXACT_MATCH
            and self.output_type == OutputType.MULTIPLE_CHOICE
        ):
            return [
                SampleLevelMetric(
                    metric_name="mcq",
                    sample_level_fn=ExactMatches(
                        strip_strings=True,
                        normalize_pred=lambda pred_str: str(
                            json.loads(pred_str)["choice_index"]
                        ),
                    ),
                    category=SamplingMethod.GENERATIVE,
                    corpus_level_fn=np.mean,
                    higher_is_better=True,
                )
            ]
        elif self.judge_type == JudgeType.EXACT_MATCH:
            return [Metrics.exact_match]
        return []

    def _create_prompt_function(self):
        input_field = self.input_field
        output_type = self.output_type
        text_config = self.text_config
        mc_config = self.mc_config
        dataset_name = self.dataset_name

        def line_to_prompt(line, _doc):
            query = line[input_field]

            if output_type == OutputType.MULTIPLE_CHOICE:
                choices = line[mc_config.choices_field]

                query_with_choices = self.MULTIPLE_CHOICE_PROMPT.format(
                    query=query,
                    choices="\n".join(
                        [f"{i}: {choice}" for i, choice in enumerate(choices)]
                    ),
                )

                gold_index = line[mc_config.gold_answer_field]
                if isinstance(gold_index, str):
                    gold_index = choices.index(gold_index)
                return Doc(
                    task_name=dataset_name,
                    query=query_with_choices,
                    choices=[str(i) for i in range(len(choices))],
                    gold_index=gold_index,
                )
            else:
                choices = []
                gold_index = 0
                if text_config and text_config.gold_answer_field:
                    gold_answer = line.get(text_config.gold_answer_field)
                    if gold_answer:
                        # Convert gold answer to list of strings
                        choices = (
                            [str(answer) for answer in gold_answer]
                            if isinstance(gold_answer, list)
                            else [str(gold_answer)]
                        )
                return Doc(
                    task_name=dataset_name,
                    query=query,
                    choices=choices,
                    gold_index=gold_index,
                )

        return line_to_prompt

    def _create_generation_grammar(self) -> TextGenerationInputGrammarType:
        return TextGenerationInputGrammarType(
            type="json",
            value={
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "choice_index": {"type": "integer", "minimum": 0, "maximum": 9},
                },
                "required": ["choice_index"],
            },
        )

    def build_lighteval_task(self) -> LightevalTask:
        self.temp_file = tempfile.NamedTemporaryFile(
            mode="w", suffix=".jsonl", delete=False
        )
        self.temp_file.write(self.dataset_content)
        self.temp_file.close()

        generation_grammar = None
        if self.output_type == OutputType.MULTIPLE_CHOICE:
            generation_grammar = self._create_generation_grammar()

        task_config = LightevalTaskConfig(
            name=self.dataset_name,
            prompt_function=self._create_prompt_function(),
            hf_repo="json",
            hf_subset=None,
            hf_avail_splits=["test"],
            evaluation_splits=["test"],
            hf_data_files={"test": self.temp_file.name},
            metrics=self._get_metrics(),
            stop_sequence=["\n\n\n"],
            generation_grammar=generation_grammar,
        )

        return LightevalTask(task_config)

    def cleanup(self):
        if self.temp_file:
            Path(self.temp_file.name).unlink(missing_ok=True)
