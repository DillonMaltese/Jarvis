import os, time
import speech_recognition as sr
from gtts import gTTS
from playsound import playsound

ACTIVE_WINDOW_SECONDS = 10
PHRASE_TIME_LIMIT = 5

# Text-to-speech function
def speak(text: str):
    # Take temporary voice file
    fname = "_jarvis_tts.mp3"
    try:
        # Run the text-to-speech conversion
        gTTS(text=text, lang='en').save(fname)
        playsound(fname)
    finally:
        # Clean up temporary file
        try: os.remove(fname)
        except: pass

# Speech recognition function
def transcribe_once(rec, src, limit=None):
    try:
        audio = rec.listen(src, timeout=None, phrase_time_limit=limit)
        return rec.recognize_google(audio).strip().lower()
    except sr.UnknownValueError:
        return None
    except sr.RequestError as e:
        print(f"[speech] API error: {e}"); return None

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