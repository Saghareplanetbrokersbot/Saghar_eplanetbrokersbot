import os
import threading

from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ePlanet Brokers - Telegram Support Bot
# 24/7 - NO working-hours restriction

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
MANAGER_USERNAME = os.getenv("MANAGER_USERNAME", "Saghar_eplanetbrokers").lstrip("@")
REFERRAL_USERNAME = os.getenv("REFERRAL_USERNAME", "hoomaneplanetbrokers").lstrip("@")

WELCOME_MESSAGE = """سلام و وقت بخیر 🌷

من ساغر هستم، پشتیبانی ePlanet Brokers.
به پشتیبانی ePlanet Brokers خوش آمدید 🤍

لطفاً موضوع موردنظر خود را از منوی زیر انتخاب کنید تا راهنمایی‌تان کنم 👇"""

SITE_MESSAGE = """با سلام

سرویسی که تحت عنوان «اینترنت ملی» در اختیار کاربران ایران قرار گرفته بود، یک امکان اضافی برای تسهیل دسترسی کاربران محسوب می‌شد. متأسفانه در حال حاضر به دلیل محدودیت‌ها و فیلترینگ اعمال‌شده، این سرویس در دسترس نیست.

لطفاً توجه داشته باشید که این موضوع به معنای اختلال یا مشکل در خدمات بروکر نیست. وب‌سایت بین‌المللی، پنل کاربری، سرورهای معاملاتی و سایر خدمات اصلی ePlanet بدون هیچ‌گونه اختلالی در حال ارائه خدمات هستند.

در حال حاضر زمان مشخصی برای بازگشت یا رفع این محدودیت وجود ندارد و در صورت ایجاد هرگونه تغییر، اطلاع‌رسانی لازم انجام خواهد شد.

در صورتی که از داخل ایران به خدمات ePlanet دسترسی دارید، لازم است برای ورود به وب‌سایت و سایر آدرس‌های بروکر از ابزار تغییر IP مناسب (فیلترشکن) استفاده فرمایید.

https://my.eplanetbrokers.com/fa/auth/sign-in"""

DEPOSIT_MESSAGE = """با سلام و وقت بخیر

جهت پیگیری واریز یا برداشت، لطفاً از طریق پنل کاربری خود یک تیکت ثبت فرمایید تا درخواست شما توسط تیم مربوطه بررسی و پیگیری شود."""

MT5_MESSAGE = """برای اتصال حساب معاملاتی به متاتریدر 5:

1. وارد MetaTrader 5 شوید.
2. از منوی File گزینه Open an Account را انتخاب کنید.
3. در قسمت جستجو عبارت ePlanet Brokers را وارد کنید.
4. گزینه Find Your Company را انتخاب کنید.
5. ePlanet Brokers را انتخاب کرده و روی Next بزنید.
6. در پنجره جدید، گزینه آخر را انتخاب کنید.
7. Login: شماره حساب معاملاتی
8. Password: رمز عبور دریافت‌شده در ایمیل
9. Server: ePlanet Brokers
10. روی Finish بزنید.

ویدئوی راهنما:
https://dl.eplanetbrokers.com/tutorial/fa/connecttometa-fa.mp4"""

PASSWORD_MESSAGE = """با سلام و وقت بخیر،

جهت تغییر رمز عبور حساب معاملاتی، نیازی به دریافت کد تأیید از طریق ایمیل یا ثبت تیکت پشتیبانی نمی‌باشد. لطفاً وارد پنل کاربری خود شده و از بخش «حساب‌های من»، حساب موردنظر را انتخاب فرمایید.

سپس از طریق منوی سه‌نقطه، گزینه «تغییر رمز اصلی پلتفرم معاملاتی» را انتخاب کرده و رمز عبور جدید خود را ثبت نمایید.

در صورت نیاز به راهنمایی بیشتر، با کمال میل در خدمت شما خواهیم بود.

بازیابی رمز عبور:
https://dl.eplanetbrokers.com/tutorial/fa/n/passreco.mp4

با سپاس از همراهی شما"""

MANAGER_MESSAGE = """با سلام و وقت بخیر

درخواست شما جهت ارتباط مستقیم با مدیر حساب ثبت شد.

لطفاً از طریق آیدی زیر با مدیر حساب در ارتباط باشید:
t.me/Saghar_eplanetbrokers

در صورتی که مدیر حساب شما ساغر است، می‌توانید درخواست خود را از طریق همین آیدی پیگیری فرمایید."""

REFERRAL_MESSAGE = """سلام و وقت بخیر

خواهشمند است در صورتی که از دانشجویان سیستم کور و جناب آقای یاسر رضایی هستید، جهت پیگیری امور و طرح تمامی سؤالات خود فقط از طریق آیدی زیر اقدام فرمایید:
t.me/hoomaneplanetbrokers

لطفاً از ادامه مکاتبه در این صفحه خودداری نمایید. در صورت دانشجوی ایشان بودن، پاسخگویی صرفاً از طریق آیدی اعلام‌شده انجام خواهد شد.

🔴 در صورتی که در پنل کاربری شما نام «ساغر» به عنوان مدیر حساب ثبت شده است، لطفاً ایمیل ثبت‌نامی خود را ارسال فرمایید تا حساب شما مورد بررسی قرار گیرد.

لطفاً در صورتی که مدیر حساب شما ساغر نیست، ایمیل خود را ارسال نکنید.

با تشکر از همکاری شما."""

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔐 ورود به سایت / پنل کاربری", callback_data="site")],
        [InlineKeyboardButton("💳 واریز و برداشت", callback_data="deposit")],
        [InlineKeyboardButton("📱 اتصال متاتریدر 5", callback_data="mt5")],
        [InlineKeyboardButton("🔑 تغییر / بازیابی رمز عبور", callback_data="password")],
        [InlineKeyboardButton("👤 ارتباط مستقیم با مدیر حساب", callback_data="manager")],
        [InlineKeyboardButton("🎓 سیستم کور / یاسر رضایی", callback_data="referral")],
    ])

async def send_welcome(update: Update):
    await update.effective_message.reply_text(
        WELCOME_MESSAGE,
        reply_markup=main_menu(),
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_welcome(update)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    responses = {
        "site": SITE_MESSAGE,
        "deposit": DEPOSIT_MESSAGE,
        "mt5": MT5_MESSAGE,
        "password": PASSWORD_MESSAGE,
        "manager": MANAGER_MESSAGE,
        "referral": REFERRAL_MESSAGE,
    }

    text = responses.get(query.data)
    if text:
        await query.message.reply_text(text, reply_markup=main_menu())
    else:
        await send_welcome(update)

def normalize(text: str) -> str:
    return " ".join(text.lower().strip().split())

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = normalize(update.message.text or "")

    # Greetings / short general messages -> ALWAYS show the full welcome first.
    greetings = [
        "سلام", "سلام وقت بخیر", "سلام و وقت بخیر", "salam",
        "hello", "hi", "hey", "درود", "وقت بخیر"
    ]
    if text in greetings or len(text) <= 2:
        await send_welcome(update)
        return

    # Topic recognition for customers who type their request directly.
    if any(k in text for k in [
        "یاسر", "رضایی", "سیستم کور", "سیستم کر", "یاسر رضایی", "yaser", "yas er"
    ]):
        await update.message.reply_text(REFERRAL_MESSAGE, reply_markup=main_menu())
        return

    if any(k in text for k in [
        "مدیر حساب", "مدیرم", "ارتباط مستقیم", "تماس با مدیر", "آیدی مدیر"
    ]):
        await update.message.reply_text(MANAGER_MESSAGE, reply_markup=main_menu())
        return

    if any(k in text for k in [
        "واریز", "برداشت", "شارژ", "دپوزیت", "withdraw", "deposit"
    ]):
        await update.message.reply_text(DEPOSIT_MESSAGE, reply_markup=main_menu())
        return

    if any(k in text for k in [
        "متاتریدر", "متا تریدر", "mt5", "meta trader", "متاتریدر 5"
    ]):
        await update.message.reply_text(MT5_MESSAGE, reply_markup=main_menu())
        return

    if any(k in text for k in [
        "رمز", "پسورد", "password", "بازیابی رمز", "تغییر رمز"
    ]):
        await update.message.reply_text(PASSWORD_MESSAGE, reply_markup=main_menu())
        return

    if any(k in text for k in [
        "ورود", "سایت", "پنل", "لاگین", "login", "website", "فیلترشکن",
        "اینترنت ملی", "باز نمیشه", "باز نمی‌شود", "دسترسی"
    ]):
        await update.message.reply_text(SITE_MESSAGE, reply_markup=main_menu())
        return

    # Any other message -> show the welcome + menu.
    await send_welcome(update)

# Small web server for Render health checks.
app = Flask(__name__)

@app.get("/")
def health():
    return "ePlanet Brokers Telegram Bot is running.", 200

def run_web():
    port = int(os.getenv("PORT", "10000"))
    app.run(host="0.0.0.0", port=port, use_reloader=False)

def run_bot():
    if not TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set in Render Environment.")

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    web_thread = threading.Thread(target=run_web, daemon=True)
    web_thread.start()

    print("==> ePlanet Brokers bot is starting 24/7...")
    run_bot()
