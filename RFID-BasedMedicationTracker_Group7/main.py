# -*- coding: utf-8 -*-
"""
@Author: Jieying Li
@Created Date: 2025-05-28
@Path: /main.py
@Purpose: Unified entry point: RFID + Telegram Bot + Scheduled Reminders
"""

import threading

from telegram import InlineKeyboardButton

from medication_db import get_medication_info, init_db
from medication_scheduler import (has_taken_this_hour, is_time_to_take,
                                  run_scheduler)
from rfid_reader import read_rfid
from telegram_bot_server import message_queue, start_bot
from telegram_notifier import queue_msg


def handle_rfid():
    while True:
        tag_id = read_rfid()
        if not tag_id:
            continue
        print(f"RFID Tag ID: {tag_id}")
        med = get_medication_info(tag_id)
        print(f"Medication info: {med}")
        if not med:
            continue
        name, desc, usage, dosage, scheduler_str = med
        msg = f"💊 *{name}*\n_{desc}_\n\nUsage: {usage}\nDosage: {dosage}"
        queue_msg(message_queue, msg)
        if is_time_to_take(scheduler_str) and not has_taken_this_hour(tag_id):
            msg = f"Did you take your medication: {name} ({usage})?"
            buttons = [[
                InlineKeyboardButton("✅ Taken", callback_data=f"taken:{tag_id}"),
                InlineKeyboardButton("❌ Skipped", callback_data=f"skipped:{tag_id}")
            ]]
            queue_msg(message_queue, msg, buttons)
        else:
            print(f"Not time to take {name} yet.")
        

def main():
    init_db()
    threading.Thread(target=handle_rfid, daemon=True).start()
    threading.Thread(target=run_scheduler, daemon=True).start()
    start_bot()

if __name__ == "__main__":
    main()
