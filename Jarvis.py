# jarvis_wake_robot.py
import os, time
import speech_recognition as sr
from gtts import gTTS
from playsound import playsound
from Jarvis_backend import speak, transcribe_once, get_input

WAKE_WORD = "jarvis"

def handle_robot_command(text: str):
    if "create a new list" in text:
        speak("What would you like to name the list?")
        list_name = get_input(rec, source)
        if list_name:
            print(f"Creating a new list named: {list_name}")
            os.makedirs("todo", exist_ok=True)
        with open(f"todo/{list_name}.todo.md", "w") as f:
            f.write(f"{list_name}\n")
        speak(f"Created a new list named {list_name}")

    elif "remove a list" in text:
        speak("Which list would you like to remove?")
        list_name = get_input(rec, source)
        if not list_name:
            speak("No list specified. Cancelling list removal.")
            return
        try:
            os.remove(f"todo/{list_name}.todo.md")
            speak(f"Removed list: {list_name}")
        except FileNotFoundError:
            speak(f"List {list_name} does not exist.")

    elif "add a task" in text:
        speak("To which list?")
        list_name = get_input(rec, source)
        if not list_name:
            speak("No list specified. Cancelling task addition.")
            return
        speak("What is the task?")
        task = get_input(rec, source)
        if task:
            print(f"Adding task: {task}")
            os.makedirs("todo", exist_ok=True)
            with open(f"todo/{list_name}.todo.md", "a") as f:
                f.write(f"{task}\n")
            speak(f"Added task: {task}")

    elif "remove a task" in text:
        speak("From which list?")
        list_name = get_input(rec, source)
        if not list_name:
            speak("No list specified. Cancelling task removal.")
            return
        elif not os.path.exists(f"todo/{list_name}.todo.md"):
            speak(f"List {list_name} does not exist. Cancelling task removal.")
            return
        speak("What is the task to remove?")
        task = get_input(rec, source)
        if task:
            print(f"Removing task: {task} from list: {list_name}")
            try:
                with open(f"todo/{list_name}.todo.md", "r") as f:
                    tasks = f.readlines()
                with open(f"todo/{list_name}.todo.md", "w") as f:
                    for line in tasks:
                        if line.strip() != task:
                            f.write(line)
                speak(f"Removed task: {task} from list: {list_name}")
            except FileNotFoundError:
                speak(f"List {list_name} does not exist.")

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
        # speak("Jarvis Activated")
        print("Ready. Say 'Jarvis' to wake me.")

        while True:
            print("\nListening for wake word…")
            heard = transcribe_once(rec, source, limit=3)
            if not heard: continue
            print(f"[heard] {heard}")
            if WAKE_WORD in heard:
                print("Wake word detected."); speak("Yes?")
                command = get_input(rec, source)
                if command:
                    handle_robot_command(command)
                print("Back to wake mode.")
