# core/redteamer_callback.py

import os
from openai import AsyncOpenAI
from google.cloud import secretmanager

def _get_openai_key() -> str:
    """
    First try the env-var (mounted via --set-secrets).
    Fallback to Secret Manager if not set.
    """
    key = os.getenv("OPENAI_API_KEY")
    if key:
        return key

    secret_name = os.getenv("OPENAI_SECRET_NAME", "")
    if not secret_name:
        raise RuntimeError(
            "Neither OPENAI_API_KEY nor OPENAI_SECRET_NAME is set"
        )

    client = secretmanager.SecretManagerServiceClient()
    response = client.access_secret_version(name=secret_name)
    return response.payload.data.decode("utf-8")


async def wrapped_model_callback(prompt: str) -> str:
    """
    Use the AsyncOpenAI client so you can 'await' chat completions.
    """
    api_key = _get_openai_key()
    client  = AsyncOpenAI(api_key=api_key)

    resp = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )

    # return the assistant’s reply
    return resp.choices[0].message.content
