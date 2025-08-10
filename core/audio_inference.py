import asyncio
from typing import AsyncGenerator
from edge_tts import Communicate


async def tts_say(text: str, voice: str = "tr-TR-ArdaNeural") -> None:
    com = Communicate(text, voice=voice)
    async for _ in com.stream():
        pass


async def dummy_stt_stream() -> AsyncGenerator[str, None]:
    # Yerleştirilebilir: faster-whisper canlı mikrofon transkripti
    while False:
        yield ""
