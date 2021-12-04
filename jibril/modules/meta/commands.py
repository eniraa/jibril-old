import math

import hikari
import lightbulb


@lightbulb.command("meta", "All bot-related commands")
@lightbulb.implements(lightbulb.commands.SlashCommandGroup)
async def meta() -> None:
    """All bot-related commands"""


@meta.child
@lightbulb.option(
    "precision",
    "The number of significant digits to round the latency to",
    int,
    required=False,
)
@lightbulb.command("ping", "Return latency information about the bot")
@lightbulb.implements(lightbulb.commands.SlashSubCommand)
async def ping(ctx: lightbulb.context.SlashContext) -> None:
    """Returns latency information about the bot

    Args:
        ctx (lightbulb.context.Context): The command's invocation context
    """
    latency = ctx.bot.heartbeat_latency
    sigfigs = ctx.options.precision or 3

    ms = round(latency, -int(math.floor(math.log10(latency))) + (sigfigs - 1)) * 1000
    if ms % 1 == 0:
        ms = int(ms)

    await ctx.respond(
        hikari.Embed(
            title="🏓 Pong!",
            description=f"Latency: {ms} ms",
        )
    )


def _load(bot: lightbulb.BotApp) -> None:
    bot.command(meta)
