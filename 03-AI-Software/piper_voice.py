import json
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

import numpy as np


BASE_DIR = Path(__file__).resolve().parent
PROFILE_PATH = BASE_DIR / "piper_voice_profile.json"
VOICES_DIR = BASE_DIR / "voices"


def load_piper_profile():
    with PROFILE_PATH.open("r", encoding="utf-8") as file:
        profile = json.load(file)

    if not isinstance(profile, dict):
        raise ValueError("Invalid Piper voice profile")

    return profile


def synthesize_piper(text, output_path):
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Speech text must be nonempty")

    profile = load_piper_profile()

    model_name = profile["model"]

    if (
        not isinstance(model_name, str)
        or not model_name
        or Path(model_name).name != model_name
    ):
        raise ValueError("Invalid Piper model name")

    model = VOICES_DIR / (model_name + ".onnx")
    config = VOICES_DIR / (model_name + ".onnx.json")

    if not model.is_file() or not config.is_file():
        raise FileNotFoundError("Piper voice model is missing")

    length_scale = float(profile["length_scale"])
    noise_scale = float(profile["noise_scale"])
    gain = float(profile["audio_gain"])

    if length_scale <= 0 or noise_scale < 0:
        raise ValueError("Invalid synthesis parameters")

    if not 0 <= gain <= 1:
        raise ValueError("Audio gain must be between 0 and 1")

    destination = Path(output_path).resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as directory:
        raw = Path(directory) / "raw.wav"

        command = [
            sys.executable,
            "-m",
            "piper",
            "--model",
            str(model),
            "--config",
            str(config),
            "--output_file",
            str(raw),
            "--length-scale",
            str(length_scale),
            "--noise-scale",
            str(noise_scale),
        ]

        result = subprocess.run(
            command,
            input=text,
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.returncode != 0:
            raise RuntimeError(
                "Piper synthesis failed: " + result.stderr[-1000:]
            )

        with wave.open(str(raw), "rb") as audio:
            params = audio.getparams()

            if params.sampwidth != 2:
                raise ValueError("Expected 16-bit PCM audio")

            samples = np.frombuffer(
                audio.readframes(audio.getnframes()),
                dtype="<i2",
            ).astype(np.float64)

        adjusted = np.clip(
            samples * gain,
            -32768,
            32767,
        ).astype("<i2")

        with wave.open(str(destination), "wb") as audio:
            audio.setparams(params)
            audio.writeframes(adjusted.tobytes())

    return destination


def play_piper_file(path):
    import winsound

    winsound.PlaySound(
        str(Path(path).resolve()),
        winsound.SND_FILENAME,
    )


def speak_piper(text):
    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory) / "moxxi_speech.wav"
        synthesize_piper(text, output)
        play_piper_file(output)

    return True
