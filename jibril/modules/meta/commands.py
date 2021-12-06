import math

import hikari
import lightbulb

from utils.defaults import CONSTANTS


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


@meta.child
@lightbulb.command("about", "Return information about the bot")
@lightbulb.implements(lightbulb.commands.SlashSubCommand)
async def about(ctx: lightbulb.context.SlashContext) -> None:
    """Returns information about the bot

    Args:
        ctx (lightbulb.context.Context): The command's invocation context
    """
    devs = [
        f"{CONSTANTS['jibril']['emoji']['developer']} "
        + f"[{(user := await ctx.bot.rest.fetch_user(dev)).username}#"
        + f"{user.discriminator}](https://discord.com/users/{dev})"
        for dev in CONSTANTS["jibril"]["devs"]
    ]

    links = "\n".join(
        [
            "\n".join(devs),
            f"{CONSTANTS['jibril']['emoji']['invite']} "
            + "[Invite](https://discord.com/api/oauth2/"
            + f"authorize?client_id={ctx.bot.get_me().id}"
            + f"&permissions={CONSTANTS['jibril']['permissions']}"
            + "&scope=bot%20applications.commands)",
            f"{CONSTANTS['jibril']['emoji']['vcs']} [Repository]"
            + f"({CONSTANTS['jibril']['uri']['repo']})",
        ]
    )

    await ctx.respond(
        hikari.Embed(
            title="Jibril",
            description=f"A Discord bot for chat games.\n\n{links}",
        )
        .set_thumbnail(CONSTANTS["jibril"]["assets"]["logo"])
        .set_image(CONSTANTS["jibril"]["assets"]["banner"])
    )


def _load(bot: lightbulb.BotApp) -> None:
    bot.command(meta)
