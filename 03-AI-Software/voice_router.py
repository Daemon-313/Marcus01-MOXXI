"""Select MOXXI's offline speech engine."""

from voice_settings import load_voice_settings


def speak(text):
    """Speak using the configured engine, with Windows fallback."""

    if not isinstance(text, str) or not text.strip():
        return False

    settings = load_voice_settings()

    if not settings.get("enabled", True):
        return False

    engine = settings.get("engine", "windows")

    if engine == "piper":
        try:
            from piper_voice import speak_piper
            return speak_piper(text) is True
        except Exception as error:
            print("Piper voice unavailable:", error)
            print("Attempting Windows voice fallback.")

    elif engine != "windows":
        print("Unknown voice engine:", engine)
        return False

    from voice import speak as windows_speak

    try:
        return windows_speak(
            text,
            voice=settings.get(
                "voice",
                "Microsoft Zira Desktop"
            )
        )
    except Exception as error:
        print("Windows voice unavailable:", error)
        return False
