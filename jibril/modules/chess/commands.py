from enum import Enum

import lightbulb

from utils.views import lichess


class Site(Enum):
    """All supported sites."""

    bot = "jibril"
    lichess = "lichess"
    chesscom = "chess.com"
    chess24 = "chess24"


@lightbulb.command("chess", "All chess commands")
@lightbulb.implements(lightbulb.commands.SlashCommandGroup)
async def chess() -> None:
    """All chess commands"""


@chess.child
@lightbulb.option("username", "The username of the profile to look up", str)
# uncomment when other implementations are done
# @lightbulb.option(
#     "locus", "The site to query", str, choices=[locus.value for locus in Site]
# )
@lightbulb.option("locus", "The site to query", str, choices=["lichess"])
@lightbulb.command("profile", "Return information about a profile")
@lightbulb.implements(lightbulb.commands.SlashSubCommand)
async def profile(ctx: lightbulb.context.SlashContext) -> None:
    """Returns information about a chess profile

    Args:
        ctx (lightbulb.context.Context): The command's invocation context
    """
    match Site(ctx.options.locus):
        case Site.lichess:
            await lichess.profile(ctx)
        case _:
            pass


def _load(bot: lightbulb.BotApp) -> None:
    bot.command(chess)
