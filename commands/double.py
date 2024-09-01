import discord
from discord import app_commands
from discord.ext import commands
from PIL import Image, UnidentifiedImageError
import io
from aiohttp import ClientSession

class Double(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="double")
    @app_commands.describe(emoji_input="이모지 입력창")
    async def select_gif(self, interaction: discord.Interaction, emoji_input:str):
        """두 이모지를 합쳐서 임베드로 전송합니다."""
        
        # 이모지 분리
        emojis = emoji_input.split()

        if len(emojis) != 2:
            await interaction.response.send_message("올바른 형식으로 두 개의 이모지를 입력해주세요. 예시: `:emoji1::emoji2:`", ephemeral=True)
            return

        l_emoji = emojis[0]
        r_emoji = emojis[1]
        same_emoji:bool = True if l_emoji == r_emoji else False
        
        # 이모지에서 이름과 ID 추출
        try:
            l_emoji_name = l_emoji.split(":")[1]
            l_emoji_id = l_emoji.split(":")[2][:-1]
            r_emoji_name = r_emoji.split(":")[1]
            r_emoji_id = r_emoji.split(":")[2][:-1]
        except IndexError:
            await interaction.response.send_message("이모지 형식이 올바르지 않습니다. `<:emoji_name:emoji_id>` 형식으로 입력해주세요.", ephemeral=True)
            return

        # 서버에서 이모지 찾기
        l_emoji_name = l_emoji.split(":")[1]
        r_emoji_name = r_emoji.split(":")[1]
        
        left_emoji = None
        right_emoji = None
        
        # 중복인 경우 하나만 탐색하게끔
        for emoji in interaction.guild.emojis:
            if emoji.name == l_emoji_name:
                left_emoji = emoji
                if same_emoji:
                    right_emoji = emoji
                    break
            elif emoji.name == r_emoji_name:
                right_emoji = emoji
                if same_emoji:
                    left_emoji = emoji
                    break


        if not left_emoji or not right_emoji:
            await interaction.response.send_message("해당 이름의 이모지를 찾을 수 없습니다.", ephemeral=True)
            return
        
        async def download_emoji(emoji):
            # 이모지 URL 탐색 (webp/gif/png)
            extensions = ['gif', 'png', 'webp']
            image = None
            async with ClientSession() as session:
                for ext in extensions:
                    image_url = f"https://cdn.discordapp.com/emojis/{emoji.id}.{ext}"
                    async with session.get(image_url) as resp:
                        if resp.status == 200:
                            image = await resp.read()
                            try:
                                img = Image.open(io.BytesIO(image))
                                img.verify()  # 이미지가 유효한지 확인
                                return image, ext
                            except UnidentifiedImageError:
                                continue
            return None, None

        try:
            # 이모지 이미지를 다운로드
            if same_emoji:
                left_emoji_image, left_ext = await download_emoji(left_emoji)
                right_emoji_image, right_ext = left_emoji_image, left_ext
            else:
                left_emoji_image, left_ext = await download_emoji(left_emoji)
                right_emoji_image, right_ext = await download_emoji(right_emoji)
            
            if not left_emoji_image or not right_emoji_image:
                await interaction.response.send_message("이모지 이미지를 다운로드하는 데 실패했습니다.", ephemeral=True)
                return
        
        except Exception as e:
            await interaction.response.send_message("이모지 이미지를 다운로드하는 도중 오류가 발생했습니다.", ephemeral=True)
            return

        try:
            # 이미지를 열고 합치기
            with Image.open(io.BytesIO(left_emoji_image)).convert("RGBA") as img1, \
                 Image.open(io.BytesIO(right_emoji_image)).convert("RGBA") as img2:
                
                # 이미지 크기 조정 (정사각형, 예: 128x128)
                size = (128, 128)
                img1 = img1.resize(size, Image.Resampling.LANCZOS)
                img2 = img2.resize(size, Image.Resampling.LANCZOS)
                
                # 가로로 합친 새 이미지 생성
                total_width = img1.width + img2.width
                max_height = max(img1.height, img2.height)
                new_img = Image.new('RGBA', (total_width, max_height))
                new_img.paste(img1, (0, 0))
                new_img.paste(img2, (img1.width, 0))
                
                # 이미지를 바이트로 변환
                image_binary = io.BytesIO()
                new_img.save(image_binary, 'PNG')
                image_binary.seek(0)
        
        except Exception as e:
            await interaction.response.send_message(f"이모지 이미지를 처리하는 데 실패했습니다: {str(e)}", ephemeral=True)
            return

        # 사용자 프로필 사진이 없으면 기본 아바타 사용
        avatar_url = interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url
        
        # 임베드 생성
        embed = discord.Embed(
            color=interaction.user.top_role.color,
            description=f""
        )
        embed.set_author(
            name=interaction.user.display_name,
            icon_url=avatar_url
        )
        embed.set_image(url="attachment://double_emoji.png")

        # 파일 생성
        file = discord.File(fp=image_binary, filename="double_emoji.png")

        await interaction.response.send_message(embed=embed, file=file)

async def setup(bot: commands.Bot):
    await bot.add_cog(Double(bot))