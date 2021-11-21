import lightbulb

from . import lichess


def load(bot: lightbulb.BotApp) -> None:
    """Loads the module

    Args:
        bot (lightbulb.BotApp): The bot to load the module into
    """
    lichess._load(bot)
