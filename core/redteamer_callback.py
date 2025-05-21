# core/redteamer_callback.py

import os
import openai
from google.cloud import secretmanager

def _get_openai_key():
    # first look for a direct env-var (Cloud Run)
    key = os.getenv("OPENAI_API_KEY")
    if key:
        return key

    # otherwise fallback to Secret Manager
    secret_name = os.getenv("OPENAI_SECRET_NAME", "")
    if not secret_name:
        raise RuntimeError(
            "Neither OPENAI_API_KEY nor OPENAI_SECRET_NAME is set in env-vars"
        )
    client = secretmanager.SecretManagerServiceClient()
    response = client.access_secret_version(name=secret_name)
    return response.payload.data.decode("utf-8")


async def wrapped_model_callback(prompt: str) -> str:
    # lazily fetch the key at call time
    openai.api_key = _get_openai_key()

    resp = await openai.ChatCompletion.acreate(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return resp.choices[0].message.content
