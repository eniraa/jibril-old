from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

import aiohttp
import bs4
import numpy
import orjson
import pandas

from utils.defaults import CONSTANTS
import utils.flags


class LichessMode(Enum):
    """All rated chess modes."""

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
    history: pandas.DataFrame


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
            try:
                points = numpy.array(rating_history[i]["points"])
                points[:, 1] += 1
                dates = pandas.to_datetime(
                    pandas.DataFrame(points[:, :3], columns=["year", "month", "day"])
                )
                ratings = pandas.Series(points[:, 3], index=dates)
            except IndexError:
                continue

            # mode_history = pandas.DataFrame(columns=["rating", "date"])

            final_ratings = ratings.copy()

            for j, item in enumerate(ratings.items()):
                date, _ = item
                if j > 0:
                    last_date = ratings.index.values[j - 1]

                    if last_date != date - timedelta(days=1):
                        final_ratings.loc[date - timedelta(days=1)] = ratings[last_date]

            history.append(
                LichessHistoryData(
                    LichessMode(mode["name"]),
                    final_ratings.sort_index(),
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
