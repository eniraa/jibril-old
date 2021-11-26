import hikari
import lightbulb
import requests

import utils.flags


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

    if data.get("disabled"):
        await ctx.respond("This account is closed")

    else:
        print(data)
        if data["online"]:
            statemoji = "<:status_online:902261836781613096>" + " (Online)"

        else:
            statemoji = "<:status_offline:902261836794200074>" + " (Offline)"

        country = data["profile"]["country"]
        print(country)
        flag1 = utils.flags.lichess_flag(country)

        count = data["count"]
        blitzrating = str(data["perfs"]["blitz"]["rating"])
        bulletrating = str(data["perfs"]["bullet"]["rating"])
        rapidrating = str(data["perfs"]["rapid"]["rating"])
        classicalrating = str(data["perfs"]["classical"]["rating"])

        if "prov" in data["perfs"]["blitz"]:
            blitzrating += "?"
        if "prov" in data["perfs"]["rapid"]:
            rapidrating += "?"
        if "prov" in data["perfs"]["bullet"]:
            bulletrating += "?"
        if "prov" in data["perfs"]["classical"]:
            classicalrating += "?"

        Games = (
            str(count["all"])
            + " ("
            + str(count["win"])
            + " Wins - "
            + str(count["draw"])
            + " Draws - "
            + str(count["loss"])
            + " Losses)"
        )
        URL = data.get("url")
        profile = data.get("profile")
        Description = profile.get("bio") or "This user's biography is empty"

        embed = (
            hikari.Embed(title=data["username"], url=URL, description="")
            .set_thumbnail("https://imgur.com/r3eEAy3.png")
            .add_field(name="Status:", value=statemoji, inline=False)
            .add_field(name="Games", value=Games, inline=False)
            .add_field(name="Bio: ", value=Description, inline=False)
            .add_field(name="Country: ", value=flag1, inline=False)
            .add_field(
                name="<:blitz:902261836899037234>"
                + "Blitz ["
                + str(data["perfs"]["blitz"]["games"])
                + "]",
                value=blitzrating,
                inline=True,
            )
            .add_field(
                name="<:rapid:902261836789993532>"
                + "Rapid ["
                + str(data["perfs"]["rapid"]["games"])
                + "]",
                value=rapidrating,
                inline=True,
            )
            .add_field(
                name="<:classical:902428900020338728>"
                + "Classical ["
                + str(data["perfs"]["classical"]["games"])
                + "]",
                value=classicalrating,
                inline=True,
            )
            .add_field(
                name="<:bullet:902261836752240640>"
                + "Bullet ["
                + str(data["perfs"]["bullet"]["games"])
                + "]",
                value=bulletrating,
                inline=True,
            )
        )

        await ctx.respond(embed)

    # await ctx.respond(data.__repr__())


def _load(bot: lightbulb.BotApp) -> None:
    bot.command(lichess)
