"""Offline Windows text-to-speech interface for MOXXI."""

import subprocess
import sys

DEFAULT_VOICE = "Microsoft Zira Desktop"


def speak(text, rate=-1, volume=100, voice=DEFAULT_VOICE):
    """Speak text through Windows System.Speech."""

    if not isinstance(text, str) or not text.strip():
        return False

    if sys.platform != "win32":
        return False

    if not isinstance(rate, int) or not -10 <= rate <= 10:
        raise ValueError("Rate must be between -10 and 10")

    if not isinstance(volume, int) or not 0 <= volume <= 100:
        raise ValueError("Volume must be between 0 and 100")

    script = r"""
$ErrorActionPreference = 'Stop'
$synth = $null

try {
    Add-Type -AssemblyName System.Speech
    $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
    $synth.SelectVoice($env:MOXXI_VOICE)
    $synth.Rate = [int]$env:MOXXI_RATE
    $synth.Volume = [int]$env:MOXXI_VOLUME
    $synth.Speak($env:MOXXI_SPEECH_TEXT)
}
finally {
    if ($null -ne $synth) {
        $synth.Dispose()
    }
}
"""

    import os

    environment = os.environ.copy()
    environment["MOXXI_VOICE"] = voice
    environment["MOXXI_RATE"] = str(rate)
    environment["MOXXI_VOLUME"] = str(volume)
    environment["MOXXI_SPEECH_TEXT"] = text

    try:
        result = subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-NonInteractive",
                "-Command",
                script,
            ],
            env=environment,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False

    return result.returncode == 0


if __name__ == "__main__":
    print("=== MOXXI VOICE MODULE TEST ===")

    success = speak(
        "Hello, darling! MOXXI's Python voice system is online."
    )

    print("VOICE TEST PASSED:", success)

    if not success:
        raise SystemExit(1)
