"""
gpt package public API.

- `ChatGPT`  : high-level Safari automation wrapper
- `api_app`  : FastAPI adapter that turns the local Safari driver into an
               OpenAI-compatible `/v1/chat/completions` endpoint
"""

from .init import ChatGPT                # existing export
from .openai_compat import app as api_app  # NEW export

__all__: list[str] = ["ChatGPT", "api_app"]
