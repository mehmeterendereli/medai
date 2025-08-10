import asyncio
import json
import websockets
from typing import Any, Dict, List
from .state import StateContext, AgentState
from .nlp_client import NLPClient, LLMConfig
from .tools_registry import ToolsRegistry, build_default_registry


class Agent:
    def __init__(self, ws_host: str, ws_port: int, llm_cfg: LLMConfig, registry: ToolsRegistry | None = None) -> None:
        self.ws_host = ws_host
        self.ws_port = ws_port
        self.llm = NLPClient(llm_cfg)
        self.registry = registry or build_default_registry()
        self.state = StateContext()

    async def _ws_emit(self, ws, payload: Dict[str, Any]) -> None:
        try:
            await ws.send(json.dumps(payload))
        except Exception:
            pass

    async def run(self) -> None:
        uri = f"ws://{self.ws_host}:{self.ws_port}"
        while True:
            try:
                async with websockets.connect(uri) as ws:
                    await self._ws_emit(ws, {"type": "state", "value": self.state.current})
                    async for msg in ws:
                        data = json.loads(msg)
                        if data.get("type") == "confirm_boot" and data.get("accept"):
                            await self._ws_emit(ws, {"type": "state", "value": AgentState.LISTENING})
                            self.state.set(AgentState.LISTENING)
                        elif data.get("type") == "hotkey" and data.get("action") == "kill":
                            self.state.set(AgentState.IDLE)
                            await self._ws_emit(ws, {"type": "state", "value": AgentState.IDLE})
                        elif data.get("type") == "task":
                            goal = data.get("goal", "")
                            await self.execute_goal(ws, goal)
            except Exception:
                await asyncio.sleep(1)

    async def execute_goal(self, ws, goal: str) -> None:
        self.state.set(AgentState.EXECUTING)
        await self._ws_emit(ws, {"type": "state", "value": self.state.current})
        # Basit plan: sadece yankıla
        plan: List[str] = [f"Görev alındı: {goal}"]
        await self._ws_emit(ws, {"type": "plan", "steps": plan})
        await self._ws_emit(ws, {"type": "result", "ok": True, "summary": f"Tamamlandı: {goal}"})
        self.state.set(AgentState.IDLE)
        await self._ws_emit(ws, {"type": "state", "value": self.state.current})
