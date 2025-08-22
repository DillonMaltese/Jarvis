# jarvis_wake_robot.py
import os, time
import speech_recognition as sr
from gtts import gTTS
from playsound import playsound

WAKE_WORD = "jarvis"
ACTIVE_WINDOW_SECONDS = 10
PHRASE_TIME_LIMIT = 5

def speak(text: str):
    fname = "_jarvis_tts.mp3"
    try:
        gTTS(text=text, lang='en').save(fname)
        playsound(fname)
    finally:
        try: os.remove(fname)
        except: pass

def transcribe_once(rec, src, limit=None):
    try:
        audio = rec.listen(src, timeout=None, phrase_time_limit=limit)
        return rec.recognize_google(audio).strip().lower()
    except sr.UnknownValueError:
        return None
    except sr.RequestError as e:
        print(f"[speech] API error: {e}"); return None

def handle_robot_command(text: str):
    if "create a new list" in text:
        speak("moving right")
    elif "move left" in text:
        speak("moving left")
    elif "move forward" in text:
         speak("moving forward")
    elif "move backward" in text or "move backwards" in text:
        speak("moving backwards")
    else:
        speak("unidentified")

if __name__ == "__main__":
    rec = sr.Recognizer()
    rec.dynamic_energy_threshold = True
    rec.pause_threshold = 0.8

    with sr.Microphone() as source:
        print("Calibrating mic…"); rec.adjust_for_ambient_noise(source, duration=1.0)
        speak("Jarvis Activated")
        print("Ready. Say 'Jarvis' to wake me.")

        while True:
            print("\nListening for wake word…")
            heard = transcribe_once(rec, source, limit=3)
            if not heard: continue
            print(f"[heard] {heard}")
            if WAKE_WORD in heard:
                print("✅ Wake word detected."); speak("Yes?")
                end = time.time() + ACTIVE_WINDOW_SECONDS
                print(f"Active for {ACTIVE_WINDOW_SECONDS}s. Speak your commands.")
                while time.time() < end:
                    text = transcribe_once(rec, source, limit=PHRASE_TIME_LIMIT)
                    if not text: continue
                    print(f"[command] {text}")
                    if any(p in text for p in ("never mind","cancel","thanks jarvis","go to sleep")):
                        speak("okay"); break
                    handle_robot_command(text)
                print("Back to wake mode.")
