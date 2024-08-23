import os
from typing import Any

import aiohttp
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

GUILD = discord.Object(id=os.getenv("TEST_GUILD_ID"))


class GifEmojiBot(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=discord.Intents.default(),
            allowed_mentions=discord.AllowedMentions.none(),
        )

        self.session: aiohttp.ClientSession = None

    async def setup_hook(self):
        await self.load_extension("commands.gif")

        self.tree.copy_global_to(guild=GUILD)
        await self.tree.sync()  # guild=GUILD

    async def on_error(self, event_method: str, /, *args: Any, **kwargs: Any) -> None:
        print(event_method, args, kwargs)
        return await super().on_error(event_method, *args, **kwargs)

    async def on_command_error(self, context, exception) -> None:
        print(context, exception)
        return await super().on_command_error(context, exception)
    
if __name__=="__main__":


    bot = GifEmojiBot()

    bot.run(os.getenv("BOT_TOKEN"))