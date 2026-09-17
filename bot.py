
import os
import re
import threading
from datetime import datetime
from zoneinfo import ZoneInfo

from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
MANAGER_USERNAME = os.environ.get("MANAGER_USERNAME", "Saghar_eplanetbrokers")
REFERRAL_USERNAME = os.environ.get("REFERRAL_USERNAME", "hoomaneplanetbrokers")

SITE_URL = "https://my.eplanetbrokers.com/fa/auth/sign-in"
MT5_VIDEO = "https://dl.eplanetbrokers.com/tutorial/fa/connecttometa-fa.mp4"
PASSWORD_VIDEO = "https://dl.eplanetbrokers.com/tutorial/fa/n/passreco.mp4"

app_web = Flask(__name__)

@app_web.get("/")
def health():
    return "ePlanet Telegram Bot is running."

def in_working_hours():
    now = datetime.now(ZoneInfo("Europe/Istanbul"))
    t = now.hour * 60 + now.minute
    return 10 * 60 + 30 <= t < 19 * 60

def normalize(text):
    return re.sub(r"\s+", " ", text.lower().strip())

def classify(text):
    t = normalize(text)

    if any(x in t for x in ["یاسر رضایی", "رضایی", "سیستم کور", "دانشجوی یاسر"]):
        return "referral"
    if any(x in t for x in ["با مدیر حساب", "صحبت با مدیر", "مدیر حساب", "ساغر",
                             "اپراتور", "کارشناس حساب", "مستقیم صحبت", "چت با مدیر"]):
        return "manager"
    if any(x in t for x in ["واریز", "برداشت", "پیگیری واریز", "پیگیری برداشت",
                             "واریزم", "برداشتم", "پولم نیومده"]):
        return "deposit_withdrawal"
    if any(x in t for x in ["متاتریدر", "متا تریدر", "mt5", "اتصال به متا",
                             "متا وصل", "حسابم به متا"]):
        return "mt5"
    if any(x in t for x in ["رمز", "پسورد", "password", "رمز عبور",
                             "بازیابی رمز", "تغییر رمز"]):
        return "password"
    if any(x in t for x in ["سایت", "وب سایت", "وب‌سایت", "ورود", "باز نمیشه",
                             "باز نمی شه", "فیلتر", "فیلترینگ", "دسترسی"]):
        return "site"
    return "unknown"

RESPONSES = {
"referral": f"""سلام و وقت بخیر

خواهشمند است در صورتی که از دانشجویان سیستم کور و جناب آقای یاسر رضایی هستید، جهت پیگیری امور و طرح تمامی سؤالات خود فقط از طریق آیدی زیر اقدام فرمایید:
t.me/{REFERRAL_USERNAME}

لطفاً از ادامه مکاتبه در این صفحه خودداری نمایید. در صورت دانشجوی ایشان بودن، پاسخگویی صرفاً از طریق آیدی اعلام‌شده انجام خواهد شد.

🔴 در صورتی که در پنل کاربری شما نام «ساغر» به عنوان مدیر حساب ثبت شده است، لطفاً ایمیل ثبت‌نامی خود را ارسال فرمایید تا حساب شما مورد بررسی قرار گیرد.

لطفاً در صورتی که مدیر حساب شما ساغر نیست، ایمیل خود را ارسال نکنید.

با تشکر از همکاری شما.""",

"deposit_withdrawal": """با سلام و وقت بخیر

جهت پیگیری واریز یا برداشت، لطفاً از طریق پنل کاربری خود یک تیکت ثبت فرمایید تا درخواست شما توسط تیم مربوطه بررسی و پیگیری شود.

لطفاً درخواست مربوط به واریز یا برداشت خود را از طریق تیکت پنل کاربری ثبت کنید.""",

"mt5": f"""با سلام و وقت بخیر

جهت اتصال حساب معاملاتی خود به MetaTrader 5، پس از دانلود، نصب و راه‌اندازی متاتریدر ۵:

1. از منوی File گزینه Open an Account را انتخاب نمایید.
2. در نوار جستجو عبارت ePlanet Brokers را وارد کرده و روی Find Your Company کلیک کنید.
3. ePlanet Brokers را انتخاب کرده و روی Next کلیک نمایید.
4. در پنجره جدید، آخرین گزینه را انتخاب کنید.
5. در قسمت Login شماره حساب و در قسمت Password رمز عبوری که از طریق ایمیل دریافت کرده‌اید را وارد نمایید.
6. اطمینان حاصل کنید که سرور انتخاب‌شده ePlanet Brokers باشد.
7. در پایان روی Finish کلیک کنید.

🎥 آموزش تصویری:
{MT5_VIDEO}""",

"password": f"""با سلام و وقت بخیر،

جهت تغییر رمز عبور حساب معاملاتی، نیازی به دریافت کد تأیید از طریق ایمیل یا ثبت تیکت پشتیبانی نمی‌باشد.

لطفاً وارد پنل کاربری خود شده و از بخش «حساب‌های من»، حساب موردنظر را انتخاب فرمایید.

سپس از طریق منوی سه‌نقطه، گزینه «تغییر رمز اصلی پلتفرم معاملاتی» را انتخاب کرده و رمز عبور جدید خود را ثبت نمایید.

🎥 آموزش تصویری بازیابی رمز عبور:
{PASSWORD_VIDEO}

در صورت نیاز به راهنمایی بیشتر، با کمال میل در خدمت شما خواهیم بود.""",

"site": f"""با سلام

سرویسی که تحت عنوان «اینترنت ملی» در اختیار کاربران ایران قرار گرفته بود، یک امکان اضافی برای تسهیل دسترسی کاربران محسوب می‌شد. متأسفانه در حال حاضر به دلیل محدودیت‌ها و فیلترینگ اعمال‌شده، این سرویس در دسترس نیست.

لطفاً توجه داشته باشید که این موضوع به معنای اختلال یا مشکل در خدمات بروکر نیست. وب‌سایت بین‌المللی، پنل کاربری، سرورهای معاملاتی و سایر خدمات اصلی ePlanet بدون هیچ‌گونه اختلالی در حال ارائه خدمات هستند.

در حال حاضر زمان مشخصی برای بازگشت یا رفع این محدودیت وجود ندارد و در صورت ایجاد هرگونه تغییر، اطلاع‌رسانی لازم انجام خواهد شد.

در صورتی که از داخل ایران به خدمات ePlanet دسترسی دارید، لازم است برای ورود به وب‌سایت و سایر آدرس‌های بروکر از ابزار تغییر IP مناسب (فیلترشکن) استفاده فرمایید.

🔗 لینک ورود:
{SITE_URL}""",

"manager": f"""با سلام و وقت بخیر

درخواست شما جهت ارتباط مستقیم با مدیر حساب ثبت شد.

لطفاً از طریق آیدی زیر با مدیر حساب در ارتباط باشید:
t.me/{MANAGER_USERNAME}

در صورتی که مدیر حساب شما ساغر است، می‌توانید درخواست خود را از طریق همین آیدی پیگیری فرمایید."""
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام و وقت بخیر 🌷\n\n"
        "به پشتیبانی ePlanet خوش آمدید.\n"
        "سؤال خود را ارسال فرمایید تا راهنمایی لازم ارائه شود."
    )

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    if not in_working_hours():
        await update.message.reply_text(
            "با سلام و وقت بخیر\n\n"
            "ساعات پاسخگویی مدیر حساب از ۱۰:۳۰ صبح تا ۷:۰۰ عصر می‌باشد.\n"
            "لطفاً درخواست خود را ارسال فرمایید تا در ساعات پاسخگویی پیگیری شود."
        )
        return

    kind = classify(update.message.text)
    if kind == "unknown":
        await update.message.reply_text(
            f"با سلام و وقت بخیر\n\n"
            f"برای راهنمایی دقیق‌تر، لطفاً درخواست خود را با جزئیات بیشتری ارسال فرمایید.\n\n"
            f"در صورت نیاز به صحبت مستقیم با مدیر حساب:\n"
            f"t.me/{MANAGER_USERNAME}"
        )
    else:
        await update.message.reply_text(RESPONSES[kind])

def run_bot():
    if not TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN environment variable is missing.")
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    application.run_polling()

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", "10000"))
    app_web.run(host="0.0.0.0", port=port)
