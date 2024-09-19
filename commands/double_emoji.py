# 메세지에서 이모지 두개가 있는지 확인하고, 두개 이상이면 합쳐서 임베드로 전송합니다.
# 기존 double.py 파일을 사용하던 방식에서, on_message 이벤트를 사용하여 메세지를 처리합니다.

import discord
from discord.ext import commands
import re
import io
from PIL import Image, UnidentifiedImageError
import logging

class DoubleEmoji(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # 메시지 전체가 두 개의 커스텀 이모지로만 구성되어 있는지 확인하는 정규식
        self.EMOJI_REGEX = re.compile(
            r'^\s*<(?P<animated1>a?):(?P<name1>[a-zA-Z0-9_]+):(?P<id1>[0-9]{15,21})>\s*<(?P<animated2>a?):(?P<name2>[a-zA-Z0-9_]+):(?P<id2>[0-9]{15,21})>\s*$'
        )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # 봇 자신 또는 다른 봇의 메시지는 무시
        if not message.guild or message.author.bot:
            return

        match = self.EMOJI_REGEX.match(message.content)
        if not match:
            # print("No match found.")
            return  # 메시지가 정확히 두 개의 이모지로만 구성되지 않은 경우 무시

        # print("Match found!")

        try:
            # 첫 번째 이모지 정보 추출
            is_animated1 = bool(match.group('animated1'))
            emoji_id1 = match.group('id1')
            extension1 = ".gif" if is_animated1 else ".png"

            # 두 번째 이모지 정보 추출
            is_animated2 = bool(match.group('animated2'))
            emoji_id2 = match.group('id2')
            extension2 = ".gif" if is_animated2 else ".png"

            # 이모지 이미지 다운로드
            image_data1, ext1 = await self.download_emoji(emoji_id1, extension1)
            image_data2, ext2 = await self.download_emoji(emoji_id2, extension2)

            if not image_data1 or not image_data2:
                await message.channel.send(
                    "이모지 이미지를 다운로드하는 데 실패했습니다.",
                    reference=message.reference,
                    mention_author=False
                )
                return

            # 이미지 합치기
            combined_image = self.combine_images(image_data1, image_data2)

            if combined_image is None:
                await message.channel.send(
                    "이모지 이미지를 처리하는 데 실패했습니다.",
                    reference=message.reference,
                    mention_author=False
                )
                return

            # 임베드 생성
            embed = discord.Embed(
                color=message.author.color if message.author.color != discord.Colour.default() else discord.Colour.greyple()
            )
            embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url if message.author.display_avatar else None)
            embed.set_image(url="attachment://combined.png")

            # 파일 생성
            file = discord.File(fp=combined_image, filename="combined.png")

            # 메시지 삭제 및 임베드 전송
            await message.delete()
            await message.channel.send(embed=embed, file=file, reference=message.reference, mention_author=False)

        except UnidentifiedImageError:
            await message.channel.send(
                "이모지 이미지를 처리하는 데 실패했습니다. 유효한 이미지가 아닙니다.",
                reference=message.reference,
                mention_author=False
            )
            logging.exception("Invalid image format.")
        except Exception as e:
            await message.channel.send(
                "이모지 이미지를 처리하는 도중 오류가 발생했습니다.",
                reference=message.reference,
                mention_author=False
            )
            logging.exception("Error processing emojis:", exc_info=e)

    async def download_emoji(self, emoji_id: str, extension: str) -> tuple:
        """
        이모지 이미지를 다운로드합니다.
        """
        url = f"https://cdn.discordapp.com/emojis/{emoji_id}{extension}"
        try:
            # self.bot.session이 제대로 설정되었는지 확인
            if self.bot.session is None:
                logging.error(f"Bot session is None. Cannot download emoji {emoji_id}.")
                return None, None

            async with self.bot.session.get(url) as resp:
                if resp.status == 200:
                    image = await resp.read()
                    try:
                        img = Image.open(io.BytesIO(image))
                        img.verify()  # 이미지가 유효한지 확인
                        return image, extension
                    except UnidentifiedImageError:
                        logging.error(f"UnidentifiedImageError for emoji {emoji_id} with extension {extension}.")
                        return None, None
                else:
                    logging.error(f"Failed to download emoji {emoji_id}. Status code: {resp.status}")
        except Exception as e:
            logging.exception(f"Exception while downloading emoji {emoji_id}: {e}")
        return None, None

    def combine_images(self, image_data1: bytes, image_data2: bytes) -> io.BytesIO:
        """
        두 개의 이미지를 가로로 합칩니다.
        """
        try:
            with Image.open(io.BytesIO(image_data1)).convert("RGBA") as img1, \
                 Image.open(io.BytesIO(image_data2)).convert("RGBA") as img2:

                # 이미지 크기 조정 (예: 128x128)
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
                return image_binary
        except UnidentifiedImageError as e:
            logging.exception("UnidentifiedImageError while combining images:", exc_info=e)
            return None
        except Exception as e:
            logging.exception("Exception while combining images:", exc_info=e)
            return None

async def setup(bot: commands.Bot):
    await bot.add_cog(DoubleEmoji(bot))