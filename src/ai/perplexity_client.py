"""
Perplexity API client wrapper.
Reads PERPLEXITY_API_KEY from env. Provides ask() and batch() convenience methods.
"""
from __future__ import annotations

import os
import time
import json
from typing import List, Dict, Any, Optional

import httpx


class PerplexityClient:
    def __init__(self, api_key: Optional[str] = None, model: str = "pplx-70b-online", timeout: int = 60, max_retries: int = 2):
        self.api_key = api_key or os.getenv("PERPLEXITY_API_KEY")
        if not self.api_key:
            raise ValueError("PERPLEXITY_API_KEY not set")
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
        self.base_url = os.getenv("PERPLEXITY_BASE_URL", "https://api.perplexity.ai")

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def ask(self, query: str, system: str | None = None, max_tokens: int = 1200, temperature: float = 0.2) -> Dict[str, Any]:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": query})
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        return self._post_json("/chat/completions", payload)

    def batch(self, queries: List[str], system: str | None = None) -> List[Dict[str, Any]]:
        out = []
        for q in queries:
            out.append(self.ask(q, system=system))
        return out

    def _post_json(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url.rstrip('/')}{path}"
        last_error: Optional[Exception] = None
        for attempt in range(self.max_retries + 1):
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    resp = client.post(url, headers=self._headers(), json=payload)
                if resp.status_code >= 200 and resp.status_code < 300:
                    data = resp.json()
                    # Normalize a minimal structure with answer and citations if present
                    content = ""
                    citations: List[Dict[str, Any]] = []
                    try:
                        content = data["choices"][0]["message"]["content"].strip()
                    except Exception:
                        pass
                    # Some Perplexity responses include a "citations" or "sources" field
                    citations = data.get("citations") or data.get("sources") or []
                    return {"success": True, "raw": data, "answer": content, "citations": citations}
                else:
                    last_error = RuntimeError(f"HTTP {resp.status_code}: {resp.text[:200]}")
            except Exception as e:
                last_error = e
            time.sleep(min(2 ** attempt, 5))
        return {"success": False, "error": str(last_error) if last_error else "Unknown error"}
