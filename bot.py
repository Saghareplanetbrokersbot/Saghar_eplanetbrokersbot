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

# ============================================================
# ePlanet Brokers Telegram Support Bot
# IMPORTANT: There is NO working-hours/time restriction here.
# The bot is designed to answer 24/7.
# ============================================================

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()

MANAGER_USERNAME = os.getenv(
    "MANAGER_USERNAME",
    "Saghar_eplanetbrokers"
).lstrip("@")

REFERRAL_USERNAME = os.getenv(
    "REFERRAL_USERNAME",
    "hoomaneplanetbrokers"
).lstrip("@")

SITE_URL = "https://my.eplanetbrokers.com/fa/auth/sign-in"
MT5_VIDEO = "https://dl.eplanetbrokers.com/tutorial/fa/connecttometa-fa.mp4"
PASSWORD_VIDEO = "https://dl.eplanetbrokers.com/tutorial/fa/n/passreco.mp4"

# ---------------- WEB HEALTH CHECK FOR RENDER ----------------

web_app = Flask(__name__)

@web_app.get("/")
def health():
    return "ePlanet Telegram Support Bot is running 24/7.", 200

def start_web_server():
    port = int(os.getenv("PORT", "10000"))
    web_app.run(host="0.0.0.0", port=port)


# ---------------- TELEGRAM MENU ----------------

def menu():
    buttons = [
        [InlineKeyboardButton("🔐 ورود به سایت / پنل کاربری", callback_data="site")],
        [InlineKeyboardButton("💳 واریز و برداشت", callback_data="deposit")],
        [InlineKeyboardButton("📱 اتصال متاتریدر 5", callback_data="mt5")],
        [InlineKeyboardButton("🔑 تغییر / بازیابی رمز عبور", callback_data="password")],
        [InlineKeyboardButton("👤 ارتباط مستقیم با مدیر حساب", callback_data="manager")],
        [InlineKeyboardButton("🎓 سیستم کور / یاسر رضایی", callback_data="referral")],
    ]
    return InlineKeyboardMarkup(buttons)


WELCOME = """سلام و وقت بخیر 🌷

من ساغر هستم، پشتیبانی ePlanet Brokers.
خوش آمدید 🤍

لطفاً موضوع موردنظر خود را از منوی زیر انتخاب کنید تا راهنمایی‌تان کنم 👇"""


SITE_TEXT = f"""با سلام و وقت بخیر 🌷

سرویسی که تحت عنوان «اینترنت ملی» در اختیار کاربران ایران قرار گرفته بود، یک امکان اضافی برای تسهیل دسترسی کاربران محسوب می‌شد. متأسفانه در حال حاضر به دلیل محدودیت‌ها و فیلترینگ اعمال‌شده، این سرویس در دسترس نیست.

لطفاً توجه داشته باشید که این موضوع به معنای اختلال یا مشکل در خدمات بروکر نیست. وب‌سایت بین‌المللی، پنل کاربری، سرورهای معاملاتی و سایر خدمات اصلی ePlanet بدون هیچ‌گونه اختلالی در حال ارائه خدمات هستند.

در حال حاضر زمان مشخصی برای بازگشت یا رفع این محدودیت وجود ندارد و در صورت ایجاد هرگونه تغییر، اطلاع‌رسانی لازم انجام خواهد شد.

در صورتی که از داخل ایران به خدمات ePlanet دسترسی دارید، لازم است برای ورود به وب‌سایت و سایر آدرس‌های بروکر از ابزار تغییر IP مناسب (فیلترشکن) استفاده فرمایید.

{SITE_URL}"""


DEPOSIT_TEXT = """با سلام و وقت بخیر 🌷

جهت پیگیری واریز یا برداشت، لطفاً از طریق پنل کاربری خود یک تیکت ثبت فرمایید تا درخواست شما توسط تیم مربوطه بررسی و پیگیری شود."""


MT5_TEXT = f"""با سلام و وقت بخیر 🌷

برای اتصال MT5 لطفاً مراحل زیر را انجام دهید:

1️⃣ در متاتریدر 5 وارد File > Open an Account شوید.
2️⃣ عبارت ePlanet Brokers را جستجو کنید.
3️⃣ گزینه Find Your Company را انتخاب کنید.
4️⃣ ePlanet Brokers را انتخاب کرده و Next را بزنید.
5️⃣ در پنجره جدید گزینه آخر را انتخاب کنید.
6️⃣ Login = شماره حساب معاملاتی
7️⃣ Password = رمز عبوری که از طریق ایمیل دریافت کرده‌اید.
8️⃣ Server = ePlanet Brokers
9️⃣ در پایان Finish را بزنید.

🎥 ویدئوی آموزش اتصال:
{MT5_VIDEO}"""


PASSWORD_TEXT = f"""با سلام و وقت بخیر 🌷

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


REFERRAL_TEXT = f"""سلام و وقت بخیر 🌷

خواهشمند است در صورتی که از دانشجویان سیستم کور و جناب آقای یاسر رضایی هستید، جهت پیگیری امور و طرح تمامی سؤالات خود فقط از طریق آیدی زیر اقدام فرمایید:

https://t.me/{REFERRAL_USERNAME}

لطفاً از ادامه مکاتبه در این صفحه خودداری نمایید. در صورت دانشجوی ایشان بودن، پاسخگویی صرفاً از طریق آیدی اعلام‌شده انجام خواهد شد.

🔴 در صورتی که در پنل کاربری شما نام «ساغر» به عنوان مدیر حساب ثبت شده است، لطفاً ایمیل ثبت‌نامی خود را ارسال فرمایید تا حساب شما مورد بررسی قرار گیرد.

لطفاً در صورتی که مدیر حساب شما ساغر نیست، ایمیل خود را ارسال نکنید.

با تشکر از همکاری شما."""


RESPONSES = {
    "site": SITE_TEXT,
    "deposit": DEPOSIT_TEXT,
    "mt5": MT5_TEXT,
    "password": PASSWORD_TEXT,
    "manager": MANAGER_TEXT,
    "referral": REFERRAL_TEXT,
}


# ---------------- TEXT DETECTION ----------------

def detect_topic(text: str):
    t = text.lower().strip()

    if any(word in t for word in [
        "سیستم کور", "یاسر رضایی", "یاسر", "دانشجوی یاسر",
        "yaser rezaei", "hooman", "کور"
    ]):
        return "referral"

    if any(word in t for word in [
        "مدیر حساب", "مدیرم", "با مدیر", "صحبت با مدیر",
        "ارتباط مستقیم", "مدیر", "ساغر", "manager"
    ]):
        return "manager"

    if any(word in t for word in [
        "واریز", "برداشت", "واریز و برداشت", "deposit",
        "withdraw", "withdrawal", "تیکت مالی"
    ]):
        return "deposit"

    if any(word in t for word in [
        "متاتریدر", "متا تریدر", "mt5", "mt 5",
        "اتصال متا", "اتصال mt", "سرور متاتریدر"
    ]):
        return "mt5"

    if any(word in t for word in [
        "رمز", "پسورد", "password", "فراموشی رمز",
        "بازیابی رمز", "تغییر رمز", "رمز عبور"
    ]):
        return "password"

    if any(word in t for word in [
        "سایت", "وب سایت", "وبسایت", "پنل", "ورود",
        "لاگین", "login", "فیلترشکن", "اینترنت ملی",
        "دسترسی به سایت"
    ]):
        return "site"

    return None


# ---------------- TELEGRAM HANDLERS ----------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        WELCOME,
        reply_markup=menu()
    )


async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    response = RESPONSES.get(query.data)

    if response:
        await query.message.reply_text(
            response,
            reply_markup=menu()
        )
    else:
        await query.message.reply_text(
            WELCOME,
            reply_markup=menu()
        )


async def text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    topic = detect_topic(text)

    if topic:
        await update.message.reply_text(
            RESPONSES[topic],
            reply_markup=menu()
        )
    else:
        await update.message.reply_text(
            """لطفاً موضوع موردنظر خود را از منوی زیر انتخاب کنید 👇

اگر سؤال دیگری دارید، آن را واضح بنویسید.""",
            reply_markup=menu()
        )


def run_telegram_bot():
    if not TOKEN:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN is missing. Add it in Render Environment Variables."
        )

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            text_message
        )
    )

    # 24/7 polling. There is deliberately NO time/working-hours check.
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    threading.Thread(
        target=start_web_server,
        daemon=True
    ).start()

    run_telegram_bot()
