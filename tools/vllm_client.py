import base64
import logging
from typing import Optional

from openai import OpenAI

logger = logging.getLogger(__name__)


class VLLMClient:
    """
    OpenAI-compatible client for vLLM local server.
    Supports text-only and vision (multimodal) requests.

    Start vLLM server:
        vllm serve Qwen/Qwen2.5-VL-7B-Instruct --host 0.0.0.0 --port 8000
        # or with tensor parallelism:
        vllm serve mistralai/Mistral-7B-Instruct-v0.3 --tensor-parallel-size 2
    """

    def __init__(self, base_url: str, api_key: str, model: str):
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.model = model

    def chat(
        self,
        prompt: str,
        system_prompt: str = "You are a helpful document analysis assistant.",
        max_tokens: int = 2048,
        temperature: float = 0.1,
    ) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content or ""

    def chat_with_image(
        self,
        prompt: str,
        image_b64: str,
        system_prompt: str = "You are a document analysis assistant with vision capabilities.",
        max_tokens: int = 2048,
        temperature: float = 0.1,
    ) -> str:
        """Send a prompt with a base64 image for vision models (e.g., Qwen2.5-VL)."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_b64}"
                            },
                        },
                        {"type": "text", "text": prompt},
                    ],
                },
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content or ""
