import os
import sys
from pathlib import Path

from PIL import ImageFont


def _font_directories():
    if os.name == "nt":
        return [Path(os.environ.get("WINDIR", "C:\\Windows")) / "Fonts"]
    if sys.platform == "darwin":
        return [Path("/Library/Fonts"), Path.home() / "Library" / "Fonts"]
    return [Path("/usr/share/fonts"), Path.home() / ".fonts", Path.home() / ".local" / "share" / "fonts"]


def load_font(size):
    for directory in _font_directories():
        if not directory.exists():
            continue
        for path in directory.rglob("*.ttf"):
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default()