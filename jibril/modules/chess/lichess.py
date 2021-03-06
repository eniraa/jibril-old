import hikari
import lightbulb

from utils.defaults import CONSTANTS
from utils.models.lichess import LichessUser
from utils.views.lichess import LichessUserEmbed, LichessUserFormatter


@lightbulb.command("lichess", "All lichess commands")
@lightbulb.implements(lightbulb.commands.SlashCommandGroup)
async def lichess() -> None:
    """All lichess commands"""


@lichess.child
@lightbulb.option("username", "The username of the profile to look up", str)
@lightbulb.command("profile", "Return information about a profile")
@lightbulb.implements(lightbulb.commands.SlashSubCommand)
async def profile(ctx: lightbulb.context.SlashContext) -> None:
    """Returns information about a Lichess profile

    Args:
        ctx (lightbulb.context.Context): The command's invocation context
    """
    user = await LichessUser.load(ctx.options.username)
    formatter = LichessUserFormatter(user, ctx.bot)

    if user.disabled:
        await ctx.respond(await formatter.embed())
        return

    embed = await formatter.embed(LichessUserEmbed.bio)

    row = ctx.bot.rest.build_action_row()

    row.add_select_menu("navigation").set_placeholder("Navigate to…").add_option(
        "User profile", "bio"
    ).set_description(
        "The user's biographical and profile-related information."
    ).set_emoji(
        hikari.Emoji.parse(CONSTANTS["lichess"]["emoji"]["other"]["profile"])
    ).add_to_menu().add_option(
        "Ratings per gamemode", "rating"
    ).set_description(
        "The user's rating between various gamemodes."
    ).set_emoji(
        hikari.Emoji.parse(CONSTANTS["lichess"]["emoji"]["other"]["stats"])
    ).add_to_menu().add_option(
        "Rating history", "history"
    ).set_description(
        "The user's rating history from when they first started."
    ).set_emoji(
        hikari.Emoji.parse(CONSTANTS["lichess"]["emoji"]["other"]["rating"])
    ).add_to_menu().add_to_container()

    message = await ctx.respond(embed, components=[row])

    unwrapped_message = await message.message()

    with ctx.bot.stream(hikari.InteractionCreateEvent, 890).filter(
        lambda event: (
            isinstance(event.interaction, hikari.ComponentInteraction)
            and event.interaction.message == unwrapped_message
            # uncomment this if other people's interactions become problematic
            # and event.interaction.user == ctx.author
        )
    ) as stream:
        async for event in stream:
            embed = await formatter.embed(LichessUserEmbed(event.interaction.values[0]))

            try:
                await event.interaction.create_initial_response(
                    hikari.ResponseType.MESSAGE_UPDATE,
                    embed=embed,
                )
            except hikari.NotFoundError:
                await event.interaction.edit_initial_response(
                    embed=embed,
                )

    await message.edit(components=[])


def _load(bot: lightbulb.BotApp) -> None:
    bot.command(lichess)
