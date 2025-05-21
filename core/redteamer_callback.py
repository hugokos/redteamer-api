# core/redteamer_callback.py

import os
from openai import OpenAI
from google.cloud import secretmanager

def _get_openai_key() -> str:
    """
    First check for the OPENAI_API_KEY env-var (mounted via --set-secrets).
    If not present, fall back to Secret Manager.
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
    Enriches your prompt as before, then calls the new chat.completions endpoint.
    """
    api_key = _get_openai_key()
    client = OpenAI(api_key=api_key)

    # New v1.x syntax: client.chat.completions.create(...) instead of ChatCompletion
    resp = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    # Extract the assistant’s reply
    return resp.choices[0].message.content
