"""Claude Sonnet client wrapper with a deterministic offline fallback for demo mode."""
from __future__ import annotations

import textwrap

from backend.config import settings


class ClaudeClient:
    """Wraps Anthropic's Claude Sonnet; falls back to an extractive summarizer offline."""

    def __init__(self) -> None:
        self._client = None
        if settings.has_claude_credentials:
            try:
                import anthropic

                self._client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
            except Exception:
                self._client = None

    @property
    def is_live(self) -> bool:
        return self._client is not None

    def generate(self, prompt: str, system: str = "", max_tokens: int = 600) -> str:
        if self._client is not None:
            response = self._client.messages.create(
                model=settings.claude_model,
                max_tokens=max_tokens,
                system=system or "You are a helpful, precise enterprise assistant.",
                messages=[{"role": "user", "content": prompt}],
            )
            return "".join(block.text for block in response.content if block.type == "text")
        return self._offline_generate(prompt)

    def stream(self, prompt: str, system: str = ""):
        """Yields text chunks; real streaming via Anthropic, or word-by-word offline."""
        if self._client is not None:
            with self._client.messages.stream(
                model=settings.claude_model,
                max_tokens=600,
                system=system or "You are a helpful, precise enterprise assistant.",
                messages=[{"role": "user", "content": prompt}],
            ) as stream:
                for text in stream.text_stream:
                    yield text
            return
        for word in self._offline_generate(prompt).split():
            yield word + " "

    @staticmethod
    def _offline_generate(prompt: str) -> str:
        """Deterministic, explainable stand-in answer — no external calls required."""
        context_marker = "Context:"
        if context_marker in prompt:
            context = prompt.split(context_marker, 1)[1]
            summary = textwrap.shorten(context.strip(), width=350, placeholder=" ...")
            return (
                "[DEMO MODE — synthetic answer, no live LLM call]\n\n"
                f"Based on the retrieved context, here is a grounded answer:\n{summary}"
            )
        return "[DEMO MODE] " + textwrap.shorten(prompt, width=200, placeholder=" ...")


claude_client = ClaudeClient()
