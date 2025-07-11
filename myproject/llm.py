from ollama import chat
import os
import requests
from typing import Optional
import os
import httpx
from ollama import Client

from django.http import StreamingHttpResponse
from ollama import Client

def lookup_with_llama(prompt: str):
    client = Client()
    response = client.chat(
        model="llama3",
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )
    for chunk in response:
        # chunk is a dict, get the content text
        content = chunk.get("message", {}).get("content")
        if content:
            yield content


# Environment variable name where the Claude API key is stored
api_key = open("claude_key.txt", "r").readlines()[0].strip()

# Claude API endpoint (replace with actual endpoint if different)
CLAUDE_API_URL = "https://api.anthropic.com/v1/complete"


def lookup_with_claude(prompt: str) -> str:
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,  # NOTE: Claude uses x-api-key, not Authorization header
        "Content-Type": "application/json",
        "anthropic-version": "2023-06-01",
    }
    data = {
        "model": "claude-3-5-sonnet-20241022",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1024
    }

    Client = httpx.Client(timeout=60) 
    response = Client.post(url, headers=headers, json=data)

    if response.status_code != 200:
        raise RuntimeError(f"Claude API request failed: {response.status_code} {response.text}")

    content_blocks = response.json()["content"]
    return "".join(block["text"] for block in content_blocks if block["type"] == "text")










