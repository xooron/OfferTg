from telegram import Update, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
import re

# Регулярное выражение для команды /gift
PATTERN = r"/gift\s+(https?://[^ ]+)\s+(\d+)\s*⭐️"

async def gift_handler(update: Update):
    # Проверяем формат сообщения
    match = re.match(PATTERN, update.message.text)
    
    if not match:
        await update.message.reply_text("Ошибка: неверный формат команды.")
        return
    
    link, number = match.groups()
    
    # Формируем финальное сообщение
    final_message = f"Пользователь @xooron предлагает Вам {number} ⭐️ за коллекционный предмет {link}\n• Предложение действует еще 5ч. 59 мин."
    
    # Удаляем исходное сообщение
    await update.message.delete()
    
    # Отправляем новое сообщение
    await update.effective_chat.send_message(final_message)

def main():
    # Токен вашего бота из @BotFather
    os.getenv("TELEGRAM_TOKEN")

    application = ApplicationBuilder().token(TOKEN).build()

    # Добавляем обработчик команд
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, gift_handler))

    # Устанавливаем описание команды
    application.bot.set_my_commands([BotCommand("/gift", "Отправить предложение обмена")])

    # Запускаем бот
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
