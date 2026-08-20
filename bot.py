import asyncio
import json
import logging
from datetime import datetime

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

# ============== НАСТРОЙКИ ==============
BOT_TOKEN = "8629237513:AAFJtsDqOmvokPkeUFIUpmAqSw9cffiMka4"   # токен от @BotFather
WEBAPP_URL = "https://alexnubmertwo.github.io/HotDog555/"       # ссылка на мини-приложение
ADMIN_GROUP_ID = -1001234567890                                  # ID группы, куда придут заказы
# ========================================

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()
router = Router()
dp.include_router(router)


def menu_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🌭🍔 Товары", web_app=WebAppInfo(url=WEBAPP_URL))]],
        resize_keyboard=True,
    )


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "🌭🔥 <b>Добро пожаловать в HotDog555!</b>\n\n"
        "Самые сочные хот-доги, бургеры и hotlet в городе — горячо, быстро, вкусно.\n\n"
        "Нажимайте «Товары», выбирайте блюда и оформляйте заказ прямо в приложении 👇",
        reply_markup=menu_keyboard(),
    )


@router.message(F.web_app_data)
async def got_order(message: Message):
    try:
        data = json.loads(message.web_app_data.data)
    except Exception:
        await message.answer("Не получилось прочитать заказ 😔 Попробуйте оформить его ещё раз.")
        return

    items = data.get("items", [])
    extras = data.get("extras", [])
    total = data.get("total", 0)
    name = data.get("name", "-")
    phone = data.get("phone", "-")
    comment = data.get("comment", "")
    location = data.get("location")

    if not items:
        await message.answer("Корзина пуста. Откройте «Товары» и выберите что-нибудь вкусное 🌭")
        return

    items_text = "\n".join(
        f"• {i['name']} × {i['qty']} — {i['price']*i['qty']:,} сум".replace(",", " ") for i in items
    )
    extras_text = ", ".join(f"{e['name']} (+{e['price']:,} сум)".replace(",", " ") for e in extras) if extras else "—"
    location_line = (
        f'<a href="https://maps.google.com/?q={location["lat"]},{location["lon"]}">📍 Открыть на карте</a>'
        if location else "не указана"
    )

    order_text = (
        "🆕 <b>НОВЫЙ ЗАКАЗ — HotDog555</b>\n"
        f"🕒 {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
        f"👤 <b>Имя:</b> {name}\n"
        f"📞 <b>Телефон:</b> {phone}\n"
        f"📍 <b>Локация:</b> {location_line}\n\n"
        f"🧾 <b>Заказ:</b>\n{items_text}\n\n"
        f"🧂 <b>Доп. услуги:</b> {extras_text}\n"
        f"💬 <b>Комментарий:</b> {comment or '—'}\n\n"
        f"💰 <b>Итого: {total:,} сум</b>".replace(",", " ")
    )

    try:
        await bot.send_message(ADMIN_GROUP_ID, order_text)
        if location:
            await bot.send_location(ADMIN_GROUP_ID, latitude=location["lat"], longitude=location["lon"])
    except Exception as e:
        logging.error(f"Не удалось отправить заказ в группу: {e}")

    await message.answer(
        f"✅ <b>Заказ принят!</b>\n\nМы уже готовим ваш заказ 🌭\n<b>Итого: {total:,} сум</b>".replace(",", " ") +
        "\n\nСпасибо, что выбрали HotDog555! Для нового заказа нажмите /start"
    )


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
