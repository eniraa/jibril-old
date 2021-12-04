import os

import hikari
import lightbulb


async def upload(bot: lightbulb.BotApp, file: hikari.Resourceish) -> str:
    """Uploads a file to Discord.

    This is useful for uploading images that are disallowed as attachments (e.g. in an
    embed in the first interaction response).

    Args:
        bot (lightbulb.BotApp): The bot to upload the file with
        file (hikari.Resourceish): The file to upload

    Returns:
        str: The URL of the uploaded file
    """
    chan: hikari.TextableChannel = await bot.rest.fetch_channel(
        int(os.environ["UPLOAD_CHANNEL"])
    )
    msg = await chan.send(attachment=file)
    return msg.attachments[0].url
