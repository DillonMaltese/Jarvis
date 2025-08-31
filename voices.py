# in Jarvis_backend.py
import asyncio, tempfile, os
from playsound import playsound
import edge_tts

VOICE = "en-US-GuyNeural"     # try: en-US-AriaNeural, en-GB-LibbyNeural, etc.
RATE  = "+0%"                 # e.g., "+10%" faster, "-10%" slower

async def _edge_tts_to_file(text, path):
    communicate = edge_tts.Communicate(text, VOICE, rate=RATE)
    await communicate.save(path)

def speak(text: str):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        out = f.name
    asyncio.run(_edge_tts_to_file(text, out))
    playsound(out)
    os.remove(out)
