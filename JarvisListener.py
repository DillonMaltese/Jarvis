# aQDJ7ENmJCEJEr/zWB9mM3wjoku9pdun5Yio9Z6qWWOtThqNM2oVKA==
import os
import struct
import pyaudio
import pvporcupine

# ===== Config =====
WAKEWORD = "jarvis"
ACCESS_KEY = os.getenv("PICOVOICE_ACCESS_KEY", "aQDJ7ENmJCEJEr/zWB9mM3wjoku9pdun5Yio9Z6qWWOtThqNM2oVKA==")
# ==================

def main():
    if not ACCESS_KEY or ACCESS_KEY.startswith("<PUT_"):
        raise RuntimeError("Set PICOVOICE_ACCESS_KEY env var or paste into ACCESS_KEY in code.")

    # Create Porcupine wake word engine
    porcupine = pvporcupine.create(
        access_key=ACCESS_KEY,
        keywords=[WAKEWORD]
    )

    pa = pyaudio.PyAudio()
    stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length
    )

    print("Listening for 'Jarvis'...")
    try:
        while True:
            pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm_unpacked = struct.unpack_from("h" * porcupine.frame_length, pcm)
            keyword_index = porcupine.process(pcm_unpacked)

            if keyword_index >= 0:
                print("✅ Heard 'Jarvis' — stopping.")
                break

    except KeyboardInterrupt:
        print("\nStopped by user.")
    finally:
        #Stop capturing audio (pyaudio)
        stream.stop_stream()
        #Stops the mic from staying in use
        stream.close()
        #Shuts down pyaudio entirely
        pa.terminate()
        #Cleans up wake word engine
        porcupine.delete()

if __name__ == "__main__":
    main()
