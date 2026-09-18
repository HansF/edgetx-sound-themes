"""Theme registry: every Theme subclass in this package with a real id."""
import importlib
import pkgutil

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
