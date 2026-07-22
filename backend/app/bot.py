import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]

MINI_APP_URL = "https://bar-buddy-hzs5.vercel.app"
GITHUB_URL = "https://github.com/7SUNNY77/BarBuddy"
WEBSITE_URL = "https://bar-buddy-hzs5.vercel.app"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_name = update.effective_user.first_name or "друг"

    text = (
        f"🍸 <b>Привет, {user_name}!</b>\n\n"
        "Добро пожаловать в <b>BarBuddy</b> — твой гид по классическим коктейлям.\n\n"
        "Опиши настроение, вкус или ингредиент — и сервис подберёт подходящие варианты."
    )

    keyboard = [
        [
            InlineKeyboardButton(
                text="Открыть BarBuddy 🍸",
                web_app=WebAppInfo(url=MINI_APP_URL),
            )
        ],
        [
            InlineKeyboardButton(
                text="Открыть сайт 🌐",
                url=WEBSITE_URL,
            ),
            InlineKeyboardButton(
                text="GitHub 🐙",
                url=GITHUB_URL,
            ),
        ],
    ]

    await update.message.reply_text(
        text=text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()