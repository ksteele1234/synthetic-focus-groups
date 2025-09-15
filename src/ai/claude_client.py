"""
Anthropic Claude API client wrapper with JSON-only completion helper.
Reads ANTHROPIC_API_KEY from env.
"""
from __future__ import annotations

import os
import json
from typing import List, Dict, Any, Optional

try:
    import anthropic
    _ANTHROPIC_AVAILABLE = True
except Exception:
    anthropic = None
    _ANTHROPIC_AVAILABLE = False


class ClaudeClient:
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-5-sonnet-latest", max_retries: int = 2):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")
        if not _ANTHROPIC_AVAILABLE:
            raise ImportError("anthropic package not installed. Add to requirements and pip install.")
        self.model = model
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.max_retries = max_retries

    def complete(self, messages: List[Dict[str, str]], temperature: float = 0.3, max_tokens: int = 2000) -> str:
        resp = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=messages,
        )
        # Anthropics returns a content array of blocks
        try:
            return "".join(block.text for block in resp.content)
        except Exception:
            return ""

    def json_only(self, system: str, user: str, temperature: float = 0.2, max_tokens: int = 4000) -> Any:
        """Request Claude to return JSON only. Raises if JSON cannot be parsed."""
        content = self.complete([
            {"role": "system", "content": system + "\nReturn strictly JSON. No commentary."},
            {"role": "user", "content": user}
        ], temperature=temperature, max_tokens=max_tokens)
        # Attempt to parse JSON; if there's extra text, try to extract JSON segment
        try:
            return json.loads(content)
        except Exception:
            # Try to find first and last curly braces
            try:
                start = content.index("{")
                end = content.rindex("}") + 1
                return json.loads(content[start:end])
            except Exception as e:
                raise ValueError(f"Claude did not return valid JSON: {e}\nRaw: {content[:400]}")
