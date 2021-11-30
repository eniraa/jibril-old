import importlib
import os
from typing import Sequence

from dotenv import load_dotenv
import hikari
import lightbulb

import utils.defaults
import utils.upload


def main(
    token: str,
    *,
    modules: Sequence[str] = (),
    guilds: Sequence[int] = (),
    status: hikari.Status = hikari.Status.IDLE,
    activity: hikari.Activity = utils.defaults.NIGHT_OPERA,
) -> None:
    """Starts the bot.

    Args:
        token (str): The token to use to start the bot.
        modules (Sequence[str], optional): The modules to load when starting the bot.
            Defaults to ().
        guilds (Sequence[int], optional): The list of guild IDs to enable guild commands
            in. Note that this makes testing significantly easier, as guild commands are
            instantly updated. Defaults to ().
        status (hikari.Status, optional): The status to start the bot with. Defaults to
            hikari.Status.IDLE.
        activity (hikari.Activity, optional): The activity to start the bot with.
            Defaults to utils.defaults.NIGHT_OPERA.
    """
    shiro = lightbulb.BotApp(token=token, default_enabled_guilds=guilds)

    for module in modules:
        importlib.import_module(module).load(shiro)

    shiro.run(
        status=status,
        activity=activity,
    )


if __name__ == "__main__":
    try:
        import uvloop

        uvloop.install()
    finally:
        load_dotenv()

        kwargs = {
            "token": os.environ.get("DISCORD_TOKEN"),
            "modules": utils.defaults.MODULES,
        }

        if "HOME_GUILDS" in os.environ:
            kwargs["guilds"] = map(int, os.environ["HOME_GUILDS"].split(","))

        main(**kwargs)
