import ast
import copy
from enum import Enum
import io

import hikari
from hikari.embeds import EmbedField
import hikari.files
import humanize
import lightbulb
import matplotlib
import matplotlib.pyplot as plt
import validators

from utils.defaults import CONSTANTS, MPL_COLOR
import utils.flags
import utils.markdown
from utils.models.lichess import LichessMode, LichessUser
from utils.upload import upload


class LichessUserEmbed(Enum):
    """All types of embeds for a user."""

    bio = "bio"
    rating = "rating"
    history = "history"


class LichessUserFormatter:
    """A class that helps format user data to an embed."""

    __slots__ = ("bot", "user", "embeds")

    def __init__(self, user: LichessUser, bot: lightbulb.BotApp) -> None:
        self.user = user
        self.bot = bot
        self.embeds = {}

    def title(self) -> str:
        """Creates the title for the user embed.

        Returns:
            str: The title to use for the user embed.
        """
        sections = []

        # status
        if self.user.disabled:
            state = CONSTANTS["lichess"]["emoji"]["other"]["closed"]
        elif self.user.patron:
            if self.user.online:
                state = CONSTANTS["lichess"]["emoji"]["status"]["patron"]["online"]
            else:
                state = CONSTANTS["lichess"]["emoji"]["status"]["patron"]["offline"]
        elif self.user.online:
            state = CONSTANTS["lichess"]["emoji"]["status"]["normie"]["online"]
        else:
            state = CONSTANTS["lichess"]["emoji"]["status"]["normie"]["offline"]

        sections.append(state)

        # title
        if self.user.title:
            sections.append(f"[{self.user.title}]")

        # username
        sections.append(self.user.username)

        # name
        if self.user.name:
            sections.append(f"({self.user.name})")

        return " ".join(sections)

    def description(self) -> str:
        """Creates the description for the user embed.

        Returns:
            str: The description to use for the user embed.
        """
        sections = []

        # trophies
        badges = self.user.trophies or []

        if self.user.violation:
            badges.append(CONSTANTS["lichess"]["emoji"]["other"]["violation"])

        sections.append(" ".join(badges))

        # bio
        if self.user.disabled:
            bio = "*This account is closed*"
        else:
            bio = utils.markdown.escape(self.user.bio)

        sections.append(bio)

        # location
        locations = []
        if self.user.country:
            locations.append(self.user.flag)
        if self.user.location:
            locations.append(utils.markdown.escape(self.user.location))

        sections.append(" ".join(locations))

        description = "\n\n".join(filter(None, sections))

        return description or "*This user has no description.*"

    def base(self) -> hikari.Embed:
        """The base embed to use for the user embed.

        Returns:
            hikari.Embed: The base embed.
        """
        return hikari.Embed(
            title=self.title(),
            url=self.user.url,
        ).set_thumbnail(CONSTANTS["lichess"]["assets"]["logo"])

    def graph(self) -> io.BytesIO:
        """Creates a graph of the user's rating history.

        Raises:
            ValueError: The user has no games.

        Returns:
            io.BytesIO: The bytes of the graph PNG.
        """
        if not self.user.total_games:
            raise ValueError("User has no games.")

        fig = plt.figure()
        ax = fig.add_axes([0.1, 0.1, 0.7, 0.7])

        ax.set_xlabel("Date")
        ax.set_ylabel("Glicko-2")
        ax.set_title(f"{self.user.username}'s Rating History")

        for mode in LichessMode:
            histories = [
                *filter(lambda x: x.mode.value == mode.value, self.user.history)
            ]
            if histories:
                history_data = histories[0]
                if not history_data.history.empty:
                    ax.plot(
                        history_data.history.index.values,
                        history_data.history.values,
                        label=history_data.mode.value,
                        color=ast.literal_eval(
                            CONSTANTS["lichess"]["mpl"][mode.name]["color"]
                        ),
                        linestyle=ast.literal_eval(
                            CONSTANTS["lichess"]["mpl"][mode.name]["linestyle"]
                        ),
                        linewidth=0.75,
                    )

        ax.grid(linewidth=0.25, alpha=0.25, color=MPL_COLOR)
        ax.legend(bbox_to_anchor=(1, 1), prop={"size": 6})

        ax.xaxis.set_major_locator(matplotlib.dates.AutoDateLocator(maxticks=8))

        graph = io.BytesIO()

        fig.savefig(graph, dpi=512, transparent=True)

        graph.seek(0, 0)

        return graph

    async def embed(self, form: LichessUserEmbed | None = None) -> hikari.Embed:
        """Creates the embed for the user.

        Args:
            form (LichessUserEmbed, optional): The type of embed to create.

        Returns:
            hikari.Embed: The embed to send.
        """
        if form in self.embeds:
            return copy.deepcopy(self.embeds[form])

        embed = self.base()
        fields = []

        match form:
            case LichessUserEmbed.bio:
                embed.description = self.description()

                # playtime
                playtimes = []

                if self.user.playtime:
                    display_time = humanize.precisedelta(
                        self.user.playtime,
                        suppress=["months", "years"],
                        minimum_unit="minutes",
                        format="%0d",
                    )
                else:
                    display_time = "0 minutes"

                playtimes.append(
                    f"{CONSTANTS['lichess']['emoji']['other']['stats']} {display_time} "
                    + "played"
                )

                if self.user.tvtime:
                    display_time = humanize.precisedelta(
                        self.user.tvtime,
                        suppress=["months", "years"],
                        minimum_unit="minutes",
                        format="%0d",
                    )
                else:
                    display_time = "0 minutes"

                playtimes.append(
                    f"{CONSTANTS['lichess']['emoji']['other']['tv']} {display_time} on "
                    + "TV"
                )

                playtime = "\n".join(playtimes)

                # games
                if self.user.total_games:
                    title = (
                        f"{CONSTANTS['lichess']['emoji']['other']['challenge']} Games "
                        + f"[{self.user.total_games}]"
                    )
                    fields.append(
                        EmbedField(
                            name=title,
                            value=f"{self.user.win} wins | {self.user.loss} losses | "
                            + f"{self.user.draw} "
                            + f"draws\n*{self.user.completion or 100}% completion*"
                            + f"\n\n{playtime}",
                            inline=False,
                        )
                    )

                # links
                if self.user.links:
                    links = []

                    for link in self.user.links.splitlines():
                        if validators.url(link):
                            if link and not (
                                link.startswith("https://")
                                or link.startswith("http://")
                            ):
                                links.append(f"https://{link}")
                            else:
                                links.append(link)

                    fields.append(
                        EmbedField(
                            name=f"{CONSTANTS['lichess']['emoji']['other']['link']} "
                            + "Links",
                            value="\n".join(links),
                            inline=False,
                        )
                    )

                embed._fields = filter(
                    None,
                    fields,
                )

            case LichessUserEmbed.rating:
                # otb
                otb_ratings = {}
                if self.user.fide:
                    otb_ratings["FIDE"] = self.user.fide
                if self.user.uscf:
                    otb_ratings["USCF"] = self.user.uscf
                if self.user.ecf:
                    otb_ratings["ECF"] = self.user.ecf

                if otb_ratings:
                    fields.append(
                        EmbedField(
                            name=f"{CONSTANTS['lichess']['emoji']['other']['stats']} "
                            + "OTB",
                            value="\n".join(
                                [f"{v} {k}" for k, v in otb_ratings.items()]
                            ),
                            inline=False,
                        )
                    )

                # lichess modes
                for mode in LichessMode:
                    try:
                        performance = next(
                            filter(
                                lambda perf: perf.mode.value == mode.value,
                                self.user.performances,
                            )
                        )
                    except StopIteration:
                        continue

                    if performance.progression:
                        emoji = CONSTANTS["lichess"]["emoji"]["other"][
                            ["down", "up"][performance.progression > 0]
                        ]
                        display_progression = f"{emoji} {performance.progression}"
                    else:
                        display_progression = ""

                    display_mode = CONSTANTS["lichess"]["emoji"]["modes"].get(
                        mode.name, "♟️"
                    )

                    fields.append(
                        EmbedField(
                            name=f"{display_mode} {mode.value} [{performance.games}]",
                            value=f"{CONSTANTS['lichess']['emoji']['other']['rating']} "
                            + f"{performance.rating}"
                            + f" ± {performance.deviation}\n{display_progression}"
                            * bool(performance.deviation),
                            inline=True,
                        )
                    )

                embed._fields = filter(
                    None,
                    fields,
                )

            case LichessUserEmbed.history:
                url = await upload(
                    self.bot, hikari.files.Bytes(self.graph(), "graph.png")
                )

                embed.set_image(url)

            case _:
                embed.description = self.description()

        self.embeds[form] = copy.deepcopy(embed)
        return embed
