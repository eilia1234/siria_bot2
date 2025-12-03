import json
import os
from openai import OpenAI
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import logging

# --------------------------
#     تنظیمات اصلی ربات
# --------------------------

TELEGRAM_TOKEN = "8253257734:AAFFtECXkhDoayg__lK0WUDhXEAoLkZb-kQ"

avalai_client = OpenAI(
    api_key="aa-zP3PwtNN9oFKBmS3tkzhvU4mmNKVK00DijpkBMkU6e2dhJf8",
    base_url="https://api.avalai.ir/v1"
)

MEMORY_FILE = "siria_memory.json"

if os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "r", encoding="utf8") as f:
        user_memory = json.load(f)
else:
    user_memory = {}

# --------------------------
#    هندل دستور /start
# --------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! من سیریا هستم، دستیار هوشمند فروشگاه اسپرت کالا. 😊\n"
        "می‌تونی هر محصولی رو که میخوای بهم بگی و من برات تحلیل می‌کنم."
    )

# --------------------------
#      هندل پیام چت
# --------------------------
async def siriabot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    message = update.message.text.strip()

    print("پیام جدید رسید:", message)

    if user_id not in user_memory:
        user_memory[user_id] = []

    history = user_memory[user_id]

    system_prompt = {
        "role": "system",
        "content": (
            "تو دستیار هوشمند فروشگاه اسپرت کالا هستی به نام سیریا. "
            "همیشه با لحن دوستانه، دقیق و فارسی طبیعی پاسخ بده. "
            "هدف تو توضیح و تجزیه و تحلیل محصولی که کاربر نام یا کد آن را وارد می‌کند است. "
            "تو نباید اطلاعات آن محصول را کپی و برای کاربر ارسال کنی بلکه باید آن را تحلیل کنی. "
            "هیچ وقت خودت را ChatGPT معرفی نکن و همیشه خودت را سیریا بدان. "
            "تو باید برنامه نویسی هم انجام بدی. "
            "تو توسط ایلیا ساخته شدی و همیشه به نفع اسپرت کالا پاسخ می‌دهی."
        )
    }

    messages = [system_prompt] + history[-20:]
    messages.append({"role": "user", "content": message})

    # --------------------------
    #      نمایش لودر هنگام پاسخ‌دهی
    # --------------------------
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    # --------------------------
    #     تماس با AvalAI
    # --------------------------
    try:
        completion = avalai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7
        )
        reply = completion.choices[0].message.content.strip()
    except Exception as e:
        print("خطا در تماس با AvalAI:", e)
        reply = "مشکلی در ارتباط با سرور پیش آمد 😥"

    # ذخیره در حافظه
    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": reply})
    user_memory[user_id] = history[-50:]

    with open(MEMORY_FILE, "w", encoding="utf8") as f:
        json.dump(user_memory, f, ensure_ascii=False, indent=2)

    await update.message.reply_text(reply)

# --------------------------
#       اجرای ربات
# --------------------------
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("ربات سیریا روشن شد")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # هندل دستور /start
    app.add_handler(CommandHandler("start", start))
    # هندل پیام‌های متنی
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, siriabot))

    app.run_polling()
