from utils.defaults import CONSTANTS

REGIONAL_INDICATOR_OFFSET = 0x1F1A5
TAG_OFFSET = 0xE0000
CANCELTAG = "\U000E007F"
BLACKFLAG = "\U0001F3F4"

LICHESS_FLAGS = CONSTANTS["lichess"]["emoji"]["flags"]


def _regional_indicator(code: str) -> str:
    return "".join(chr(ord(char.upper()) + REGIONAL_INDICATOR_OFFSET) for char in code)


def _tag(code: str) -> str:
    return (
        BLACKFLAG
        + "".join(chr(ord(char.upper()) + TAG_OFFSET) for char in code)
        + CANCELTAG
    )
