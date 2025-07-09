
from datetime import datetime, time, timedelta
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor

API_TOKEN = '8028029772:AAHr6CUMSmc3Hrk4-GY-sbjcEgRAUGbcByw'
ADMIN_ID = 420626866  # @Kaliakpari ID

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

user_data = {}

# Кнопки
gender_kb = ReplyKeyboardMarkup(resize_keyboard=True)
gender_kb.add(KeyboardButton("Мужчина"), KeyboardButton("Женщина"))

payment_kb = ReplyKeyboardMarkup(resize_keyboard=True)
payment_kb.add(KeyboardButton("Kaspi"), KeyboardButton("Halyk"))

def is_working_hours():
    now = datetime.utcnow() + timedelta(hours=5)  # UTC+5
    return time(9, 0) <= now.time() <= time(21, 0)

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    if not is_working_hours():
        await message.answer("Бот принимает заказы с 9:00 до 21:00 по времени Астаны.")
        return
    await message.answer("Привет! Отправь фото товара, который хочешь заказать.")

@dp.message_handler(content_types=types.ContentType.PHOTO)
async def photo_handler(message: types.Message):
    if not is_working_hours():
        await message.answer("Бот принимает заказы с 9:00 до 21:00 по времени Астаны.")
        return
    user_data[message.from_user.id] = {'photo_id': message.photo[-1].file_id}
    await message.answer("Теперь укажи свой пол:", reply_markup=gender_kb)

@dp.message_handler(lambda message: message.text in ["Мужчина", "Женщина"])
async def gender_handler(message: types.Message):
    user_data[message.from_user.id]['gender'] = message.text
    await message.answer("Какой размер хотите заказать, если не уверены Укажи свой рост и вес (например: 175см, 70кг).")

@dp.message_handler(lambda message: True if message.from_user.id in user_data and 'size' not in user_data[message.from_user.id] else False)
async def size_handler(message: types.Message):
    user_data[message.from_user.id]['size'] = message.text
    await message.answer("Укажи адрес доставки по Астане (адрес, квартиру,подъезд, этаж и контактный номер).")

@dp.message_handler(lambda message: True if message.from_user.id in user_data and 'address' not in user_data[message.from_user.id] else False)
async def address_handler(message: types.Message):
    user_data[message.from_user.id]['address'] = message.text
    await message.answer("Выбери способ оплаты:", reply_markup=payment_kb)

@dp.message_handler(lambda message: message.text in ["Kaspi", "Halyk"])
async def payment_handler(message: types.Message):
    user_data[message.from_user.id]['payment'] = message.text
    await message.answer("Укажи номер телефона, привязанный к Kaspi или Halyk.")

@dp.message_handler(lambda message: message.text.startswith('+') or message.text.replace(' ', '').isdigit())
async def phone_handler(message: types.Message):
    user_data[message.from_user.id]['phone'] = message.text
    await message.answer("Если у вас есть промокод — введите его. Или напишите 'нет'.")

@dp.message_handler(lambda message: message.from_user.id in user_data and 'phone' in user_data[message.from_user.id] and 'promo' not in user_data[message.from_user.id])
async def promo_handler(message: types.Message):
    user_data[message.from_user.id]['promo'] = message.text
    data = user_data[message.from_user.id]

    msg = (
        "🧾 Новый заказ:\n\n"
        f"Пол: {data['gender']}\n"
        f"Размеры: {data['size']}\n"
        f"Адрес: {data['address']}\n"
        f"Способ оплаты: {data['payment']}\n"
        f"Номер: {data['phone']}\n"
        f"Промокод: {data['promo']}"
    )
    try:
        await bot.send_photo(chat_id=ADMIN_ID, photo=data['photo_id'], caption=msg)
    except Exception as e:
        await message.answer("Произошла ошибка при отправке заказа администратору.")
        return

    await message.answer("Спасибо! Ваш заказ принят, мы скоро свяжемся с вами.")
    user_data.pop(message.from_user.id, None)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
