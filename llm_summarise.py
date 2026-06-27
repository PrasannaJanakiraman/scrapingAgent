"""LLM summarisation module using Azure OpenAI."""

import os

from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

_client = AzureOpenAI(
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2025-01-01-preview"),
)


def summarise(text: str) -> str:
    """Summarise the given text into 1-5 lines using Azure OpenAI."""
    response = _client.chat.completions.create(
        model=os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-5"),
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant. Summarize the provided data in 1 to 5 lines.",
            },
            {
                "role": "user",
                "content": text,
            },
        ],
    )
    return response.choices[0].message.content
