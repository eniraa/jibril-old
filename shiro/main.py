import os

from dotenv import load_dotenv
import hikari
import lightbulb

load_dotenv()

try:
    import uvloop

    uvloop.install()
finally:
    bot = lightbulb.Bot(token=os.environ.get("DISCORD_TOKEN"), slash_commands_only=True)

    bot.run(
        status=hikari.Status.IDLE,
        activity=hikari.Activity(
            name="Night Opera lose", type=hikari.ActivityType.WATCHING
        ),
    )
