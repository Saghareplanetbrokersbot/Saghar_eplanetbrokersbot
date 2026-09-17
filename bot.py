import os
import re
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

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
MANAGER_USERNAME = os.environ.get("MANAGER_USERNAME", "Saghar_eplanetbrokers")
REFERRAL_USERNAME = os.environ.get("REFERRAL_USERNAME", "hoomaneplanetbrokers")

SITE_URL = "https://my.eplanetbrokers.com/fa/auth/sign-in"
MT5_VIDEO = "https://dl.eplanetbrokers.com/tutorial/fa/connecttometa-fa.mp4"
PASSWORD_VIDEO = "https://dl.eplanetbrokers.com/tutorial/fa/n/passreco.mp4"

app_web = Flask(__name__)

@app_web.get("/")
def health():
    return "ePlanet Telegram Support Bot is running."

def main_menu():
    keyboard = [
        [InlineKeyboardButton("🔐 ورود به سایت / پنل کاربری", callback_data="site")],
        [InlineKeyboardButton("💳 واریز و برداشت", callback_data="deposit")],
        [InlineKeyboardButton("📱 اتصال متاتریدر 5", callback_data="mt5")],
        [InlineKeyboardButton("🔑 تغییر / بازیابی رمز عبور", callback_data="password")],
        [InlineKeyboardButton("👤 ارتباط مستقیم با مدیر حساب", callback_data="manager")],
        [InlineKeyboardButton("🎓 دانشجویان سیستم کور / یاسر رضایی", callback_data="referral")],
    ]
    return InlineKeyboardMarkup(keyboard)

WELCOME = """سلام و وقت بخیر 🌷

من ساغر هستم، پشتیبانی ePlanet Brokers.
خوش آمدید.

لطفاً موضوع موردنظر خود را از منوی زیر انتخاب کنید تا راهنمایی‌تان کنم 👇"""

REFERRAL_TEXT = """سلام و وقت بخیر

خواهشمند است در صورتی که از دانشجویان سیستم کور و جناب آقای یاسر رضایی هستید، جهت پیگیری امور و طرح تمامی سؤالات خود فقط از طریق آیدی زیر اقدام فرمایید:
https://t.me/hoomaneplanetbrokers

لطفاً از ادامه مکاتبه در این صفحه خودداری نمایید. در صورت دانشجوی ایشان بودن، پاسخگویی صرفاً از طریق آیدی اعلام‌شده انجام خواهد شد.

🔴 در صورتی که در پنل کاربری شما نام «ساغر» به عنوان مدیر حساب ثبت شده است، لطفاً ایمیل ثبت‌نامی خود را ارسال فرمایید تا حساب شما مورد بررسی قرار گیرد.

لطفاً در صورتی که مدیر حساب شما ساغر نیست، ایمیل خود را ارسال نکنید.

با تشکر از همکاری شما."""

SITE_TEXT = f"""با سلام

سرویسی که تحت عنوان «اینترنت ملی» در اختیار کاربران ایران قرار گرفته بود، یک امکان اضافی برای تسهیل دسترسی کاربران محسوب می‌شد. متأسفانه در حال حاضر به دلیل محدودیت‌ها و فیلترینگ اعمال‌شده، این سرویس در دسترس نیست.

لطفاً توجه داشته باشید که این موضوع به معنای اختلال یا مشکل در خدمات بروکر نیست. وب‌سایت بین‌المللی، پنل کاربری، سرورهای معاملاتی و سایر خدمات اصلی ePlanet بدون هیچ‌گونه اختلالی در حال ارائه خدمات هستند.

در حال حاضر زمان مشخصی برای بازگشت یا رفع این محدودیت وجود ندارد و در صورت ایجاد هرگونه تغییر، اطلاع‌رسانی لازم انجام خواهد شد.

در صورتی که از داخل ایران به خدمات ePlanet دسترسی دارید، لازم است برای ورود به وب‌سایت و سایر آدرس‌های بروکر از ابزار تغییر IP مناسب (فیلترشکن) استفاده فرمایید.

{SITE_URL}"""

DEPOSIT_TEXT = """با سلام و وقت بخیر

جهت پیگیری واریز یا برداشت، لطفاً از طریق پنل کاربری خود یک تیکت ثبت فرمایید تا درخواست شما توسط تیم مربوطه بررسی و پیگیری شود."""

MT5_TEXT = f"""با سلام و وقت بخیر

برای اتصال MT5 لطفاً مراحل زیر را انجام دهید:

1️⃣ در متاتریدر 5 وارد File > Open an Account شوید.
2️⃣ عبارت ePlanet Brokers را جستجو کنید.
3️⃣ گزینه Find Your Company را انتخاب کنید.
4️⃣ ePlanet Brokers را انتخاب کرده و Next را بزنید.
5️⃣ در پنجره جدید، گزینه آخر را انتخاب کنید.
6️⃣ Login = شماره حساب معاملاتی
7️⃣ Password = رمز عبوری که از طریق ایمیل دریافت کرده‌اید.
8️⃣ Server = ePlanet Brokers
9️⃣ در پایان Finish را بزنید.

🎥 ویدئوی آموزش اتصال:
{MT5_VIDEO}"""

PASSWORD_TEXT = f"""با سلام و وقت بخیر،

جهت تغییر رمز عبور حساب معاملاتی، نیازی به دریافت کد تأیید از طریق ایمیل یا ثبت تیکت پشتیبانی نمی‌باشد.

لطفاً وارد پنل کاربری خود شده و از بخش «حساب‌های من»، حساب موردنظر را انتخاب فرمایید.

سپس از طریق منوی سه‌نقطه، گزینه «تغییر رمز اصلی پلتفرم معاملاتی» را انتخاب کرده و رمز عبور جدید خود را ثبت نمایید.

🎥 ویدئوی بازیابی رمز عبور:
{PASSWORD_VIDEO}

با سپاس از همراهی شما"""

MANAGER_TEXT = f"""با سلام و وقت بخیر 🌷

درخواست شما جهت ارتباط مستقیم با مدیر حساب ثبت شد.

لطفاً از طریق آیدی زیر با مدیر حساب در ارتباط باشید:
https://t.me/{MANAGER_USERNAME}

در صورتی که مدیر حساب شما ساغر است، می‌توانید درخواست خود را از طریق همین آیدی پیگیری فرمایید."""

RESPONSES = {
    "site": SITE_TEXT,
    "deposit": DEPOSIT_TEXT,
    "mt5": MT5_TEXT,
    "password": PASSWORD_TEXT,
    "manager": MANAGER_TEXT,
    "referral": REFERRAL_TEXT,
}

def classify(text: str):
    t = text.lower().strip()

    if any(x in t for x in [
        "سیستم کور", "یاسر رضایی", "یاسر", "کور", "yaser rezaei", "hooman",
    ]):
        return "referral"

    if any(x in t for x in [
        "مدیر حساب", "مدیرم", "مدیر", "ساغر", "صحبت مستقیم", "آنلاین با مدیر",
        "ارتباط با مدیر", "با مدیر صحبت", "manager",
    ]):
        return "manager"

    if any(x in t for x in [
        "واریز", "برداشت", "تیکت مالی", "deposit", "withdraw", "withdrawal",
    ]):
        return "deposit"

    if any(x in t for x in [
        "متاتریدر", "متا تریدر", "mt5", "mt 5", "اتصال mt", "سرور",
    ]):
        return "mt5"

    if any(x in t for x in [
        "رمز", "پسورد", "password", "فراموشی رمز", "بازیابی رمز",
        "تغییر رمز", "رمز عبور",
    ]):
        return "password"

    if any(x in t for x in [
        "سایت", "وب سایت", "وبسایت", "پنل", "ورود", "لاگین", "login",
        "فیلترشکن", "اینترنت ملی", "دسترسی به سایت",
    ]):
        return "site"

    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME, reply_markup=main_menu())

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    key = query.data
    if key in RESPONSES:
        await query.message.reply_text(
            RESPONSES[key],
            reply_markup=main_menu()
        )
    else:
        await query.message.reply_text(WELCOME, reply_markup=main_menu())

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    key = classify(text)

    if key:
        await update.message.reply_text(
            RESPONSES[key],
            reply_markup=main_menu()
        )
    else:
        await update.message.reply_text(
            """لطفاً موضوع موردنظر خود را از منوی زیر انتخاب کنید تا راهنمایی‌تان کنم 👇

اگر موضوع شما در منو نیست، می‌توانید درخواستتان را واضح بنویسید.""",
            reply_markup=main_menu()
        )

def run_web():
    port = int(os.environ.get("PORT", "10000"))
    app_web.run(host="0.0.0.0", port=port)

def run_bot():
    if not TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set.")

    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    run_bot()
