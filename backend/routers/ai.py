"""AI 关键词提示词（覆盖 `data.AI_KEYWORD_PROMPT`，存 `user_ai_prompt.txt`）。"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.path_utils import project_root

_PROMPT_FILE = project_root() / "user_ai_prompt.txt"

router = APIRouter()


class PromptBody(BaseModel):
    prompt: str = Field(..., min_length=1)


@router.get("/prompt")
def get_ai_prompt():
    from data import AI_KEYWORD_PROMPT

    if _PROMPT_FILE.is_file():
        try:
            t = _PROMPT_FILE.read_text(encoding="utf-8")
            if t.strip():
                return {"prompt": t, "source": "user_ai_prompt.txt"}
        except OSError:
            pass
    return {"prompt": AI_KEYWORD_PROMPT, "source": "data.py"}


@router.post("/prompt")
def save_ai_prompt(body: PromptBody):
    try:
        _PROMPT_FILE.write_text(body.prompt.strip(), encoding="utf-8")
    except OSError as e:
        raise HTTPException(500, detail=str(e)) from e
    return {"ok": True, "path": str(_PROMPT_FILE)}
