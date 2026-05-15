"""AI 提示词管理专用路由。"""

from __future__ import annotations

import json
import time
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.schemas.settings import AiTestBody

router = APIRouter()

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
USER_PROMPT_FILE = PROJECT_ROOT / "user_ai_prompt.txt"


class PromptResponse(BaseModel):
    content: str
    source: str


def _load_prompt() -> PromptResponse:
    if USER_PROMPT_FILE.is_file():
        text = USER_PROMPT_FILE.read_text(encoding="utf-8").strip()
        if text:
            return PromptResponse(content=text, source="user_ai_prompt.txt")
    from data import AI_KEYWORD_PROMPT

    return PromptResponse(content=AI_KEYWORD_PROMPT, source="data.py (默认)")


@router.get("/prompt")
def get_prompt():
    return _load_prompt()


class PromptSave(BaseModel):
    content: str


@router.post("/prompt")
def save_prompt(body: PromptSave):
    text = body.content.strip()
    if not text:
        raise HTTPException(400, detail="内容不能为空")
    if "{seed}" not in text or "{num}" not in text:
        raise HTTPException(400, detail="模板必须包含 {seed} 和 {num} 占位符")
    USER_PROMPT_FILE.write_text(text, encoding="utf-8")
    return {"ok": True, "source": "user_ai_prompt.txt"}


@router.post("/test")
async def test_llm(body: AiTestBody):
    api_key = body.api_key.strip()
    if not api_key:
        raise HTTPException(400, detail="API Key 不能为空")

    base_url = body.base_url.strip() or "https://ark.cn-beijing.volces.com/api/v3"
    model = body.model_endpoint.strip()
    if not model:
        raise HTTPException(400, detail="模型端点不能为空")

    try:
        from openai import AsyncOpenAI
    except ImportError:
        raise HTTPException(500, detail="openai 库未安装")

    client = AsyncOpenAI(
        api_key=api_key,
        base_url=base_url,
        timeout=15.0,
        max_retries=1,
    )

    t0 = time.perf_counter()
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": "Hi, respond with just: OK"},
            ],
            temperature=0,
            max_tokens=10,
        )
        elapsed_ms = round((time.perf_counter() - t0) * 1000)
        reply = (response.choices[0].message.content or "").strip()
        usage = response.usage
        return {
            "ok": True,
            "elapsed_ms": elapsed_ms,
            "reply": reply,
            "usage": {
                "prompt_tokens": usage.prompt_tokens if usage else 0,
                "completion_tokens": usage.completion_tokens if usage else 0,
            } if usage else None,
        }
    except Exception as e:
        elapsed_ms = round((time.perf_counter() - t0) * 1000)
        return {
            "ok": False,
            "elapsed_ms": elapsed_ms,
            "error": str(e),
        }