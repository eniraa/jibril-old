from pathlib import Path
from typing import Sequence

import yaml

REGIONAL_INDICATOR_OFFSET = 0x1F1A5
TAG_OFFSET = 0xE0000
CANCELTAG = "\U000E007F"
BLACKFLAG = "\U0001F3F4"

with open(Path(__file__).parent / "emoji.yml", "r") as file:
    LICHESS_FLAGS = yaml.safe_load(file)["lichess"]["flags"]


def _regional_indicator(code: Sequence[str]) -> str:
    return "".join(
        map(lambda char: chr(ord(char.upper()) + REGIONAL_INDICATOR_OFFSET), code)
    )


def _tag(code: Sequence[str]) -> str:
    return (
        BLACKFLAG
        + "".join(map(lambda char: chr(ord(char.upper()) + TAG_OFFSET), code))
        + CANCELTAG
    )


def lichess_flag(code: str) -> str:
    """Returns the string to use on Discord for a given country from lichess.

    Args:
        code (str): The country code given.

    Returns:
        str: The emoji string to use.
    """
    if code in LICHESS_FLAGS:
        return LICHESS_FLAGS[code]
    elif len(code) == 2:
        return _regional_indicator(code)
    else:
        return _tag(code)
