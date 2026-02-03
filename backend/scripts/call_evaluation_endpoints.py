"""
Call evaluation endpoints /api/evaluations/tasks and /api/evaluations/flexible.

Session: set one of:
  - ACCESS_TOKEN: Bearer token (e.g. from Supabase or POST /api/auth/login).
  - AUTH_EMAIL + AUTH_PASSWORD: script will POST /api/auth/login to get a token.
  - USER_ID: create session via Supabase admin (run from backend with .env;
    requires SUPABASE_URL and SUPABASE_SECRET_KEY).
"""

import os
import sys

import httpx

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE_URL = "http://localhost:8000"


def get_token() -> str:
    email = "admin@evalhub.com"
    password = "12345678"
    if email and password:
        r = httpx.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": email, "password": password},
            timeout=30.0,
        )
        r.raise_for_status()
        return r.json()["access_token"]

def main() -> None:
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}

    baseten_deepseek_config = {
        "api_source": "standard",
        "model_name": "deepseek-ai/DeepSeek-V3.2",
        "model_id": "2",
        "api_name": "deepseek-ai/DeepSeek-V3.2",
        "model_provider": "Baseten",
        "model_provider_slug": "baseten",
        "model_provider_id": 2
    }

    openai_gpt_4_1_config = {
        "api_source": "standard",
        "model_name": "gpt-4.1",
        "model_id": "7",
        "api_name": "gpt-4.1",
        "model_provider": "OpenAI",
        "model_provider_slug": "openai",
        "model_provider_id": 3
    }

    openrouter_together_openai_oss_20b_config = {
        "api_source": "openrouter",
        "model_name": "openai/gpt-oss-20b",
        "model_id": "1",
        "api_name": "openai/gpt-oss-20b",
        "model_provider": "together",
        "model_provider_slug": "together",
        "model_provider_id": 0
    }



    tasks_payload = {
        "task_name": "gsm8k",
        "dataset_config": {
            "dataset_name": "gsm8k",
            "n_samples": 50,
            "n_fewshots": 0,
        },
        "model_completion_config": openrouter_together_openai_oss_20b_config # baseten_deepseek_config
    }

    flexible_payload = {
        "dataset_name": "mmlu_college_chem_test_sample",
        "input_field": "question",
        "output_type": "multiple_choice",
        "mc_config": {"choices_field": "choices", "gold_answer_field": "answer"},
        "judge_type": "exact_match",
        "model_completion_config": tasks_payload["model_completion_config"],
        "judge_config": None,
    }
    flexible_payload_2 = {
        "dataset_name": "jokes2",
        "input_field": "input",
        "output_type": "text",
        "text_config": {},
        "judge_type": "llm_as_judge",
        "guideline_names": [
            "simplicity",
            "writing_professionalism_1to10"
        ],
        "model_completion_config": openai_gpt_4_1_config,
        "judge_config": baseten_deepseek_config
    }


    task_list = [
        {
            "task_name": "openbookqa",
            "dataset_config": {
                "dataset_name": "openbookqa",
                "n_samples": 50,
                "n_fewshots": 0,
            },
            "model_completion_config": openai_gpt_4_1_config
        },
        {
            "task_name": "openbookqa",
            "dataset_config": {
                "dataset_name": "openbookqa",
                "n_samples": 50,
                "n_fewshots": 0,
            },
            "model_completion_config": baseten_deepseek_config
        },
        {
            "task_name": "openbookqa",
            "dataset_config": {
                "dataset_name": "openbookqa",
                "n_samples": 50,
                "n_fewshots": 0,
            },
            "model_completion_config": baseten_deepseek_config
        }
    ]

    with httpx.Client(timeout=60.0) as client:
        which = "tasks"

        if which == "tasks":
            r = client.post(
                f"{BASE_URL}/api/evaluations/tasks",
                json=tasks_payload,
                headers=headers,
            )
        elif which == "flexible":
            r = client.post(
                f"{BASE_URL}/api/evaluations/flexible",
                json=flexible_payload,
                headers=headers,
            )
        else:
            raise SystemExit("Set CALL=tasks or CALL=flexible")

    print(r.status_code, r.text)
    r.raise_for_status()


if __name__ == "__main__":
    main()
