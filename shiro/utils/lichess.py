from pathlib import Path

import yaml

import utils.flags

with open(Path(__file__).parent / "alias.yml", "r") as file:
    DISPLAY_MODES = yaml.safe_load(file)["lichess"]["modes"]

with open(Path(__file__).parent / "emoji.yml", "r") as file:
    EMOJI = yaml.safe_load(file)["lichess"]


def flag(code: str) -> str:
    """Returns the string to use on Discord for a given country from lichess.

    Args:
        code (str): The country code given.

    Returns:
        str: The emoji string to use.
    """
    if code in utils.flags.LICHESS_FLAGS:
        return utils.flags.LICHESS_FLAGS[code]
    elif len(code) == 2:
        return utils.flags._regional_indicator(code)
    else:
        return utils.flags._tag(code)


def mode_display(mode: str) -> str:
    """Returns the displayed mode for a lichess mode.

    Args:
        mode (str): The mode of a game.

    Returns:
        str: The displayed mode.
    """
    return DISPLAY_MODES.get(mode, mode)


def mode_emoji(mode: str) -> str:
    """Returns the mode emoji for a lichess mode.

    Args:
        mode (str): The mode of a game.

    Returns:
        str: The mode emoji.
    """
    return EMOJI["modes"].get(mode, "♟️")
