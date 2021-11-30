from pathlib import Path

import hikari
import matplotlib
import orjson

MODULES = [
    f"modules.{path.parts[-1]}"
    for path in (Path(__file__).parent.parent / "modules").glob("*/")
]
NIGHT_OPERA = hikari.Activity(
    name="Night Opera lose", type=hikari.ActivityType.WATCHING
)
with open(Path(__file__).parent / "constants.json", "rb") as file:
    CONSTANTS = orjson.loads(file.read())

MPL_COLOR = "white"

matplotlib.rcParams["text.color"] = MPL_COLOR
matplotlib.rcParams["axes.edgecolor"] = MPL_COLOR
matplotlib.rcParams["axes.labelcolor"] = MPL_COLOR
matplotlib.rcParams["xtick.color"] = MPL_COLOR
matplotlib.rcParams["ytick.color"] = MPL_COLOR
matplotlib.rcParams["legend.framealpha"] = 0
