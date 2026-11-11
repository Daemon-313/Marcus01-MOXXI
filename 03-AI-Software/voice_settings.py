import json
from pathlib import Path

SETTINGS_FILE = Path(__file__).parent / "voice_settings.json"

DEFAULT_SETTINGS = {
    "enabled": True,
    "engine": "windows",
    "voice": "Microsoft Zira Desktop"
}


def load_voice_settings():
    if not SETTINGS_FILE.exists():
        return DEFAULT_SETTINGS.copy()

    try:
        with SETTINGS_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            return DEFAULT_SETTINGS.copy()

        settings = DEFAULT_SETTINGS.copy()
        settings.update(data)
        return settings

    except (OSError, json.JSONDecodeError):
        return DEFAULT_SETTINGS.copy()


def save_voice_settings(settings):
    with SETTINGS_FILE.open("w", encoding="utf-8") as file:
        json.dump(settings, file, indent=4)


def voice_enabled():
    return load_voice_settings()["enabled"] is True


def set_voice_enabled(enabled):
    settings = load_voice_settings()
    settings["enabled"] = bool(enabled)
    save_voice_settings(settings)
    return settings["enabled"]
