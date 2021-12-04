import lightbulb

from . import commands


def load(bot: lightbulb.BotApp) -> None:
    """Loads the module

    Args:
        bot (lightbulb.BotApp): The bot to load the module into
    """
    commands._load(bot)
