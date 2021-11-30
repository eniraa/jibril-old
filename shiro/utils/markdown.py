import re

_MARKDOWN_ESCAPE_COMMON = r"^>(?:>>)?\s|\[.+\]\(.+\)"
_MARKDOWN_STOCK_REGEX = fr"(?P<markdown>[_\\~|\*`]|{_MARKDOWN_ESCAPE_COMMON})"


def _escape_markdown(text: str) -> str:
    def _replacement(match: re.Match) -> str:
        groupdict = match.groupdict()
        is_url = groupdict.get("url")
        if is_url:
            return is_url
        return "\\" + groupdict["markdown"]

    return re.sub(_MARKDOWN_STOCK_REGEX, _replacement, text, 0, re.MULTILINE)


def _escape_mentions(text: str) -> str:
    return re.sub(r"@(everyone|here|[!&]?[0-9]{17,20})", "@\u200b\\1", text)


def escape(text: str | None) -> str:
    """Escapes markdown and mentions in a string

    Args:
        text (str | None): The string to sanitize

    Returns:
        str: The sanitized string
    """
    return _escape_markdown(_escape_mentions(text or ""))
