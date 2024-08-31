import discord
from discord import app_commands
from discord.ext import commands

class DefaultCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ping")
    async def ping(self, interaction: discord.Interaction) -> None:
        """봇의 응답속도를 알려줍니다."""
        
        latency = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"Pong! `{latency}ms`")

    @app_commands.command(name="help")
    async def help(self, interaction: discord.Interaction) -> None:
        """봇의 정보를 알려줍니다."""
        
        embed = discord.Embed(
            color=0xFDFD96,
            description="""
- 니트로 없이 GIF 이모지 사용, 더블 이모지 확대 등 디스코드에서 이모지 사용 경혐을 향상시켜주는 봇입니다.
- 명령어 목록을 보려면 `/list` 명령어나 하단 버튼을 클릭해주세요.
- 별도의 서포트 디스코드는 운영하고 있지 않습니다. 피드백이나 이슈는 [깃허브 이슈](https://github.com/karpitony/discord-emoji-bot/issues)에 남겨주세요 :)\n\n      
[초대하기](https://discord.com/oauth2/authorize?client_id=1275860131711815690&permissions=826781527040&integration_type=0&scope=bot) | [소스코드 구경하기](https://github.com/karpitony/discord-emoji-bot)
            """   
        )
        embed.set_author(
            name=f"{self.bot.user.name} 소개",
            icon_url=f"{self.bot.user.avatar}"
        )
        
        # 명령어 보기 버튼 생성
        view = discord.ui.View()

        button = discord.ui.Button(
            label="명령어 목록 보기",
            style=discord.ButtonStyle.primary,
            custom_id="show_command_list",
        )
        button.callback = self.button_callback
        view.add_item(button)

        await interaction.response.send_message(embed=embed, view=view)

    async def button_callback(self, interaction: discord.Interaction):
        if interaction.data['custom_id'] == "show_command_list":
            await self.show_command_list(interaction)
    
    async def show_command_list(self, interaction: discord.Interaction) -> None:
        """봇의 명령어 목록을 보여주는 내부 메서드."""
        
        embed = discord.Embed(
            color=0xFDFD96,
            title=f"{self.bot.user.name} 명령어 목록"
        )
        embed.add_field(name="/ping", value="봇의 응답속도를 알려줍니다.", inline=False)
        embed.add_field(name="/help", value="봇의 정보를 알려줍니다.", inline=False)
        embed.add_field(name="/list", value="봇의 명령어 목록을 보여줍니다.", inline=False)
        embed.add_field(name="/selectgif", value="""GIF이모지를 버튼에 담아 보여줍니다.
                                                    버튼을 눌러 이모지를 보내세요.""", inline=False)
        embed.add_field(name="/double", value="이모지 두개를 합쳐서 임베드에 담아 크게 보여줍니다.", inline=False)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="list")
    async def list(self, interaction: discord.Interaction) -> None:
        """봇의 명령어 목록을 보여줍니다."""
        await self.show_command_list(interaction)

    
async def setup(bot: commands.Bot):
    await bot.add_cog(DefaultCommand(bot))
