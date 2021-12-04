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


def flag(code: str) -> str:
    """Generates a flag emoji based on a country code.

    Args:
        code (str): The country code to generate the flag for.

    Raises:
        ValueError: If the code is not a valid country code.

    Returns:
        str: The flag generated.
    """
    if len(code) == 2:
        return _regional_indicator(code)
    elif len(code) > 2:
        return _tag(code)
    raise ValueError("Invalid flag code")
