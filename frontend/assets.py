from pathlib import Path


ASSETS_DIR = Path(__file__).resolve().parent


def asset_path(filename):
    return ASSETS_DIR / filename