from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio


api = ""
bot = Bot(token=api)

dp = Dispatcher(bot, storage=MemoryStorage())

start_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Рассчитать"), KeyboardButton(text="Информация")],
        [InlineKeyboardButton(text="Купить")]
    ], resize_keyboard=True
)


inline_kb = InlineKeyboardMarkup()
inline_button_calories = InlineKeyboardButton(text="Рассчитать норму калорий", callback_data="calories")
inline_button_formulas = InlineKeyboardButton(text="Формулы расчёта", callback_data="formulas")
inline_kb.add(inline_button_calories, inline_button_formulas)

inline_button_products = InlineKeyboardMarkup()
products = ["Продукт1", "Продукт2", "Продукт3", "Продукт4"]
button_row = [InlineKeyboardButton(text=product, callback_data="product_buying") for product in products]
inline_button_products.row(*button_row)

class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

@dp.message_handler(commands=["start"])
async def start_message(message):
    await message.answer("Привет! Я бот, помогающий твоему здоровью.", reply_markup=start_menu)

@dp.message_handler(text = "Информация")
async def inform(message):
    await message.answer("Информация о боте!")

@dp.message_handler(text="Рассчитать")
async def main_menu(message):
    await message.answer("Выберите опцию:", reply_markup=inline_kb)

@dp.callback_query_handler(text="formulas")
async def get_formulas(call):
    formulas_message = (
        "Формула Миффлина-Сан Жеора:"
        "Для мужчин: BMR = 10 * вес (кг) + 6.25 * рост (см) - 5 * возраст (лет) + 5"
        "Для женщин: BMR = 10 * вес (кг) + 6.25 * рост (см) - 5 * возраст (лет) - 161"
    )
    await call.message.answer(formulas_message, reply_markup=inline_kb)
    await call.answer()

@dp.callback_query_handler(text="calories")
async def set_age(call):
    await call.message.answer("Введите свой возраст:")
    await UserState.age.set()

@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age=message.text)
    await message.answer("Введите свой рост:")
    await UserState.growth.set()

@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=message.text)
    await message.answer("Введите свой вес:")
    await UserState.weight.set()

@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight=message.text)
    data = await state.get_data()

    age = int(data["age"])
    growth = int(data["growth"])
    weight = int(data["weight"])

    calories_man = 10 * weight + 6.25 * growth - 5 * age + 5
    calories_woman = 10 * weight + 6.25 * growth - 5 * age - 161

    await message.answer(f"Ваша норма калорий для мужчин: {calories_man:.2f} ккал")
    await message.answer(f"Ваша норма калорий для женщин: {calories_woman:.2f} ккал")

    await state.finish()

@dp.message_handler(text="Купить")
async def get_buying_list(message):
    product_count = 4
    product_price = 100
    products_info = [(i, product_price * i) for i in range(1, product_count + 1)]
    image_files = ["files/5.jpg", "files/6.jpg", "files/7.jpg", "files/8.jpg"]

    for i, (number, price) in enumerate(products_info):
        product_message = f"Название: Product {number} | Описание: описание {number} | Цена: {price}"
        await message.answer(product_message)

        with open(image_files[i], "rb") as img:
            await message.answer_photo(img)

    await message.answer("Выберите продукт для покупки:", reply_markup=inline_button_products)

@dp.callback_query_handler(text="product_buying")
async def send_confirm_message(call):
    await call.message.answer("Вы успешно приобрели продукт!")
    await call.answer()

@dp.message_handler()
async def all_message(message):
    await message.answer("Введите команду /start, чтобы начать общение.")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)