#!/usr/bin/env python3
"""
OpenAI-compatible REST façade for proxy_chatgpt.

Run with:
    uvicorn openai_compat:app --host 0.0.0.0 --port 8000
Then point the official openai-python client at:
    openai.api_key = "any-string"
    openai.base_url = "http://localhost:8000/v1/"
"""
import uuid, time
from typing import List, Optional, Literal

from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, Field

# 👇 our existing desktop-automation wrapper
from gpt.init import ChatGPT        # noqa: E402  (import after FastAPI)

# ------------ OpenAI-style request / response models ------------ #
class Message(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: str

class Choice(BaseModel):
    index: int
    message: Message
    finish_reason: Literal["stop"] = "stop"

class Usage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

class ChatCompletionResponse(BaseModel):
    id: str = Field(default_factory=lambda: f"chatcmpl-{uuid.uuid4().hex[:24]}")
    object: Literal["chat.completion"] = "chat.completion"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str
    choices: List[Choice]
    usage: Usage = Usage()

class ChatCompletionRequest(BaseModel):
    model: str = "gpt-4o"
    messages: List[Message]
    stream: Optional[bool] = False
    temperature: Optional[float] = 1.0
    # …you can add the rest of the OpenAI parameters here; they’ll be ignored.

# --------------------------- FastAPI ---------------------------- #
app = FastAPI(
    title="proxy_chatgpt OpenAI façade",
    version="1.0.0",
    openapi_url=None,      # keep the surface identical to OpenAI
    docs_url=None,
    redoc_url=None,
)

# Single global ChatGPT driver (Safari tab) – thread-safety isn’t a concern
# because FastAPI default workers are single-threaded per request.
_driver = ChatGPT(window_geometry=(0, 0, 700, 900))

@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
def chat_completions(
    body: ChatCompletionRequest,
    authorization: Optional[str] = Header(default=None),
):
    """
    Emulates POST /v1/chat/completions from the OpenAI Chat Completions API :contentReference[oaicite:1]{index=1}
    * Only the last **user** message is forwarded to ChatGPT.
    * `chat_id` can be supplied via `body.messages[0].content` meta tag or omitted for new chats.
    """
    if body.stream:
        raise HTTPException(400, "Streaming not supported")

    # --- extract the last user prompt & an optional chat-id marker --- #
    last_user_msg = next((m for m in reversed(body.messages) if m.role == "user"), None)
    if not last_user_msg:
        raise HTTPException(400, "No user message supplied")

    chat_id = None
    if body.messages and body.messages[0].role == "system":
        # Convention: system message may contain `CHAT_ID:<uuid>` to resume a thread
        if body.messages[0].content.startswith("CHAT_ID:"):
            chat_id = body.messages[0].content.split(":", 1)[1].strip()

    # --- call the existing macOS automation driver --- #
    answer = _driver.chat(
        prompt=last_user_msg.content,
        chat_id=chat_id or "new",
        model_name=body.model,
        search=False,
        deep_research=False,
    )

    # --- shape the OpenAI-style response --- #
    return ChatCompletionResponse(
        model=body.model,
        choices=[Choice(index=0, message=Message(role="assistant", content=answer))],
    )
