import os

from dotenv import load_dotenv
import hikari
import lightbulb

load_dotenv()

try:
    import uvloop

    uvloop.install()
finally:
    modules = ["chess"]

    shiro = lightbulb.BotApp(token=os.environ.get("DISCORD_TOKEN"))

    for module in modules:
        __import__(module).load(shiro)

    shiro.run(
        status=hikari.Status.IDLE,
        activity=hikari.Activity(
            name="Night Opera lose", type=hikari.ActivityType.WATCHING
        ),
    )
