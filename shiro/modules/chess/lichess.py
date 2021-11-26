import logging

import bs4
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

    soup = bs4.BeautifulSoup(requests.get(data["url"]).text, "html.parser")

    trophies = []

    for trophy in soup.find_all(class_="trophy"):
        for emoji in utils.lichess.EMOJI["trophy"]:
            if emoji in trophy["class"]:
                trophies.append(utils.lichess.EMOJI["trophy"][emoji])
                break

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

        description = [" ".join(trophies)]

        if profile := data.get("profile"):
            if "bio" in profile:
                description.append(profile["bio"])

            location = []
            if "country" in profile:
                location.append(utils.lichess.flag(profile["country"]))
            if "location" in profile:
                location.append(profile["location"])

            if location:
                description.append(" ".join(location))

        count = data["count"]

        title = f" [{data.get('title')}]" if "title" in data else ""

        embed = (
            hikari.Embed(
                title=f"{state}{title} {data['username']}",
                url=data["url"],
                description="\n\n".join(description),
            )
            .set_thumbnail("https://imgur.com/r3eEAy3.png")
            .add_field(
                name=f"{utils.lichess.EMOJI['other']['challenge']} Games "
                + f"[{count['all']}]",
                value=f"{count['win']} wins | {count['loss']} losses | {count['draw']} "
                + f"draws\n*{data.get('completionRate', 100)}% completion*",
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
