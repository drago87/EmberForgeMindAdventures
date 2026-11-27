import json
from pathlib import Path


def load_languages(lang_dir: Path):
    langs = {}
    for file in lang_dir.glob("*.json"):
        try:
            with file.open("r", encoding="utf-8") as f:
                data = json.load(f)
                key = file.stem
                langs[key] = data
        except Exception:
            pass
    return langs


def get_translation_func(langs, lang_code):
    def t(key):
        # Try requested language
        data = langs.get(lang_code, {})
        if key in data:
            return data[key]
        # Fallback to English
        return langs.get("en", {}).get(key, key)
    return t

__all__ = ["load_languages", "get_translation_func"]
