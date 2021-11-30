import ast
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import io
import os

import aiohttp
import bs4
import hikari
from hikari.embeds import EmbedField
import hikari.files
import humanize
import matplotlib
import matplotlib.pyplot as plt
import orjson

from utils.defaults import CONSTANTS, MPL_COLOR
import utils.flags
from utils.markdown import escape


class LichessMode(Enum):
    """This class is used for organizing a user's ratings by mode"""

    ultraBullet = "UltraBullet"
    bullet = "Bullet"
    blitz = "Blitz"
    rapid = "Rapid"
    classical = "Classical"
    correspondence = "Correspondence"
    crazyhouse = "Crazyhouse"
    chess960 = "Chess960"
    kingOfTheHill = "King of the Hill"
    threeCheck = "Three-check"
    antichess = "Antichess"
    atomic = "Atomic"
    horde = "Horde"
    racingKings = "Racing Kings"
    puzzle = "Puzzles"
    storm = "Puzzle Storm"
    racer = "Puzzle Racer"
    streak = "Puzzle Streak"


@dataclass(frozen=True, slots=True)
class LichessHistoryPoint:
    """A date and its associated rating."""

    rating: int
    date: datetime


@dataclass(frozen=True, slots=True)
class LichessHistoryData:
    """All historical ratings for a given mode."""

    mode: LichessMode
    history: list[LichessHistoryPoint]


@dataclass(frozen=True, slots=True)
class LichessPerfData:
    """Performance data for a given mode."""

    mode: LichessMode
    games: int
    rating: int
    deviation: int | None = None
    progression: int | None = None


@dataclass(frozen=True, slots=True)
class LichessUser:
    """A wrapper for a Lichess user."""

    username: str
    disabled: bool = False
    online: bool = False
    violation: bool | None = None
    title: str | None = None
    patron: bool | None = None
    country: str | None = None
    location: str | None = None
    bio: str | None = None
    links: str | None = None
    name: str | None = None
    fide: int | None = None
    uscf: int | None = None
    ecf: int | None = None
    win: int | None = None
    loss: int | None = None
    draw: int | None = None
    completion: int | None = None
    playtime: timedelta | None = None
    tvtime: timedelta | None = None
    trophies: list[str] | None = None
    performances: list[LichessPerfData] | None = None
    history: list[LichessHistoryData] | None = None

    @property
    def id_(self) -> str:
        """The user's ID"""
        return self.username.lower()

    @property
    def url(self) -> str:
        """The user's URL"""
        return f"https://lichess.org/@/{self.id_}"

    @property
    def total_games(self) -> int | None:
        """Sums the wins, losses, and draws for the user.

        Returns:
            int | None: The total number of games, if any.
        """
        try:
            return self.win + self.loss + self.draw
        except TypeError:
            return None

    @property
    def flag(self) -> str:
        """Provides a flag emoji for the user's country.

        Returns:
            str: The emoji of the flag.
        """
        if self.country in CONSTANTS["lichess"]["emoji"]["flags"]:
            return CONSTANTS["lichess"]["emoji"]["flags"][self.country]
        elif len(self.country) == 2:
            return utils.flags._regional_indicator(self.country)
        else:
            return utils.flags._tag(self.country)

    @classmethod
    async def load(cls, username: str) -> "LichessUser":
        """Load a user's profile from Lichess into the wrapper class.

        Args:
            username (str): The username of the user to load.

        Returns:
            LichessUser: The user that has been loaded.
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://lichess.org/api/user/{username}"
            ) as response:
                public_data = orjson.loads(await response.text())

            # don't need to run anything after this if the account is disabled
            if public_data.get("disabled"):
                return cls(
                    username=public_data["username"],
                    disabled=True,
                )

            async with session.get(
                f"https://lichess.org/api/user/{username}/rating-history"
            ) as response:
                rating_history = orjson.loads(await response.text())

            async with session.get(public_data["url"]) as response:
                # finds trophies through web scraping
                trophies = []
                for trophy in bs4.BeautifulSoup(
                    await response.text(), "html.parser"
                ).find_all(class_="trophy"):
                    for emoji in CONSTANTS["lichess"]["emoji"]["trophy"]:
                        if emoji in trophy["class"]:
                            trophies.append(
                                CONSTANTS["lichess"]["emoji"]["trophy"][emoji]
                            )
                            break

        history = []
        for i, mode in enumerate(rating_history):
            mode_history = []
            for day in rating_history[i]["points"]:
                date = datetime(year=day[0], month=day[1] + 1, day=day[2])
                day_before = date - timedelta(days=1)

                if mode_history and day_before != mode_history[-1].date:
                    mode_history.append(
                        LichessHistoryPoint(
                            mode_history[-1].rating,
                            day_before,
                        )
                    )

                mode_history.append(LichessHistoryPoint(day[-1], date))

            history.append(
                LichessHistoryData(
                    LichessMode(mode["name"]),
                    mode_history,
                )
            )

        perfs = []

        for mode in LichessMode:
            if mode.name not in public_data.get("perfs", []):
                continue

            performance = public_data["perfs"][mode.name]

            if "rating" in performance:
                perfs.append(
                    LichessPerfData(
                        mode,
                        deviation=performance["rd"],
                        progression=performance["prog"],
                        **{
                            k: performance[k]
                            for k in performance.keys()
                            & LichessPerfData.__annotations__.keys()
                        },
                    )
                )
            else:
                perfs.append(
                    LichessPerfData(
                        mode, rating=performance["score"], games=performance["runs"]
                    )
                )

        profile = public_data.get("profile", {})

        # concatenates first & last name if they exist, otherwise set to None
        if name_list := filter(
            bool, [profile.get("firstName"), profile.get("lastName")]
        ):
            name = " ".join(name_list)
        else:
            name = None

        # gets playtimes if they exist, otherwise set to None
        if public_data.get("playTime"):
            playtime = timedelta(seconds=public_data["playTime"].get("total", 0))
            tvtime = timedelta(seconds=public_data["playTime"].get("tv", 0))
        else:
            playtime = None
            tvtime = None

        etc = public_data | profile | public_data.get("count", {})

        return cls(
            history=history,
            performances=perfs,
            trophies=trophies,
            completion=public_data.get("completionRate"),
            fide=profile.get("fideRating"),
            uscf=profile.get("uscfRating"),
            ecf=profile.get("ecfRating"),
            name=name,
            playtime=playtime,
            tvtime=tvtime,
            **{k: etc[k] for k in LichessUser.__annotations__.keys() & etc.keys()},
        )


class LichessUserFormatter:
    """A class that helps format user data to an embed."""

    @staticmethod
    def _state(user: LichessUser) -> str:
        if user.disabled:
            return CONSTANTS["lichess"]["emoji"]["other"]["closed"]
        if user.patron:
            if user.online:
                return CONSTANTS["lichess"]["emoji"]["status"]["patron"]["online"]
            return CONSTANTS["lichess"]["emoji"]["status"]["patron"]["offline"]
        elif user.online:
            return CONSTANTS["lichess"]["emoji"]["status"]["normie"]["online"]
        return CONSTANTS["lichess"]["emoji"]["status"]["normie"]["offline"]

    @staticmethod
    def _name(user: LichessUser) -> str:
        names = [LichessUserFormatter._state(user)]
        if user.title:
            names.append(f"[{user.title}]")
        names.append(user.username)
        if user.name:
            names.append(f"({user.name})")

        return " ".join(names)

    @staticmethod
    def _location(user: LichessUser) -> str:
        locations = []
        if user.country:
            locations.append(user.flag)
        if user.location:
            locations.append(escape(user.location))
        return " ".join(locations)

    @staticmethod
    def _trophies(user: LichessUser) -> str:
        trophies = user.trophies or []

        if user.violation:
            trophies.append(CONSTANTS["lichess"]["emoji"]["other"]["violation"])

        return " ".join(trophies)

    @staticmethod
    def _playtime(user: LichessUser) -> str:
        playtimes = []

        if user.playtime:
            display_time = humanize.precisedelta(
                user.playtime,
                suppress=["months", "years"],
                minimum_unit="minutes",
                format="%0.0f",
            )
        else:
            display_time = "0 minutes"

        playtimes.append(
            f"{CONSTANTS['lichess']['emoji']['other']['stats']} {display_time} played"
        )

        if user.tvtime:
            display_time = humanize.precisedelta(
                user.tvtime,
                suppress=["months", "years"],
                minimum_unit="minutes",
                format="%0.0f",
            )
        else:
            display_time = "0 minutes"

        playtimes.append(
            f"{CONSTANTS['lichess']['emoji']['other']['tv']} {display_time} on TV"
        )

        if not playtimes:
            return None

        return "\n".join(playtimes)

    @staticmethod
    def _description(user: LichessUser) -> str:
        return (
            "\n\n".join(
                filter(
                    bool,
                    [
                        LichessUserFormatter._trophies(user),
                        "*This account is closed*"
                        if user.disabled
                        else escape(user.bio),
                        LichessUserFormatter._location(user),
                    ],
                )
            )
            or "*This user has no description.*"
        )

    @staticmethod
    def _base_embed(user: LichessUser) -> hikari.Embed:
        return hikari.Embed(
            title=LichessUserFormatter._name(user),
            url=user.url,
            description=LichessUserFormatter._description(user),
        ).set_thumbnail(CONSTANTS["lichess"]["assets"]["logo"])

    @staticmethod
    def _games_field(user: LichessUser) -> EmbedField:
        if not user.total_games:
            return None
        return EmbedField(
            name=f"{CONSTANTS['lichess']['emoji']['other']['challenge']} Games "
            + f"[{user.total_games}]",
            value=f"{user.win} wins | {user.loss} losses | {user.draw} "
            + f"draws\n*{user.completion or 100}% completion*"
            + f"\n\n{LichessUserFormatter._playtime(user)}",
            inline=False,
        )

    @staticmethod
    def _otb_field(user: LichessUser) -> EmbedField:
        otb_ratings = {}
        if user.fide:
            otb_ratings["FIDE"] = user.fide
        if user.uscf:
            otb_ratings["USCF"] = user.uscf
        if user.ecf:
            otb_ratings["ECF"] = user.ecf

        if not otb_ratings:
            return None

        return EmbedField(
            name=f"{CONSTANTS['lichess']['emoji']['other']['stats']} OTB",
            value="\n".join([f"{v} {k}" for k, v in otb_ratings.items()]),
            inline=False,
        )

    @staticmethod
    def _links_field(user: LichessUser) -> EmbedField:
        if not user.links:
            return None

        links = []

        for link in user.links.splitlines():
            if link and not (link.startswith("https://") or link.startswith("http://")):
                links.append(f"https://{link}")
            else:
                links.append(link)

        return EmbedField(
            name=f"{CONSTANTS['lichess']['emoji']['other']['link']} Links",
            value=escape("\n".join(links)),
            inline=False,
        )

    @staticmethod
    def _mode_field(user: LichessUser, mode: LichessMode) -> EmbedField:
        performance = None

        for perf in user.performances:
            if perf.mode.value == mode.value:
                performance = perf
                break

        if not performance:
            return None

        if performance.progression:
            emoji = CONSTANTS["lichess"]["emoji"]["other"][
                ["down", "up"][performance.progression > 0]
            ]
            display_progression = f"{emoji} {performance.progression}"
        else:
            display_progression = ""

        return EmbedField(
            name=f"{CONSTANTS['lichess']['emoji']['modes'].get(mode.name, '♟️')} "
            + f"{mode.value} [{performance.games}]",
            value=f"{CONSTANTS['lichess']['emoji']['other']['rating']} "
            + f"{performance.rating}"
            + f" ± {performance.deviation}\n{display_progression}"
            * bool(performance.deviation),
            inline=True,
        )

    @staticmethod
    def _graph(user: LichessUser) -> io.BytesIO:
        if not user.total_games:
            return

        fig = plt.figure()
        ax = fig.add_axes([0.1, 0.1, 0.7, 0.7])

        ax.set_xlabel("Date")
        ax.set_ylabel("Glicko-2")
        ax.set_title(f"{user.username}'s Rating History")

        for mode in LichessMode:
            histories = [*filter(lambda x: x.mode.value == mode.value, user.history)]
            if histories:
                history_data = histories[0]
                if history_data.history:
                    ax.plot(
                        [point.date for point in history_data.history],
                        [point.rating for point in history_data.history],
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

    @staticmethod
    def bio_embed(user: LichessUser) -> hikari.Embed:
        """Creates an embed with a user's biographical information.

        Args:
            user (LichessUser): The user to generate the embed for.

        Returns:
            hikari.Embed: The embed to use.
        """
        embed = LichessUserFormatter._base_embed(user)

        embed._fields = filter(
            bool,
            [
                LichessUserFormatter._games_field(user),
                LichessUserFormatter._links_field(user),
            ],
        )

        return embed

    @staticmethod
    def rating_embed(user: LichessUser) -> hikari.Embed:
        """Creates an embed with a user's ratings per mode.

        Args:
            user (LichessUser): The user to generate the embed for.

        Returns:
            hikari.Embed: The embed to use.
        """
        embed = LichessUserFormatter._base_embed(user)
        embed.description = None

        embed._fields = filter(
            bool,
            [LichessUserFormatter._otb_field(user)]
            + [LichessUserFormatter._mode_field(user, mode) for mode in LichessMode],
        )

        return embed

    @staticmethod
    async def graph_embed(user: LichessUser) -> hikari.Embed:
        """Creates an embed with a graph of the user's rating history.

        Args:
            user (LichessUser): The user to generate the embed for.

        Returns:
            hikari.Embed: The embed to use.
        """
        embed = LichessUserFormatter._base_embed(user)
        embed.description = None

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.imgbb.com/1/upload",
                data={
                    "key": os.environ["IMGBB_KEY"],
                    "image": LichessUserFormatter._graph(user).read(),
                },
            ) as response:
                imgbb = await response.json()

        embed.set_image(imgbb["data"]["url"])

        return embed
