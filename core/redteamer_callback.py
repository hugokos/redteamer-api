# core/redteamer_callback.py

import os
import openai

try:
    # 1) If you set OPENAI_API_KEY directly in Cloud Run → env-vars, we pick it up here.
    openai.api_key = os.environ["OPENAI_API_KEY"]
except KeyError:
    # 2) Otherwise, fall back to Secret Manager
    from google.cloud import secretmanager

    # Name of your secret version in Secret Manager:
    # e.g. "projects/1234567890/secrets/openai-api-key/versions/latest"
    secret_name = os.environ.get(
        "OPENAI_SECRET_NAME",
        ""
    )
    if not secret_name:
        raise RuntimeError(
            "Neither OPENAI_API_KEY nor OPENAI_SECRET_NAME is set in env-vars"
        )

    client = secretmanager.SecretManagerServiceClient()
    response = client.access_secret_version(name=secret_name)
    openai.api_key = response.payload.data.decode("utf-8")


async def wrapped_model_callback(prompt: str) -> str:
    """
    Enrich prompt however you like, then call OpenAI.
    """
    resp = await openai.ChatCompletion.acreate(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return resp.choices[0].message.content
