import discord
from discord import app_commands
from discord.ext import commands

class Gif(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # 자동완성 함수 정의
    async def gif_autocomplete(self, interaction: discord.Interaction, current: str):
        # 입력한 텍스트에서 ':' 제거
        current = current.replace(":", "")

        # 사용자가 입력한 텍스트(current)에 맞게 필터링된 이모지 이름 목록 반환 (GIF 이모지만)
        return [
            app_commands.Choice(name=f":{emoji.name}:", value=f":{emoji.name}:")
            for emoji in interaction.guild.emojis
            if emoji.animated and current.lower() in emoji.name.lower()
        ]

    @app_commands.command(name="sendgif")
    @app_commands.rename(emoji_name="gif")
    @app_commands.describe(
        emoji_name="GIF 이모지를 입력하세요.",
    )
    @app_commands.autocomplete(emoji_name=gif_autocomplete)  # 자동완성 기능 추가
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
