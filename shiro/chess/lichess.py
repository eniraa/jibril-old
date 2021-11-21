import lightbulb
import requests


@lightbulb.command("lichess", "All lichess commands")
@lightbulb.implements(lightbulb.commands.SlashCommandGroup)
async def lichess() -> None:
    """All lichess commands"""


@lichess.child
@lightbulb.option("username", "The username of the profile to look up", str)
@lightbulb.command("profile", "Return information about a profile")
@lightbulb.implements(lightbulb.commands.SlashSubCommand)
async def profile(ctx: lightbulb.context.Context) -> None:
    """Returns information about a Lichess profile

    Args:
        ctx (lightbulb.context.Context): The command's invocation context
    """
    data = requests.get(f"https://lichess.org/api/user/{ctx.options.username}").json()
    await ctx.respond(data.__repr__())


def load(bot: lightbulb.BotApp) -> None:
    """Loads the module

    Args:
        bot (lightbulb.BotApp): The bot to load the module into
    """
    bot.command(lichess)
