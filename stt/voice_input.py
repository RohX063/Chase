import sounddevice as sd
import numpy as np
import librosa
from faster_whisper import WhisperModel

# Load once
model = WhisperModel("base", device="cpu", compute_type="int8")

# Use default device automatically
sd.default.channels = 1

def listen(duration=4):
    print("Listening...")

    # Record at native device sample rate
    device_info = sd.query_devices(kind='input')
    native_sr = int(device_info['default_samplerate'])

    recording = sd.rec(
        int(native_sr * duration),
        samplerate=native_sr,
        channels=1,
        dtype="int16"
    )
    sd.wait()

    # Convert to float
    audio = recording.astype(np.float32) / 32768.0
    audio = audio.flatten()

    # Resample to 16000 for Whisper
    audio = librosa.resample(audio, orig_sr=native_sr, target_sr=16000)

    segments, _ = model.transcribe(audio)
    text = "".join([seg.text for seg in segments]).strip()

    print("You (voice):", text)
    return text