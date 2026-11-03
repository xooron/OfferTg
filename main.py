import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, BotCommand
import re
import os
from starlette.applications import Starlette
from starlette.responses import Response, PlainTextResponse
from starlette.routing import Route
import uvicorn


# Регулярное выражение для команды /gift
PATTERN = r"/gift\s+(https?://[^ ]+)\s+(\d+)\s*⭐️"

async def gift_handler(update: Update):
    match = re.match(PATTERN, update.message.text)
    
    if not match:
        await update.message.reply_text("Ошибка: неверный формат команды.")
        return
    
    link, number = match.groups()
    
    final_message = f"Пользователь @xooron предлагает Вам {number} ⭐️ за коллекционный предмет {link}\n• Предложение действует еще 5ч. 59 мин."
    
    # Отправляем новое сообщение без удаления старого (на Render это может вызвать ошибку)
    await update.effective_chat.send_message(final_message)

def main():
    TOKEN = os.getenv("TELEGRAM_TOKEN")  # Токен берётся из переменных окружения!

    application = (
        ApplicationBuilder().token(TOKEN).updater(None)  # Убираем Updater для Webhook
        .build()
    )

    # Добавляем обработчик команд
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, gift_handler))

    # Устанавливаем описание команды
    application.bot.set_my_commands([BotCommand("/gift", "Отправить предложение обмена")])

    # URL для вебхука
    url = os.getenv('RENDER_EXTERNAL_URL') + '/telegram'

    # Настраиваем вебхук
    asyncio.run(application.bot.set_webhook(url=url, allowed_updates=Update.ALL_TYPES))

    # Обработчики запросов от Telegram и healthcheck'ов Render
    async def telegram(request):
        data = await request.json()
        update = Update.de_json(data=data, bot=application.bot)
        await application.update_queue.put(update)
        return Response()

    async def health(_: Request):
        return PlainTextResponse(content="I'm alive")

    app = Starlette(
        routes=[
            Route('/telegram', telegram, methods=['POST']),
            Route('/healthcheck', health, methods=['GET'])
        ]
    )

    config = uvicorn.Config(app=app, host='0.0.0.0', port=int(os.getenv('PORT', '8000')))
    server = uvicorn.Server(config=config)

    # Запуск сервера
    with application:
        server.run()

if __name__ == "__main__":
    main()
