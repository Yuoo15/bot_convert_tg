import asyncio
from io import BytesIO
from os import remove

from skimage import io as sk_io
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import CommandStart
from middle import CheckLink
from config import config
API_TOKEN = config.bot_token.get_secret_value()
bot = Bot(token=API_TOKEN)
dp = Dispatcher()
dp.message.middleware(CheckLink())

FORMAT = ['png', 'jpeg', 'jbg', 'webp', 'bmp', 'ppm']
file_storage = {} #хранения загруженных файлов
@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Добро пожаловать! Пожалуйста, отправьте мне изображение.")

@dp.message(F.photo)
async def handle_photo(message: Message):
    photo_id = message.photo[-1].file_id
    message_id = message.message_id
    file_storage[message_id] = photo_id
    builder = InlineKeyboardBuilder()
    for fmt in FORMAT:
        builder.add(InlineKeyboardButton(text=fmt, callback_data=f"{fmt}:{message_id}"))
    await message.answer("Выберите формат:", reply_markup=builder.adjust(2).as_markup())


@dp.callback_query(F.data)
async def process_format_selection(callback: CallbackQuery):
    await callback.answer('Пожалуйста, подождите...')  # Отвечаем на запрос, чтобы избежать таймаута
    await bot.answer_callback_query(callback.id)
    format, message_id = callback.data.split(':')
    message_id = int(message_id)
    file_id = file_storage.get(message_id)

    if file_id:
        file_info = await bot.get_file(file_id) # Получаем информацию о файле
        file = await bot.download_file(file_info.file_path) # Загружаем файл
        img = sk_io.imread(BytesIO(file.read())) # Читаем изображение
        output_path = f'{message_id}.{format}' # Путь к выходному файлу
        sk_io.imsave(output_path, img) # Сохраняем изображение
        input_file = FSInputFile(output_path) # Создаем объект FSInputFile
        await bot.send_document(callback.from_user.id, input_file) # Отправляем документ

        del file_storage[message_id]
        remove(output_path) # Удаляем временный файл
        await callback.message.delete() # Удаляем сообщение с кнопками
        await callback.message.answer("Изображение успешно конвертировано, отправьте новое!")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('exit')