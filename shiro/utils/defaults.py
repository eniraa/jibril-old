from pathlib import Path

import hikari

__all__ = ["MODULES", "NIGHT_OPERA"]

MODULES = [
    f"modules.{path.parts[-1]}"
    for path in (Path(__file__).parent.parent / "modules").glob("*/")
]
NIGHT_OPERA = hikari.Activity(
    name="Night Opera lose", type=hikari.ActivityType.WATCHING
)
