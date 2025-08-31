import os, time, threading, re
import speech_recognition as sr
from playsound import playsound
from Jarvis_backend import speak, transcribe_once, get_input
from Lights import plug2
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

TZ = ZoneInfo("America/New_York")
WAKE_WORD = "jarvis"

# Where we determine what to do given a command
def handle_robot_command(text: str):
    if "lights on" in text:
        speak("Turning the lights on")
        state = plug2("on")
        if state is None:
            speak("I couldn't reach the light")
        return
    
    elif "lights off" in text:
        speak("Turning the lights off")
        state = plug2("off")
        if state is None:
            speak("I couldn't reach the light")
        return
    
    elif "create a list" in text:
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

    elif "list lists" in text:
        speak("Here are your lists:")
        todo_dir = "todo"
        if os.path.exists(todo_dir):
            lists = [f.replace(".todo.md", "") for f in os.listdir(todo_dir) if f.endswith(".todo.md")]
            if lists:
                speak(", ".join(lists))
            else:
                speak("No lists found.")
        else:
            speak("No lists found.")

    elif "list tasks" in text:
        speak("Which list's tasks would you like to see?")
        list_name = get_input(rec, source)
        if not list_name:
            speak("No list specified. Cancelling task listing.")
            return
        elif not os.path.exists(f"todo/{list_name}.todo.md"):
            speak(f"List {list_name} does not exist. Cancelling task listing.")
            return
        speak("Here are the tasks:")
        with open(f"todo/{list_name}.todo.md", "r") as f:
            tasks = f.readlines()
        if tasks:
            speak("".join(tasks))
        else:
            speak("No tasks found.")

    elif "remind me to" in text:
        match = re.search(r"remind me to (.+?) (at|on|in) (.+)", text)
        if match:
            task = match.group(1).strip()
            time_part = match.group(3).strip()
            when_dt = None

            if " at " in text:
                try:
                    when_dt = datetime.strptime(time_part, "%I %p").replace(tzinfo=TZ)
                    if when_dt < datetime.now(TZ):
                        when_dt += timedelta(days=1)
                except ValueError:
                    speak("I couldn't understand the time format. Please use 'H AM/PM'.")
                    return
            elif " on " in text:
                try:
                    when_dt = datetime.strptime(time_part, "%B %d at %I %p").replace(year=datetime.now(TZ).year, tzinfo=TZ)
                    if when_dt < datetime.now(TZ):
                        when_dt = when_dt.replace(year=when_dt.year + 1)
                except ValueError:
                    speak("I couldn't understand the date format. Please use 'Month Day at H AM/PM'.")
                    return
            elif " in " in text:
                try:
                    num, unit = time_part.split()
                    num = int(num)
                    if "minute" in unit:
                        when_dt = datetime.now(TZ) + timedelta(minutes=num)
                    elif "hour" in unit:
                        when_dt = datetime.now(TZ) + timedelta(hours=num)
                    elif "day" in unit:
                        when_dt = datetime.now(TZ) + timedelta(days=num)
                except (ValueError, IndexError):
                    speak("I couldn't understand the duration format. Please use 'X minutes/hours/days'.")
                    return

            if when_dt:
                schedule_reminder(task, when_dt, speak)
                speak(f"Reminder set for {task} at {when_dt.strftime('%I:%M %p on %B %d')}")
            else:
                speak("I couldn't determine when to set the reminder.")
        else:
            speak("Please specify the task and time for the reminder.") 

    else:
        speak("not sure what you're trying to say")

def schedule_reminder(task: str, when_dt: datetime, speak):
    delay = max((when_dt - datetime.now(TZ)).total_seconds(), 0)
    def _ding():
        speak(f"Reminder: {task}")
    timer = threading.Timer(delay, _ding)
    timer.daemon = True
    timer.start()
    return timer

if __name__ == "__main__":
    rec = sr.Recognizer()
    rec.dynamic_energy_threshold = True
    rec.pause_threshold = 0.8

    with sr.Microphone() as source:
        print("Calibrating mic…"); rec.adjust_for_ambient_noise(source, duration=1.0)
        # speak("Jarvis Activated")
        speak("Good evening. All systems are nominal.")
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
