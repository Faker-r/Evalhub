"""Module for generating response classes for guideline scoring."""

from collections import Counter
from typing import Callable, Type, Literal, Dict, Any
import json
from pydantic import BaseModel, Field
from lighteval.models.model_output import ModelResponse
from lighteval.tasks.requests import Doc, SamplingMethod
from lighteval.metrics.utils.llm_as_judge import JudgeLM
from lighteval.metrics import Metric
from api.guidelines.schemas import GuidelineScoringScale


class BooleanScoreResponse(BaseModel):
    """Response class for boolean guideline scoring."""

    score: Literal["true", "false"]


class PercentageScoreResponse(BaseModel):
    """Response class for percentage guideline scoring."""

    score: int = Field(ge=0, le=100)


class GuidelineScoringScaleAbstract:
    """Abstract class for guideline scoring scales."""

    def generate_response_class(self, guideline: dict[str, Any]) -> Type[BaseModel]:
        """Generate a response class for the guideline scoring scale."""
        raise NotImplementedError

    def generate_score_prompt(self, guideline: dict[str, Any]) -> str:
        """Generate a score prompt for the guideline scoring scale."""
        raise NotImplementedError


class BooleanGuidelineScoringScale(GuidelineScoringScaleAbstract):
    """Class for boolean guideline scoring scale."""

    def generate_response_class(self, guideline: dict[str, Any]) -> Type[BaseModel]:
        """Generate a response class for the boolean guideline scoring scale."""
        return BooleanScoreResponse

    def generate_score_prompt(self, guideline: dict[str, Any]) -> str:
        """Generate a score prompt for the boolean guideline scoring scale."""
        return "Please choose one of the following options as your score: true, false."


class PercentageGuidelineScoringScale(GuidelineScoringScaleAbstract):
    """Class for percentage guideline scoring scale."""

    def generate_response_class(self, guideline: dict[str, Any]) -> Type[BaseModel]:
        """Generate a response class for the percentage guideline scoring scale."""
        return PercentageScoreResponse

    def generate_score_prompt(self, guideline: dict[str, Any]) -> str:
        """Generate a score prompt for the percentage guideline scoring scale."""
        return "Please score the response on a scale of 0 to 100."


class NumericGuidelineScoringScale(GuidelineScoringScaleAbstract):
    """Class for numeric guideline scoring scale."""

    def generate_response_class(self, guideline: dict[str, Any]) -> Type[BaseModel]:
        """Generate a response class for the numeric guideline scoring scale."""

        class NumericScoreResponse(BaseModel):
            """Response class for numeric guideline scoring."""

            score: int = Field(
                ge=guideline["scoring_scale_config"]["min_value"],
                le=guideline["scoring_scale_config"]["max_value"],
            )

        return NumericScoreResponse

    def generate_score_prompt(self, guideline: dict[str, Any]) -> str:
        """Generate a score prompt for the numeric guideline scoring scale."""
        return f"Please score the response on a scale of {guideline['scoring_scale_config']['min_value']} to {guideline['scoring_scale_config']['max_value']}."


class CustomCategoryGuidelineScoringScale(GuidelineScoringScaleAbstract):
    """Class for custom category guideline scoring scale."""

    def generate_response_class(self, guideline: dict[str, Any]) -> Type[BaseModel]:
        """Generate a response class for the custom category guideline scoring scale."""

        class CustomCategoryScoreResponse(BaseModel):
            """Response class for custom category guideline scoring."""

            score: Literal[*guideline["scoring_scale_config"]["categories"]]

        return CustomCategoryScoreResponse

    def generate_score_prompt(self, guideline: dict[str, Any]) -> str:
        """Generate a score prompt for the custom category guideline scoring scale."""
        return f"Please choose one of the following options as your score: {', '.join(guideline['scoring_scale_config']['categories'])}."


def generate_get_judge_prompt_function(
    guideline: dict[str, Any], guideline_scoring_scale: GuidelineScoringScaleAbstract
) -> Callable:
    """Generate a function that returns the judge prompt for the given guideline and guideline scoring scale."""

    def fn(question: str, answer: str, gold: str = None, **_kwargs):
        """Generate the judge prompt for the given guideline and guideline scoring scale."""
        score_prompt = guideline_scoring_scale.generate_score_prompt(guideline)

        TEMPLATE = """
        You are an expert judge evaluating the response to the provided question. Your evaluation should be based on the following guideline:
        {guideline_description}

        The request is: {question}

        The response is: {answer}

        {gold_answer}

        {score_prompt}
        """.strip()

        content = TEMPLATE.format(
            guideline_description=guideline["prompt"],
            score_prompt=score_prompt,
            question=question,
            answer=answer,
            gold_answer=f"The gold answer is: {gold}" if gold else "",
        )

        return [{"role": "user", "content": content}]

    return fn


def process_judge_response(response: str) -> float | int | str:
    """Process the judge response to extract the score."""
    return json.loads(response)["score"]


class GuidelineJudgeMetric(Metric):
    """Metric for guideline scoring."""

    def __init__(
        self,
        guideline: Dict[str, Any],
        model: str,
        url: str,
        api_key: str,
    ):
        self.guideline = guideline
        self.guideline_scoring_scale = self._init_guideline_scoring_scale()
        self.metric_name = guideline.get("name", "guideline_score")
        self.short_judge_name = "judge_" + guideline.get("name", "guideline")
        self.category = SamplingMethod.GENERATIVE
        self.corpus_level_fn = self.aggregate_scores
        self.sample_level_fn = self.compute
        self.higher_is_better = (
            True
            if guideline["scoring_scale"]
            in (GuidelineScoringScale.NUMERIC, GuidelineScoringScale.PERCENTAGE)
            else False
        )
        self.judge = JudgeLM(
            model=model,
            templates=generate_get_judge_prompt_function(
                guideline, self.guideline_scoring_scale
            ),
            api_key=api_key,
            url=url,
            process_judge_response=process_judge_response,
            response_format=self.guideline_scoring_scale.generate_response_class(
                guideline
            ),
            judge_backend="litellm",
        )

    def _init_guideline_scoring_scale(self) -> GuidelineScoringScaleAbstract:
        if self.guideline["scoring_scale"] == GuidelineScoringScale.BOOLEAN:
            return BooleanGuidelineScoringScale()
        elif self.guideline["scoring_scale"] == GuidelineScoringScale.PERCENTAGE:
            return PercentageGuidelineScoringScale()
        elif self.guideline["scoring_scale"] == GuidelineScoringScale.NUMERIC:
            return NumericGuidelineScoringScale()
        elif self.guideline["scoring_scale"] == GuidelineScoringScale.CUSTOM_CATEGORY:
            return CustomCategoryGuidelineScoringScale()
        else:
            raise ValueError(f"Invalid guideline: {self.guideline}")

    def compute(
        self, responses: list[ModelResponse], docs: list[Doc], **_kwargs
    ) -> list:
        """Compute the guideline score for responses generated by the model."""
        questions = [doc.query for doc in docs]
        predictions = [response.final_text[0] for response in responses]

        scores, messages, judgements = self.judge.evaluate_answer_batch(
            questions,
            predictions,
            options=[None] * len(questions),
            golds=[None] * len(questions),
        )

        metrics = []
        for i in range(len(docs)):
            metric_dict = {
                self.metric_name: scores[i],
                f"user_prompt_{self.short_judge_name}": messages[i],
            }

            judgement = judgements[i]
            if isinstance(judgement, BaseModel):
                metric_dict[f"judgement_{self.short_judge_name}"] = {
                    "score": judgement.score,
                }
            else:
                metric_dict[f"judgement_{self.short_judge_name}"] = judgement

            metrics.append(metric_dict)

        return metrics

    def aggregate_scores(self, scores: list) -> float | dict[str, int]:
        scale_type = self.guideline["scoring_scale"]

        if scale_type in (
            GuidelineScoringScale.CUSTOM_CATEGORY,
            GuidelineScoringScale.BOOLEAN,
        ):
            return dict(Counter(scores))
        else:
            return sum(scores) / len(scores) if scores else 0.0
