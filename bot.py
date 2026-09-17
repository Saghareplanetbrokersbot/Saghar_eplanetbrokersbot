import os
import logging
import threading

from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    BusinessConnectionHandler,
    ContextTypes,
    filters,
)

# ============================================================
# ePlanet Brokers - Saghar Support Bot
# Supports:
# 1) Normal Telegram Bot chats
# 2) Telegram Business / Secretary Mode
# ============================================================

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN is not set in Render Environment Variables.")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# -----------------------------
# Flask health check for Render
# -----------------------------
app = Flask(__name__)


@app.get("/")
def health():
    return "ePlanet Brokers bot is running.", 200


def run_web_server():
    port = int(os.environ.get("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)


# -----------------------------
# Welcome + menu
# -----------------------------
WELCOME_TEXT = """سلام و وقت بخیر 🌷

من ساغر هستم، پشتیبانی ePlanet Brokers.
به پشتیبانی ePlanet Brokers خوش آمدید 🤍

لطفاً موضوع موردنظر خود را از منوی زیر انتخاب کنید تا راهنمایی‌تان کنم 👇"""


def main_menu():
    keyboard = [
        [
            InlineKeyboardButton("🔐 ورود به سایت / پنل کاربری", callback_data="website"),
        ],
        [
            InlineKeyboardButton("💳 واریز و برداشت", callback_data="deposit"),
        ],
        [
            InlineKeyboardButton("📱 اتصال متاتریدر 5", callback_data="mt5"),
        ],
        [
            InlineKeyboardButton("🔑 تغییر / بازیابی رمز عبور", callback_data="password"),
        ],
        [
            InlineKeyboardButton("👤 ارتباط مستقیم با مدیر حساب", callback_data="manager"),
        ],
        [
            InlineKeyboardButton("🎓 سیستم کور / یاسر رضایی", callback_data="core"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


CORE_TEXT = """سلام و وقت بخیر

خواهشمند است در صورتی که از دانشجویان سیستم کور و جناب آقای یاسر رضایی هستید، جهت پیگیری امور و طرح تمامی سؤالات خود فقط از طریق آیدی زیر اقدام فرمایید:
t.me/hoomaneplanetbrokers

لطفاً از ادامه مکاتبه در این صفحه خودداری نمایید. در صورت دانشجوی ایشان بودن، پاسخگویی صرفاً از طریق آیدی اعلام‌شده انجام خواهد شد.

🔴 در صورتی که در پنل کاربری شما نام «ساغر» به عنوان مدیر حساب ثبت شده است، لطفاً ایمیل ثبت‌نامی خود را ارسال فرمایید تا حساب شما مورد بررسی قرار گیرد.

لطفاً در صورتی که مدیر حساب شما ساغر نیست، ایمیل خود را ارسال نکنید.

با تشکر از همکاری شما."""


WEBSITE_TEXT = """با سلام

سرویسی که تحت عنوان «اینترنت ملی» در اختیار کاربران ایران قرار گرفته بود، یک امکان اضافی برای تسهیل دسترسی کاربران محسوب می‌شد. متأسفانه در حال حاضر به دلیل محدودیت‌ها و فیلترینگ اعمال‌شده، این سرویس در دسترس نیست.

لطفاً توجه داشته باشید که این موضوع به معنای اختلال یا مشکل در خدمات بروکر نیست. وب‌سایت بین‌المللی، پنل کاربری، سرورهای معاملاتی و سایر خدمات اصلی ePlanet بدون هیچ‌گونه اختلالی در حال ارائه خدمات هستند.

در حال حاضر زمان مشخصی برای بازگشت یا رفع این محدودیت وجود ندارد و در صورت ایجاد هرگونه تغییر، اطلاع‌رسانی لازم انجام خواهد شد.

در صورتی که از داخل ایران به خدمات ePlanet دسترسی دارید، لازم است برای ورود به وب‌سایت و سایر آدرس‌های بروکر از ابزار تغییر IP مناسب (فیلترشکن) استفاده فرمایید.

https://my.eplanetbrokers.com/fa/auth/sign-in"""


DEPOSIT_TEXT = """با سلام و وقت بخیر

جهت پیگیری واریز یا برداشت، لطفاً از طریق پنل کاربری خود یک تیکت ثبت فرمایید تا درخواست شما توسط تیم مربوطه بررسی و پیگیری شود."""


MT5_TEXT = """برای اتصال حساب معاملاتی به MetaTrader 5:

1️⃣ وارد MetaTrader 5 شوید.
2️⃣ از منوی File گزینه Open an Account را انتخاب کنید.
3️⃣ عبارت ePlanet Brokers را جستجو کنید.
4️⃣ گزینه ePlanet Brokers را انتخاب کرده و Next را بزنید.
5️⃣ در پنجره جدید، آخرین گزینه را انتخاب کنید.
6️⃣ Login را شماره حساب معاملاتی وارد کنید.
7️⃣ Password را رمز دریافت‌شده از طریق ایمیل وارد کنید.
8️⃣ Server را روی ePlanet Brokers قرار دهید.
9️⃣ روی Finish بزنید.

راهنمای ویدیویی:
https://dl.eplanetbrokers.com/tutorial/fa/connecttometa-fa.mp4"""


PASSWORD_TEXT = """با سلام و وقت بخیر،

جهت تغییر رمز عبور حساب معاملاتی، نیازی به دریافت کد تأیید از طریق ایمیل یا ثبت تیکت پشتیبانی نمی‌باشد. لطفاً وارد پنل کاربری خود شده و از بخش «حساب‌های من»، حساب موردنظر را انتخاب فرمایید.

سپس از طریق منوی سه‌نقطه، گزینه «تغییر رمز اصلی پلتفرم معاملاتی» را انتخاب کرده و رمز عبور جدید خود را ثبت نمایید.

در صورت نیاز به راهنمایی بیشتر، با کمال میل در خدمت شما خواهیم بود.

بازیابی رمز عبور:
https://dl.eplanetbrokers.com/tutorial/fa/n/passreco.mp4

با سپاس از همراهی شما"""


MANAGER_TEXT = """با سلام و وقت بخیر

درخواست شما جهت ارتباط مستقیم با مدیر حساب ثبت شد.

لطفاً از طریق آیدی زیر با مدیر حساب در ارتباط باشید:
t.me/Saghar_eplanetbrokers

در صورتی که مدیر حساب شما ساغر است، می‌توانید درخواست خود را از طریق همین آیدی پیگیری فرمایید."""


# -----------------------------
# Helpers
# -----------------------------
def is_business_message(update: Update) -> bool:
    return update.business_message is not None


async def send_menu(message):
    """reply_text automatically carries business_connection_id for Business chats."""
    await message.reply_text(
        WELCOME_TEXT,
        reply_markup=main_menu(),
    )


# -----------------------------
# /start for normal bot
# -----------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    if message:
        await send_menu(message)


# -----------------------------
# Business connection logging
# -----------------------------
async def business_connection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    connection = update.business_connection
    if connection:
        logger.info(
            "Business connection: id=%s enabled=%s user_chat_id=%s",
            connection.id,
            connection.is_enabled,
            connection.user_chat_id,
        )


# -----------------------------
# Normal text + Business text
# -----------------------------
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    if not message or not message.text:
        return

    text = message.text.strip().lower()

    # Core / Yaser Rezaei
    core_words = [
        "سیستم کور",
        "سیستمکور",
        "یاسر رضایی",
        "یاسر رضایی",
        "yaser rezaei",
        "yaserrezaei",
    ]
    if any(word in text for word in core_words):
        await message.reply_text(CORE_TEXT)
        return

    # For any other new text, show the welcome + menu.
    await send_menu(message)


# -----------------------------
# Button actions
# Works for normal bot AND Business/Secretary Mode.
# -----------------------------
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return

    await query.answer()

    message = query.message
    if not message:
        return

    data = query.data

    if data == "website":
        await message.reply_text(WEBSITE_TEXT)

    elif data == "deposit":
        await message.reply_text(DEPOSIT_TEXT)

    elif data == "mt5":
        await message.reply_text(MT5_TEXT)

    elif data == "password":
        await message.reply_text(PASSWORD_TEXT)

    elif data == "manager":
        await message.reply_text(MANAGER_TEXT)

    elif data == "core":
        await message.reply_text(CORE_TEXT)



# -----------------------------
# Error logging
# -----------------------------
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.exception("Telegram update error: %s", context.error)


# -----------------------------
# Main
# -----------------------------
def main():
    # Flask health server runs in the background.
    threading.Thread(target=run_web_server, daemon=True).start()

    application = Application.builder().token(TOKEN).build()

    # Normal bot commands.
    application.add_handler(CommandHandler("start", start))

    # Telegram Business / Secretary Mode.
    # python-telegram-bot 22 supports BUSINESS_MESSAGE updates.
    application.add_handler(
        BusinessConnectionHandler(business_connection)
    )

    application.add_handler(
        MessageHandler(
            filters.UpdateType.BUSINESS_MESSAGE & filters.TEXT,
            text_handler,
        )
    )

    # Normal Telegram bot text messages.
    # Exclude Business messages so they are not handled twice.
    application.add_handler(
        MessageHandler(
            filters.TEXT
            & ~filters.COMMAND
            & ~filters.UpdateType.BUSINESS_MESSAGE,
            text_handler,
        )
    )

    # Inline keyboard buttons.
    application.add_handler(CallbackQueryHandler(button_handler))

    application.add_error_handler(error_handler)

    logger.info("ePlanet Brokers bot started - Normal Bot + Secretary Mode")
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
