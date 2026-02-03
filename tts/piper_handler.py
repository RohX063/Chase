import subprocess
import simpleaudio as sa
import os
import re

def speak(text):

    print(">>> SPEAK CALLED")
    text = clean_for_speech(text)
    
    piper_path = r"C:\piper_windows_amd64\piper\piper.exe"
    model_path = r"C:\piper_windows_amd64\piper\models\en_US-ryan-medium.onnx"
    output_path = "temp_audio.wav"

    command = [
        piper_path,
        "-m", model_path,
        "-f", output_path
    ]

    subprocess.run(command, input=text, text=True)

    wave_obj = sa.WaveObject.from_wave_file(output_path)
    play_obj = wave_obj.play()
    play_obj.wait_done()

    os.remove(output_path)
    import re

def clean_for_speech(text):
    # Remove markdown bold/italic
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)

    # Remove standalone special characters
    text = re.sub(r"[#\-•]", "", text)

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()