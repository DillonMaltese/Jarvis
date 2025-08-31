import os, time, asyncio, tempfile
import speech_recognition as sr
from gtts import gTTS
from playsound import playsound
import edge_tts

ACTIVE_WINDOW_SECONDS = 10
PHRASE_TIME_LIMIT = 5
VOICE  = "en-GB-ThomasNeural"
RATE   = "-10%"
PITCH  = "-10Hz"
VOLUME = "+0%"

async def _edge_tts_to_file(text: str, path: str):
    communicate = edge_tts.Communicate(text, VOICE, rate=RATE, volume=VOLUME, pitch=PITCH)
    await communicate.save(path)

def _run_tts_sync(text: str, path: str):
    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        loop.run_until_complete(_edge_tts_to_file(text, path))
    finally:
        try: loop.close()
        except: pass
        asyncio.set_event_loop(asyncio.new_event_loop())

def speak(text: str):
    out = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            out = f.name
        _run_tts_sync(text, out)

        if not os.path.exists(out) or os.path.getsize(out) < 512:
            raise RuntimeError("TTS output file missing/empty — check internet or voice name.")

        playsound(out)
    except Exception as e:
        print(f"[TTS error] {type(e).__name__}: {e}")
    finally:
        if out:
            try: os.remove(out)
            except: pass

# Get user input function
def get_input(rec, source):
    end = time.time() + ACTIVE_WINDOW_SECONDS
    print(f"Active for {ACTIVE_WINDOW_SECONDS}s. Speak your commands.")
    while time.time() < end:
        text = transcribe_once(rec, source, limit=PHRASE_TIME_LIMIT)
        if not text: continue
        print(f"[command] {text}")
        if any(p in text for p in ("never mind","cancel","thanks jarvis","go to sleep")):
            speak("okay"); return None
        return text
    
# Speech recognition function
def transcribe_once(rec, src, limit=None):
    try:
        audio = rec.listen(src, timeout=None, phrase_time_limit=limit)
        return rec.recognize_google(audio).strip().lower()
    except sr.UnknownValueError:
        return None
    except sr.RequestError as e:
        print(f"[speech] API error: {e}"); return None