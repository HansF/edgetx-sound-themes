"""Theme registry: every Theme subclass in this package with a real id."""
import importlib
import importlib.util
import os
import pkgutil
from pathlib import Path

from ..theme import Theme

REGISTRY = {}

for mod in pkgutil.iter_modules(__path__):
    m = importlib.import_module(f"{__name__}.{mod.name}")
    for obj in vars(m).values():
        if isinstance(obj, type) and issubclass(obj, Theme) and obj is not Theme and obj.id != "base":
            if obj.__module__ == m.__name__:
                REGISTRY[obj.id] = obj

CATEGORIES = [
    ("retro", "Retro consoles"),
    ("pc", "Old PCs & phones"),
    ("screen", "Screen & story"),
    ("sim", "Sim & tycoon"),
    ("meme", "Gen Z, Gen Alpha & weird"),
]


# Private themes: personal packs that must never be published (e.g. recreations of
# copyrighted game sounds). They live in private_themes/ (gitignored) and only load
# when STICKBEATS_PRIVATE=1, which `build.py --private` sets.
PRIVATE_DIR = Path(__file__).resolve().parents[2] / "private_themes"
if os.environ.get("STICKBEATS_PRIVATE") == "1" and PRIVATE_DIR.is_dir():
    CATEGORIES.append(("private", "Private · local only"))
    for f in sorted(PRIVATE_DIR.glob("*.py")):
        spec = importlib.util.spec_from_file_location(f"{__name__}._private_{f.stem}", f)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        for obj in vars(m).values():
            if isinstance(obj, type) and issubclass(obj, Theme) and obj.__module__ == m.__name__:
                obj.category = "private"
                REGISTRY[obj.id] = obj
