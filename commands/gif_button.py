import discord
from discord import app_commands
from discord.ext import commands

class GifButtonView(discord.ui.View):
    def __init__(self, emojis):
        super().__init__(timeout=None)
        self.emojis = emojis

        # 이모지 버튼 만들기
        for emoji in self.emojis:
            button = discord.ui.Button(
                label="",
                style=discord.ButtonStyle.primary,
                custom_id=f"send_gif_{emoji.id}",
                emoji=emoji
            )
            button.callback = self.button_callback
            self.add_item(button)
    
    async def button_callback(self, interaction: discord.Interaction):
        emoji_id = int(interaction.data['custom_id'].split('_')[-1])
        emoji = discord.utils.get(interaction.guild.emojis, id=emoji_id)
        
        if emoji:
            embed = discord.Embed(
            title="",
            color=0x6DB69E,
        )

        if emoji:
            # 임베드 생성
            embed = discord.Embed(
                color=interaction.user.top_role.color,
            )
            embed.set_author(
                name=interaction.user.display_name,
                icon_url=interaction.user.avatar.url
            )
            embed.set_image(url=emoji.url)

            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("해당 이모지를 찾을 수 없습니다.", ephemeral=True)
        
        try:
            await interaction.message.delete()
        except discord.NotFound:
            pass

class GifSelector(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="selectgif")
    async def select_gif(self, interaction: discord.Interaction):
        """서버 내의 GIF 이모지들을 버튼으로 선택할 수 있는 인터페이스를 제공합니다."""

        gif_emojis = [emoji for emoji in interaction.guild.emojis if emoji.animated]
        
        if not gif_emojis:
            await interaction.response.send_message("서버에 GIF 이모지가 없습니다.", ephemeral=True)
            return
        
        view = GifButtonView(gif_emojis)
        await interaction.response.send_message("원하는 GIF 이모지를 선택하세요:", view=view, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(GifSelector(bot))
