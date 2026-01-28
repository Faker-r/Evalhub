import asyncio
from api.core.database import async_session

from api.models_and_providers.schemas import ModelCreate, ProviderCreate
from api.models_and_providers.service import ModelsAndProvidersService


PROVIDER_NAME = "openrouter"
PROVIDER_BASE_URL = "https://openrouter.ai/api/v1"

MODEL_DISPLAY_NAME = "GPT-4.1"
MODEL_DEVELOPER = "OpenAI"
MODEL_API_NAME = "openai/gpt-4.1"


async def main() -> None:
    async with async_session() as session:
        service = ModelsAndProvidersService(session)

        provider = await service.create_provider(
            ProviderCreate(name=PROVIDER_NAME, base_url=PROVIDER_BASE_URL)
        )
        model = await service.create_model(
            ModelCreate(
                display_name=MODEL_DISPLAY_NAME,
                developer=MODEL_DEVELOPER,
                api_name=MODEL_API_NAME,
                provider_ids=[provider.id],
            )
        )

        print(provider.model_dump())
        print(model.model_dump())

"""
"openai": "https://api.openai.com/v1",
    "baseten": "https://inference.baseten.co/v1",
"""

async def backfill_providers():
    async with async_session() as session:
        service = ModelsAndProvidersService(session)
        _ = await service.create_provider(
            ProviderCreate(name="baseten", base_url="https://inference.baseten.co/v1")
        )
        _ = await service.create_provider(
            ProviderCreate(name="openai", base_url="https://api.openai.com/v1")
        )
        


if __name__ == "__main__":
    asyncio.run(backfill_providers())
