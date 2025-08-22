from RealtimeSTT import AudioToTextRecorder

def on_text(t: str):
    if t:
        print(t)

if __name__ == "__main__":  # required on Windows (multiprocessing)
    # No wake_words -> continuous VAD. Starts when you speak.
    rec = AudioToTextRecorder(
        model="small.en",   # "tiny.en" = faster; "base.en/medium.en" = better but slower
        device="cpu"        # CPU only; no CUDA/cuDNN needed
    )
    print("Speak normally. VAD will start/stop segments. Ctrl+C to exit.")
    try:
        while True:
            rec.text(on_text)   # emits text for each detected segment
    except KeyboardInterrupt:
        pass
    finally:
        try:
            rec.shutdown()
        except Exception:
            pass
