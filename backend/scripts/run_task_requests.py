"""
Send POST /api/evaluations/tasks for the configured tasks × models × providers (all via OpenRouter).

Auth: set AUTH_EMAIL + AUTH_PASSWORD, or the script uses default admin login.
"""

import os
import sys
import time
import httpx

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")

TASKS = [
    # {"task_name": "gsm8k", "dataset_name": "gsm8k"},
    # {"task_name": "math_500", "dataset_name": "math_500"},
    {"task_name": "mmlu_pro", "dataset_name": "mmlu_pro"},
    # {"task_name": "gpqa", "dataset_name": "gpqa:main"},
]

# (api_name, display_name from log, providers from fetch_openrouter_models_and_providers.log)
MODELS_AND_PROVIDERS = [
    ("qwen/qwen3-coder-next", "Qwen: Qwen3 Coder Next", ["Together"]),
    ("openai/gpt-oss-120b", "OpenAI: gpt-oss-120b", ["Cerebras", "BaseTen"]),
    ("z-ai/glm-4.7-flash", "Z.AI: GLM 4.7 Flash", ["DeepInfra", "Novita"]),
    ("mistralai/ministral-14b-2512", "Mistral: Ministral 3 14B 2512", ["Mistral", "Together"]),
    ("deepseek/deepseek-v3.2", "DeepSeek: DeepSeek V3.2", ["Google", "DeepInfra"]),
    ("moonshotai/kimi-k2.5", "MoonshotAI: Kimi K2.5", ["BaseTen", "Together"]),
]

# Provider names and slugs from OpenRouter log (provider_name as key, slug for API)
PROVIDER_SLUG = {
    "Together": "together",
    "BaseTen": "baseten",
    "Mistral": "mistral",
    "DeepInfra": "deepinfra",
    "Cerebras": "cerebras",
    "Google": "google-vertex",
    "Novita": "novita",
}


def get_token() -> str:
    email = os.environ.get("AUTH_EMAIL", "admin@evalhub.com")
    password = os.environ.get("AUTH_PASSWORD", "12345678")
    r = httpx.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": email, "password": password},
        timeout=30.0,
    )
    r.raise_for_status()
    return r.json()["access_token"]


def model_config_openrouter(api_name: str, model_name: str, provider: str) -> dict:
    slug = PROVIDER_SLUG[provider]
    return {
        "api_source": "openrouter",
        "model_name": model_name,
        "model_id": -1,
        "api_name": api_name,
        "model_provider": provider,
        "model_provider_slug": slug,
        "model_provider_id": 0,
    }


def main() -> None:
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}

    requests_to_send = []
    for task in TASKS:
        for api_name, model_name, providers in MODELS_AND_PROVIDERS:
            for provider in providers:
                requests_to_send.append(
                    {
                        "task_name": task["task_name"],
                        "dataset_config": {
                            "dataset_name": task["dataset_name"],
                            "n_fewshots": 5,
                            "n_samples": 50,
                        },
                        "model_completion_config": model_config_openrouter(
                            api_name, model_name, provider
                        ),
                    }
                )

    
    for i, payload in enumerate(requests_to_send):
        with httpx.Client(timeout=120.0) as client:
            task_name = payload["task_name"]
            model = payload["model_completion_config"]["api_name"]
            provider_slug = payload["model_completion_config"]["model_provider_slug"]
            print(f"[{i + 1}/{len(requests_to_send)}] {task_name} | {model} | {provider_slug}")
            r = client.post(
                f"{BASE_URL}/api/evaluations/tasks",
                json=payload,
                headers=headers,
            )
            print(r.status_code, r.text[:200] if r.text else "")
            r.raise_for_status()

        time.sleep(20)

if __name__ == "__main__":
    main()
