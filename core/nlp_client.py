from dataclasses import dataclass
from typing import List, Dict, Any
from openai import OpenAI


@dataclass
class LLMConfig:
    base_url: str
    model: str
    api_key: str = "local"


class NLPClient:
    def __init__(self, cfg: LLMConfig) -> None:
        self.cfg = cfg
        self.client = OpenAI(base_url=cfg.base_url, api_key=cfg.api_key)

    def chat(self, messages: List[Dict[str, str]], **kwargs: Any) -> str:
        resp = self.client.chat.completions.create(model=self.cfg.model, messages=messages, **kwargs)
        return resp.choices[0].message.content
