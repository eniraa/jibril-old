import logging

import hikari
import lightbulb
import requests

import utils.lichess


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
        if data.get("patron"):
            if data["online"]:
                state = utils.lichess.EMOJI["status"]["patron"]["online"]
            else:
                state = utils.lichess.EMOJI["status"]["patron"]["offline"]
        else:
            if data["online"]:
                state = utils.lichess.EMOJI["status"]["normie"]["online"]
            else:
                state = utils.lichess.EMOJI["status"]["normie"]["offline"]

        logging.debug(f"Lichess profile of {ctx.options.username}: {data.__repr__()}")

        if profile := data.get("profile"):
            location = ""
            if "country" in profile:
                location += utils.lichess.flag(profile["country"])
            if "location" in profile:
                location += " " + profile["location"]

            description = f"{profile.get('bio', '')}\n\n{location}"
        else:
            description = None

        count = data["count"]

        games = (
            f"**Wins: {count['win']}**\n**Losses: {count['loss']}**\n**Draws: "
            + f"{count['draw']}**\nRated: {count['rated']}\nBot: {count['ai']}\n\n*"
            + f"{data['completionRate']}% completion*"
        )

        title = f" [{data.get('title')}]" if "title" in data else ""

        embed = (
            hikari.Embed(
                title=f"{state}{title} {data['username']}",
                url=data["url"],
                description=description,
            )
            .set_thumbnail("https://imgur.com/r3eEAy3.png")
            .add_field(
                name=f"{utils.lichess.EMOJI['other']['challenge']} Games "
                + f"[{count['all']}]",
                value=games,
                inline=False,
            )
        )

        for mode in utils.lichess.DISPLAY_MODES:
            if mode not in data.get("perfs", []):
                continue

            display = utils.lichess.mode_display(mode)
            emoji = utils.lichess.mode_emoji(mode)
            performance = data["perfs"][mode]

            if "rating" in performance:
                rating = performance["rating"]
                games = performance["games"]
                deviation = performance["rd"]
                if (prog := performance["prog"]) > 0:
                    progression = f"\n{utils.lichess.EMOJI['other']['up']} {prog}"
                elif prog < 0:
                    progression = f"\n{utils.lichess.EMOJI['other']['down']} {prog}"
                else:
                    progression = ""

                embed = embed.add_field(
                    name=f"{emoji} {display} [{games}]",
                    value=f"{utils.lichess.EMOJI['other']['rating']} {rating} ± "
                    + f"{deviation} {progression}",
                    inline=True,
                )
            else:
                rating = performance["score"]
                games = performance["runs"]
                embed = embed.add_field(
                    name=f"{emoji} {display} [{games}]",
                    value=f"{utils.lichess.EMOJI['other']['rating']} {rating}",
                    inline=True,
                )

        await ctx.respond(embed)


def _load(bot: lightbulb.BotApp) -> None:
    bot.command(lichess)
