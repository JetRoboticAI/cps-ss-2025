# -*- coding: utf-8 -*-
"""
@Author: Jieying Li
@Created Date: 2025-05-28 14:34:07
@Path: /telegram_notifier.py
"""

import asyncio
import time

from telegram import InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from config import CHAT_ID
from medication_logger import get_logs_for_today, log_medication


def queue_msg(queue, msg, buttons=None):
    """
    Queue medication information for sending to Telegram.
    """
    print(f"Queuing: {msg}, Buttons: {buttons}")
    queue.append((msg, buttons))
    print(f"Queue size: {len(queue)}")
    time.sleep(1)


def process_message_queue(bot, queue, loop):
    """
    Continuously check the queue and send messages using asyncio-safe method.
    """
    print("🟢 process_message_queue started.")
    while True:
        if queue:
            item = queue.pop(0)
            coroutine = _send_message(bot, msg=item[0], buttons=item[1])
            asyncio.run_coroutine_threadsafe(coroutine, loop)
        else:
            time.sleep(1)

async def _send_message(bot, msg, buttons=None):
    """
    Async message sender for Telegram.
    """

    try:
        print("📤 Sending Telegram message...")
        print(f"Message content: {msg}")
        print(f"Buttons: {buttons}, len(buttons): {len(buttons) if buttons else 'None'}")
        await bot.send_message(
            chat_id=CHAT_ID,
            text=msg,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(buttons) if buttons else None
        )
    except Exception as e:
        print("Error sending message:", e)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle button callbacks for taken/skipped actions.
    """
    query = update.callback_query
    await query.answer()
    print("🔘 Callback received:", query.data)
    action, tag_id = query.data.split(":")
    print(f"🔘 Button pressed: {action} for tag {tag_id}")
    log_medication(tag_id, action)
    await query.edit_message_text(f"✅ Recorded as *{action}*.")
