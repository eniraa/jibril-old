import hikari
import lightbulb

from utils.defaults import CONSTANTS
import utils.models.lichess as lichess_models


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
    user = await lichess_models.LichessUser.load(ctx.options.username)
    embed = lichess_models.LichessUserFormatter.bio_embed(user)

    embeds = {"profile": embed, "rating": None, "history": None}

    if user.disabled:
        await ctx.respond(embed)
        return

    row = ctx.bot.rest.build_action_row()

    row.add_select_menu("navigation").set_placeholder("Navigate to…").add_option(
        "User profile", "profile"
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
            match event.interaction.values[0]:
                case "profile":
                    embed = embeds["profile"]
                case "rating":
                    embed = embeds[
                        "rating"
                    ] or lichess_models.LichessUserFormatter.rating_embed(user)
                case "history":
                    embed = embeds[
                        "history"
                    ] or await lichess_models.LichessUserFormatter.graph_embed(user)

            if not embeds[event.interaction.values[0]]:
                embeds[event.interaction.values[0]] = embed

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
