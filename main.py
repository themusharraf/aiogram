import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from config import API_ENDPOINT_URL, BOT_TOKEN

# Logging konfiguratsiyasi
logging.basicConfig(level=logging.INFO)

# Botni yaratish
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


# Start komandasi uchun ishlovchi funktsiya
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user = message.from_user
    text = f"Salom, {user.full_name}! Men botman va sizga yordam bera olishim mumkin."
    await message.reply(text)


import re


def is_valid_url(url):
    url_pattern = re.compile(
        r'^(https?://)?(www\d?\.)?([a-zA-Z0-9.-]+)\.([a-z]{2,6})([/a-zA-Z0-9.-]*)*?'
    )
    return re.match(url_pattern, url)


# ... yuqoridagi kodlar ...
@dp.message_handler(content_types=types.ContentTypes.ANY)
async def get_media_info(message: types.Message):
    if message.text.startswith("https"):
        try:
            url = message.text

            # Xabarni tekshirib chiqing
            if not is_valid_url(url):
                await message.reply("Xato formatda URL yuborildi.")
                return

            # Video maxfiylikni tekshirib ko'rish
            response = requests.get(API_ENDPOINT_URL, params={"url": url})
            data = response.json()

            if data.get('ok', False) and data.get('private', False):
                await message.reply("Video maxfiy holatda. Iltimos, Instagram Private Downloader ni ishlating.")
            else:
                response = requests.post(API_ENDPOINT_URL, json={"video_url": url})
                data = response.json()

                # Video manzilini foydalanuvchiga jo'natish
                video_media = data.get('contents', [])[0].get('media', '')
                if video_media:
                    await bot.send_video(message.chat.id, video_media)
                else:
                    await message.reply("Video topilmadi yoki qayta yuklanmadi.")
        except Exception as e:
            await message.reply("Xatolik yuz berdi: " + str(e))


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
