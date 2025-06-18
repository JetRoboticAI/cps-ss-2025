# -*- coding: utf-8 -*-
"""
@Author: Jieying Li
@Created Date: 2025-05-28 15:16:50
@Path: /medication_scheduler.py
"""


import sqlite3
import time
from datetime import datetime

import schedule

from medication_logger import get_logs_for_today
from telegram_bot_server import message_queue
from telegram_notifier import queue_msg

DB_NAME = "medication_tracker.db"

def has_taken_this_hour(tag_id):
    """
    Check if the medication has already been logged during the current hour today.
    """
    logs = get_logs_for_today(tag_id)
    print(f"Logs for today for {tag_id}: {logs}")
    current_hour = datetime.now().hour
    for log in logs:
        log_hour = datetime.fromisoformat(log[4]).hour
        if log_hour == current_hour:
            return True
    return False

def is_time_to_take(schedule):
    """
    Check if it's time to take the medication based on schedule string.
    """
    now_hour = datetime.now().hour
    hours = [int(h.strip()) for h in schedule.split(",") if h.strip().isdigit()]
    print(f"Current hour: {now_hour}, Scheduled hours: {hours}")
    return now_hour in hours

def get_all_medications():
    """
    Fetch all medications with their schedule from the database.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT tag_id, name, description, usage, dosage, schedule FROM medications")
    rows = cursor.fetchall()
    conn.close()
    return rows

def check_and_remind():
    medications = get_all_medications()
    for tag_id, name, _, usage, _, schedule_str in medications:
        if not schedule_str:
            continue
        try:
            should_take = is_time_to_take(schedule_str) and not has_taken_this_hour(tag_id)
            if should_take:
                msg = f"⏰ Time to take your medication: {name} ({usage})"
                queue_msg(message_queue, msg)
        except ValueError:
            print(f"Invalid schedule format for {name}: {schedule_str}")

def run_scheduler():
    schedule.every(10).minutes.do(check_and_remind)
    print("Scheduler started with `schedule` module. Press Ctrl+C to stop.")
    while True:
        schedule.run_pending()
        time.sleep(1)
