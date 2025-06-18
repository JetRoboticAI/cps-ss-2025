# -*- coding: utf-8 -*-
"""
@Author: Jieying Li
@Created Date: 2025-05-28 16:10:07
@Path: /telegram_bot_server.py
@Purpose: Start a Telegram Bot server that handles medication button interactions
"""


import asyncio
import threading

from telegram.ext import ApplicationBuilder, CallbackQueryHandler

from config import BOT_TOKEN
from telegram_notifier import handle_callback, process_message_queue

message_queue = []

def start_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CallbackQueryHandler(handle_callback))

    loop = asyncio.get_event_loop()

    threading.Thread(
        target=process_message_queue,
        args=(app.bot, message_queue, loop),
        daemon=True
    ).start()

    print("✅ Telegram bot is running...")
    app.run_polling()