"""Side-by-side evaluation comparison across model-provider pairs."""

import asyncio

from api.core.database import async_session
from api.evaluation_comparison.schemas import ModelProviderPair
from api.evaluation_comparison.service import EvaluationComparisonService


async def main() -> None:
    pairs = [
        ModelProviderPair(model="Qwen: Qwen3 235B A22B Thinking 2507", provider="openrouter"),
        ModelProviderPair(model="OpenAI: GPT-5.1", provider="openrouter"),
    ]
    async with async_session() as session:
        service = EvaluationComparisonService(session)
        overlap = await service.get_overlapping_datasets(pairs)
        print(f"Overlapping datasets: {overlap.count} -> {overlap.dataset_names}")
        report = await service.generate_side_by_side_report(pairs)
        for e in sorted(report.entries, key=lambda x: (x.model, x.provider, x.dataset_name, x.metric_name)):
            print(f"{e.model} | {e.provider} | {e.dataset_name} | {e.metric_name} -> trace={e.trace_id} at {e.created_at} score={e.score}")


if __name__ == "__main__":
    asyncio.run(main())
