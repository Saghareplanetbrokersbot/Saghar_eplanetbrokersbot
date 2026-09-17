import os
import threading

from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

# =========================================================
# ePlanet Brokers - Telegram Support Bot
# 24/7 - NO working-hours restriction
# =========================================================

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()

MANAGER_USERNAME = os.getenv("MANAGER_USERNAME", "Saghar_eplanetbrokers").lstrip("@")
REFERRAL_USERNAME = os.getenv("REFERRAL_USERNAME", "hoomaneplanetbrokers").lstrip("@")

SITE_URL = "https://my.eplanetbrokers.com/fa/auth/sign-in"
MT5_VIDEO = "https://dl.eplanetbrokers.com/tutorial/fa/connecttometa-fa.mp4"
PASSWORD_VIDEO = "https://dl.eplanetbrokers.com/tutorial/fa/n/passreco.mp4"

# ---------------- Render health server ----------------

web_app = Flask(__name__)

@web_app.get("/")
def home():
    return "ePlanet Brokers Support Bot is running 24/7.", 200

def run_web():
    port = int(os.environ.get("PORT", "10000"))
    web_app.run(host="0.0.0.0", port=port)


# ---------------- Main menu ----------------

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔐 ورود به سایت / پنل کاربری", callback_data="site")],
        [InlineKeyboardButton("💳 واریز و برداشت", callback_data="deposit")],
        [InlineKeyboardButton("📱 اتصال متاتریدر 5", callback_data="mt5")],
        [InlineKeyboardButton("🔑 تغییر / بازیابی رمز عبور", callback_data="password")],
        [InlineKeyboardButton("👤 ارتباط مستقیم با مدیر حساب", callback_data="manager")],
        [InlineKeyboardButton("🎓 سیستم کور / یاسر رضایی", callback_data="referral")],
    ])


# THIS is the first message after /start.
WELCOME_MESSAGE = """سلام و وقت بخیر 🌷

من ساغر هستم، پشتیبانی ePlanet Brokers.
به پشتیبانی ePlanet Brokers خوش آمدید 🤍

لطفاً موضوع موردنظر خود را از منوی زیر انتخاب کنید تا راهنمایی‌تان کنم 👇"""


SITE_MESSAGE = f"""با سلام و وقت بخیر 🌷

سرویسی که تحت عنوان «اینترنت ملی» در اختیار کاربران ایران قرار گرفته بود، یک امکان اضافی برای تسهیل دسترسی کاربران محسوب می‌شد. متأسفانه در حال حاضر به دلیل محدودیت‌ها و فیلترینگ اعمال‌شده، این سرویس در دسترس نیست.

لطفاً توجه داشته باشید که این موضوع به معنای اختلال یا مشکل در خدمات بروکر نیست. وب‌سایت بین‌المللی، پنل کاربری، سرورهای معاملاتی و سایر خدمات اصلی ePlanet بدون هیچ‌گونه اختلالی در حال ارائه خدمات هستند.

در حال حاضر زمان مشخصی برای بازگشت یا رفع این محدودیت وجود ندارد و در صورت ایجاد هرگونه تغییر، اطلاع‌رسانی لازم انجام خواهد شد.

در صورتی که از داخل ایران به خدمات ePlanet دسترسی دارید، لازم است برای ورود به وب‌سایت و سایر آدرس‌های بروکر از ابزار تغییر IP مناسب (فیلترشکن) استفاده فرمایید.

{SITE_URL}"""


DEPOSIT_MESSAGE = """با سلام و وقت بخیر 🌷

جهت پیگیری واریز یا برداشت، لطفاً از طریق پنل کاربری خود یک تیکت ثبت فرمایید تا درخواست شما توسط تیم مربوطه بررسی و پیگیری شود."""


MT5_MESSAGE = f"""با سلام و وقت بخیر 🌷

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


PASSWORD_MESSAGE = f"""با سلام و وقت بخیر 🌷

جهت تغییر رمز عبور حساب معاملاتی، نیازی به دریافت کد تأیید از طریق ایمیل یا ثبت تیکت پشتیبانی نمی‌باشد.

لطفاً وارد پنل کاربری خود شده و از بخش «حساب‌های من»، حساب موردنظر را انتخاب فرمایید.

سپس از طریق منوی سه‌نقطه، گزینه «تغییر رمز اصلی پلتفرم معاملاتی» را انتخاب کرده و رمز عبور جدید خود را ثبت نمایید.

🎥 ویدئوی بازیابی رمز عبور:
{PASSWORD_VIDEO}

با سپاس از همراهی شما"""


MANAGER_MESSAGE = f"""با سلام و وقت بخیر 🌷

درخواست شما جهت ارتباط مستقیم با مدیر حساب ثبت شد.

لطفاً از طریق آیدی زیر با مدیر حساب در ارتباط باشید:

https://t.me/{MANAGER_USERNAME}

در صورتی که مدیر حساب شما ساغر است، می‌توانید درخواست خود را از طریق همین آیدی پیگیری فرمایید."""


REFERRAL_MESSAGE = f"""سلام و وقت بخیر 🌷

خواهشمند است در صورتی که از دانشجویان سیستم کور و جناب آقای یاسر رضایی هستید، جهت پیگیری امور و طرح تمامی سؤالات خود فقط از طریق آیدی زیر اقدام فرمایید:

https://t.me/{REFERRAL_USERNAME}

لطفاً از ادامه مکاتبه در این صفحه خودداری نمایید. در صورت دانشجوی ایشان بودن، پاسخگویی صرفاً از طریق آیدی اعلام‌شده انجام خواهد شد.

🔴 در صورتی که در پنل کاربری شما نام «ساغر» به عنوان مدیر حساب ثبت شده است، لطفاً ایمیل ثبت‌نامی خود را ارسال فرمایید تا حساب شما مورد بررسی قرار گیرد.

لطفاً در صورتی که مدیر حساب شما ساغر نیست، ایمیل خود را ارسال نکنید.

با تشکر از همکاری شما."""


ANSWERS = {
    "site": SITE_MESSAGE,
    "deposit": DEPOSIT_MESSAGE,
    "mt5": MT5_MESSAGE,
    "password": PASSWORD_MESSAGE,
    "manager": MANAGER_MESSAGE,
    "referral": REFERRAL_MESSAGE,
}


# ---------------- /start ----------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Always show the welcome message first, then the menu.
    await update.message.reply_text(WELCOME_MESSAGE, reply_markup=main_menu())


# ---------------- Menu buttons ----------------

async def menu_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    answer = ANSWERS.get(query.data)

    if answer:
        await query.message.reply_text(answer, reply_markup=main_menu())


# ---------------- Text messages ----------------

def detect_topic(text):
    text = (text or "").lower()

    if any(x in text for x in ["سیستم کور", "یاسر رضایی", "دانشجوی یاسر", "yaser rezaei"]):
        return "referral"

    if any(x in text for x in ["مدیر حساب", "ارتباط مستقیم", "با مدیر", "مدیرم", "manager"]):
        return "manager"

    if any(x in text for x in ["واریز", "برداشت", "deposit", "withdraw"]):
        return "deposit"

    if any(x in text for x in ["متاتریدر", "متا تریدر", "mt5", "mt 5"]):
        return "mt5"

    if any(x in text for x in ["رمز", "پسورد", "password", "بازیابی رمز", "تغییر رمز"]):
        return "password"

    if any(x in text for x in ["سایت", "وب سایت", "وبسایت", "پنل", "ورود", "لاگین", "login", "فیلترشکن", "اینترنت ملی"]):
        return "site"

    return None


async def text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = detect_topic(update.message.text)

    if topic:
        await update.message.reply_text(ANSWERS[topic], reply_markup=main_menu())
    else:
        await update.message.reply_text(
            "لطفاً موضوع موردنظر خود را از منوی زیر انتخاب کنید 👇",
            reply_markup=main_menu()
        )


# ---------------- Start bot ----------------

def run_bot():
    if not TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is missing in Render Environment Variables.")

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(menu_button))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, text_message)
    )

    # Polling runs continuously. There is NO time check anywhere in this file.
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    run_bot()
