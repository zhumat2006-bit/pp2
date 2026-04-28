# настройки

import json
import os

SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "settings.json")

DEFAULTS = {
    "snake_color": [0, 200, 0],   # ргб лист
    "grid_overlay": False,
    "sound": True,
}


def load_settings() -> dict:
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                data = json.load(f)
            # Заполнение всех отсутствующих ключей значениями по умолчанию.
            for k, v in DEFAULTS.items():
                data.setdefault(k, v)
            return data
        except Exception as e:
            print(f"[Settings] load error: {e}")
    return dict(DEFAULTS)


def save_settings(settings: dict) -> bool:
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=2)
        return True
    except Exception as e:
        print(f"[Settings] save error: {e}")
        return False