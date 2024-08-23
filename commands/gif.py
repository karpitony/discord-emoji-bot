import discord
from discord import app_commands
from discord.ext import commands

class Gif(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="sendgif")
    @app_commands.rename(emoji_name="gif")
    @app_commands.describe(
        emoji_name="GIF 이모지를 입력하세요.",
    )
    async def send_gif(self, interaction: discord.Interaction, emoji_name: str):
        """
        GIF 이모지를 대신 전송합니다.
        """
        emoji_name = emoji_name.split(":")[1]
        
        # 서버의 모든 이모지를 탐색
        for emoji in interaction.guild.emojis:
            if emoji.name == emoji_name and emoji.animated:
                await interaction.response.send_message(str(emoji))
                return

        # 일치하는 이모지가 없을 경우
        await interaction.response.send_message(f'해당 이모지 이름과 일치하는 Gif 이모지가 없습니다. :{emoji_name}:')

async def setup(bot: commands.Bot):
    await bot.add_cog(Gif(bot))
