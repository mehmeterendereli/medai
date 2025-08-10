import asyncio
import json
import os
import toml
import websockets
from pathlib import Path
from .agent import Agent
from .nlp_client import LLMConfig
from .tools_registry import ToolsRegistry


async def hud_server(host: str, port: int):
    clients = set()

    async def broadcast(sender, payload: str):
        dead = []
        for ws in clients:
            if ws is sender:
                continue
            try:
                await ws.send(payload)
            except Exception:
                dead.append(ws)
        for d in dead:
            clients.discard(d)

    async def handler(websocket):
        clients.add(websocket)
        # İlk bağlantıda boot mesajını gönder
        await websocket.send(json.dumps({"type": "boot", "message": "Sistemi başlatmamı onaylıyor musunuz?"}))
        try:
            async for message in websocket:
                # Alınan mesajları diğer istemcilere yayınla (agent <-> HUD)
                await broadcast(websocket, message)
        except websockets.ConnectionClosed:
            pass
        finally:
            clients.discard(websocket)

    async with websockets.serve(handler, host, port):
        await asyncio.Future()


async def main():
    cfg = toml.load(str(Path(__file__).resolve().parents[1] / 'configs' / 'config.toml'))
    ws_host = cfg.get('hud', {}).get('ws_host', '127.0.0.1')
    ws_port = int(cfg.get('hud', {}).get('ws_port', 8765))
    llm_enabled = bool(cfg.get('llm', {}).get('enabled', False))
    base_url = cfg.get('llm', {}).get('base_url', '') if llm_enabled else ''
    llm_cfg = LLMConfig(
        base_url=base_url,
        model=cfg.get('llm', {}).get('model', 'openai/gpt-oss-20b'),
        api_key=cfg.get('llm', {}).get('api_key', 'local'),
    )

    # HUD köprüsü sunucusunu başlat
    server_task = asyncio.create_task(hud_server(ws_host, ws_port))

    # Agent
    registry = ToolsRegistry()
    agent = Agent(ws_host, ws_port, llm_cfg, registry)
    agent_task = asyncio.create_task(agent.run())

    await asyncio.gather(server_task, agent_task)


if __name__ == "__main__":
    asyncio.run(main())
