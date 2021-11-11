import os

from dotenv import load_dotenv
import hikari
import lightbulb

load_dotenv()

if os.name != "nt":
    import uvloop

    uvloop.install()

bot = lightbulb.Bot(token=os.environ.get("DISCORD_TOKEN"), slash_commands_only=True)

bot.run(
    activity=hikari.Activity(name="Night Opera lose", type=hikari.ActivityType.WATCHING)
)
