# -*- coding: utf-8 -*-
"""
@Author: Jieying Li
@Created Date: 2025-05-27 21:58:46
@Path: /medication_logger.py
"""

import sqlite3
from datetime import datetime

from medication_db import DB_FILE


def log_medication(tag_id: str, action: str):
    """
    Log medication intake or action into the database.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO logs (tag_id, action, timestamp)
        VALUES (?, ?, ?)
    """, (tag_id, action, timestamp))
    conn.commit()
    conn.close()


def get_logs_for_today(tag_id: str):
    """
    Retrieve logs for the current day for a specific medication.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("""
        SELECT * FROM logs
        WHERE tag_id = ? AND DATE(timestamp) = ?
    """, (tag_id, today))
    logs = cursor.fetchall()
    conn.close()
    return logs