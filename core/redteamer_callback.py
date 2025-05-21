# core/redteamer_callback.py

import os
import openai
from google.cloud import secretmanager

def _get_openai_key():
    # direct env-var first
    key = os.getenv("OPENAI_API_KEY")
    if key:
        return key
    # fallback to Secret Manager
    secret_name = os.getenv("OPENAI_SECRET_NAME", "")
    if not secret_name:
        raise RuntimeError(
            "Neither OPENAI_API_KEY nor OPENAI_SECRET_NAME is set"
        )
    client = secretmanager.SecretManagerServiceClient()
    response = client.access_secret_version(name=secret_name)
    return response.payload.data.decode("utf-8")

async def wrapped_model_callback(prompt: str) -> str:
    # set key at call time (no loop patching)
    openai.api_key = _get_openai_key()

    resp = await openai.ChatCompletion.acreate(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return resp.choices[0].message.content
