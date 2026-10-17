"""
Campus Connect - Local SQLite Persistence Layer
Stores notices, revisions, exam timetables, and notification audit logs locally in notice_intel.db.
Requires zero external database setup.
"""

import sqlite3
import os
import json
import re
from typing import List, Dict, Any, Optional
from sample_data import SAMPLE_NOTICES, SAMPLE_EXAMS, SAMPLE_NOTIFICATIONS

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notice_intel.db")


def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(reset: bool = False):
    """Initializes tables and seeds with sample demo data if empty or reset requested."""
    conn = get_db_connection()
    cur = conn.cursor()

    if reset:
        cur.execute("DROP TABLE IF EXISTS notices")
        cur.execute("DROP TABLE IF EXISTS exams")
        cur.execute("DROP TABLE IF EXISTS notifications")

    # Notices table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS notices (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            reference_code TEXT,
            version INTEGER DEFAULT 1,
            is_revision BOOLEAN DEFAULT 0,
            parent_notice_id TEXT,
            department TEXT,
            category TEXT,
            issue_date TEXT,
            date TEXT,
            start_time TEXT,
            end_time TEXT,
            venue TEXT,
            raw_text TEXT,
            status TEXT DEFAULT 'ACTIVE',
            is_sample BOOLEAN DEFAULT 1,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Migration for existing SQLite database file if issue_date column does not exist yet
    try:
        cur.execute("ALTER TABLE notices ADD COLUMN issue_date TEXT")
    except sqlite3.OperationalError:
        pass

    # Exams table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS exams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_code TEXT NOT NULL,
            course_title TEXT NOT NULL,
            exam_type TEXT,
            department TEXT,
            date TEXT,
            start_time TEXT,
            end_time TEXT,
            venue TEXT,
            invigilator TEXT,
            total_students INTEGER,
            status TEXT DEFAULT 'CONFIRMED',
            conflict_flag BOOLEAN DEFAULT 0,
            conflict_reason TEXT,
            is_sample BOOLEAN DEFAULT 1
        )
    """)

    # Notifications table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id TEXT PRIMARY KEY,
            type TEXT,
            title TEXT,
            message TEXT,
            timestamp TEXT,
            read BOOLEAN DEFAULT 0,
            action_url TEXT,
            is_sample BOOLEAN DEFAULT 0
        )
    """)

    # Migration for existing SQLite database file if is_sample column does not exist yet
    try:
        cur.execute("ALTER TABLE notifications ADD COLUMN is_sample BOOLEAN DEFAULT 0")
    except sqlite3.OperationalError:
        pass

    # Ensure known demo notifications are tagged as is_sample = 1
    cur.execute("UPDATE notifications SET is_sample = 1 WHERE id IN ('NOTIF-01', 'NOTIF-02', 'NOTIF-03')")
    conn.commit()

    # Seed initial demo notices if table is empty
    cur.execute("SELECT COUNT(*) FROM notices")
    if cur.fetchone()[0] == 0:
        for n in SAMPLE_NOTICES:
            cur.execute("""
                INSERT INTO notices (
                    id, title, reference_code, version, is_revision, parent_notice_id,
                    department, category, issue_date, date, start_time, end_time, venue, raw_text,
                    status, is_sample, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                n["id"], n["title"], n["reference_code"], n["version"],
                1 if n["is_revision"] else 0, n["parent_notice_id"],
                n["department"], n["category"], n.get("issue_date", "[Not Specified]"),
                n["date"], n["start_time"],
                n["end_time"], n["venue"], n["raw_text"], n["status"],
                1 if n.get("is_sample", True) else 0, n.get("notes", "")
            ))

        for ex in SAMPLE_EXAMS:
            cur.execute("""
                INSERT INTO exams (
                    course_code, course_title, exam_type, department, date,
                    start_time, end_time, venue, invigilator, total_students,
                    status, conflict_flag, conflict_reason, is_sample
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ex["course_code"], ex["course_title"], ex["exam_type"],
                ex["department"], ex["date"], ex["start_time"], ex["end_time"],
                ex["venue"], ex["invigilator"], ex["total_students"],
                ex["status"], 1 if ex["conflict_flag"] else 0,
                ex["conflict_reason"], 1
            ))

        for notif in SAMPLE_NOTIFICATIONS:
            cur.execute("""
                INSERT OR REPLACE INTO notifications (id, type, title, message, timestamp, read, action_url, is_sample)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                notif["id"], notif["type"], notif["title"], notif["message"],
                notif["timestamp"], 1 if notif["read"] else 0, notif["action_url"],
                1 if notif.get("is_sample", True) else 0
            ))

        conn.commit()

    conn.close()


def get_all_notices() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM notices ORDER BY date ASC, created_at DESC")
    rows = [dict(r) for r in cur.fetchall()]
    # Normalize booleans
    for r in rows:
        r["is_revision"] = bool(r["is_revision"])
        r["is_sample"] = bool(r["is_sample"])
    conn.close()
    return rows


def get_notice_by_id(notice_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM notices WHERE id = ?", (notice_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        d = dict(row)
        d["is_revision"] = bool(d["is_revision"])
        d["is_sample"] = bool(d["is_sample"])
        return d
    return None


def find_matching_parent_notice(parent_ref_hint: Optional[str]) -> Optional[Dict[str, Any]]:
    """
    Matches an extracted parent notice reference code or ID against existing notices in SQLite.
    Never invents an ID or fabricates a match. Returns None if no valid match exists.
    """
    if not parent_ref_hint:
        return None

    cleaned_hint = str(parent_ref_hint).strip()
    if not cleaned_hint or cleaned_hint.lower() in ("none", "[not specified]", "[unknown]", "null", "n/a", ""):
        return None

    conn = get_db_connection()
    cur = conn.cursor()

    # 1. Exact match on reference_code or id (case-insensitive)
    cur.execute("""
        SELECT * FROM notices 
        WHERE LOWER(reference_code) = LOWER(?) OR LOWER(id) = LOWER(?)
        LIMIT 1
    """, (cleaned_hint, cleaned_hint))
    row = cur.fetchone()
    if row:
        d = dict(row)
        d["is_revision"] = bool(d["is_revision"])
        d["is_sample"] = bool(d["is_sample"])
        conn.close()
        return d

    # 2. Normalized match (punctuation and whitespace agnostic, e.g. 'CSE/EXAM/2026/01' vs 'CSE-EXAM-2026-01')
    def normalize_code(val: Optional[str]) -> str:
        if not val:
            return ""
        return re.sub(r'[^A-Za-z0-9]', '', str(val)).upper()

    norm_hint = normalize_code(cleaned_hint)
    if norm_hint:
        cur.execute("SELECT * FROM notices")
        all_rows = cur.fetchall()
        for r in all_rows:
            r_ref = normalize_code(r["reference_code"])
            r_id = normalize_code(r["id"])
            if (norm_hint == r_ref and r_ref) or (norm_hint == r_id and r_id):
                d = dict(r)
                d["is_revision"] = bool(d["is_revision"])
                d["is_sample"] = bool(d["is_sample"])
                conn.close()
                return d

    conn.close()
    return None


def add_notice(data: Dict[str, Any]) -> str:
    """Inserts a new notice into the database."""
    conn = get_db_connection()
    cur = conn.cursor()

    notice_id = data.get("id")
    if not notice_id:
        cur.execute("SELECT COUNT(*) FROM notices")
        count = cur.fetchone()[0] + 1
        notice_id = f"NOT-2026-{count:03d}"

    # If this notice is a revision of an existing notice, mark parent as SUPERSEDED
    parent_id = data.get("parent_notice_id")
    if parent_id:
        cur.execute("UPDATE notices SET status = 'SUPERSEDED' WHERE id = ?", (parent_id,))

    cur.execute("""
        INSERT INTO notices (
            id, title, reference_code, version, is_revision, parent_notice_id,
            department, category, issue_date, date, start_time, end_time, venue, raw_text,
            status, is_sample, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        notice_id,
        data.get("title", "Untitled Notice"),
        data.get("reference_code", "UNASSIGNED"),
        data.get("version", 1),
        1 if data.get("is_revision", False) else 0,
        parent_id,
        data.get("department", "Central Academic Administration"),
        data.get("category", "General Notice"),
        data.get("issue_date", "[Not Specified]"),
        data.get("date", "2026-10-24"),
        data.get("start_time", "10:00"),
        data.get("end_time", "12:00"),
        data.get("venue", "Campus-Wide"),
        data.get("raw_text", ""),
        data.get("status", "ACTIVE"),
        1 if data.get("is_sample", False) else 0,
        data.get("notes", "User uploaded notice")
    ))

    # Add notification about new upload / revision
    notif_id = f"NOTIF-{notice_id}"
    n_type = "REVISION_ALERT" if data.get("is_revision") else "NOTICE_ADDED"
    n_title = f"{'Revised Notice Added' if data.get('is_revision') else 'New Academic Notice'}: {data.get('title')[:35]}"
    n_msg = f"Notice Ref: {data.get('reference_code')} uploaded for {data.get('date')} at {data.get('venue')}."
    cur.execute("""
        INSERT OR REPLACE INTO notifications (id, type, title, message, timestamp, read, action_url, is_sample)
        VALUES (?, ?, ?, ?, datetime('now', 'localtime'), 0, 'notices', ?)
    """, (notif_id, n_type, n_title, n_msg, 1 if data.get("is_sample") else 0))

    conn.commit()
    conn.close()
    return notice_id


def get_all_exams() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM exams ORDER BY date ASC, start_time ASC")
    rows = [dict(r) for r in cur.fetchall()]
    for r in rows:
        r["conflict_flag"] = bool(r["conflict_flag"])
        r["is_sample"] = bool(r["is_sample"])
    conn.close()
    return rows


def add_exam(data: Dict[str, Any]):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO exams (
            course_code, course_title, exam_type, department, date,
            start_time, end_time, venue, invigilator, total_students,
            status, conflict_flag, conflict_reason, is_sample
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("course_code"), data.get("course_title"), data.get("exam_type", "Midterm"),
        data.get("department"), data.get("date"), data.get("start_time"), data.get("end_time"),
        data.get("venue"), data.get("invigilator", "TBD"), data.get("total_students", 60),
        data.get("status", "CONFIRMED"), 1 if data.get("conflict_flag") else 0,
        data.get("conflict_reason", "None"), 0
    ))
    conn.commit()
    conn.close()


def get_notifications() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM notifications ORDER BY timestamp DESC")
    rows = [dict(r) for r in cur.fetchall()]
    for r in rows:
        r["read"] = bool(r["read"])
        r["is_sample"] = bool(r.get("is_sample", 0))
    conn.close()
    return rows


def mark_notification_read(notif_id: str):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE notifications SET read = 1 WHERE id = ?", (notif_id,))
    conn.commit()
    conn.close()


def mark_notification_unread(notif_id: str):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE notifications SET read = 0 WHERE id = ?", (notif_id,))
    conn.commit()
    conn.close()


def delete_notification(notif_id: str):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM notifications WHERE id = ?", (notif_id,))
    conn.commit()
    conn.close()


def mark_all_notifications_read():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE notifications SET read = 1")
    conn.commit()
    conn.close()


def sync_conflict_notifications(conflicts: List[Dict[str, Any]]):
    """
    Synchronizes conflict notifications in SQLite based on detected timeline clashes.
    If the conflict involves real (non-sample) notices, it is recorded as a real event (is_sample=0).
    If it involves sample notices, it is tagged as demonstration data (is_sample=1).
    """
    if not conflicts:
        return
    conn = get_db_connection()
    cur = conn.cursor()
    for c in conflicts:
        notif_id = f"NOTIF-CONF-{c['id']}"
        ev_a = c.get("event_a", {})
        ev_b = c.get("event_b", {})
        is_sample = bool(ev_a.get("is_sample") or ev_b.get("is_sample"))
        cur.execute("SELECT COUNT(*) FROM notifications WHERE id = ?", (notif_id,))
        if cur.fetchone()[0] == 0:
            cur.execute("""
                INSERT INTO notifications (id, type, title, message, timestamp, read, action_url, is_sample)
                VALUES (?, 'CRITICAL_CONFLICT', ?, ?, datetime('now', 'localtime'), 0, 'conflicts', ?)
            """, (
                notif_id,
                f"Schedule Clash: {c['type'].replace('_', ' ')} on {c.get('date', '')}",
                c.get("explanation", "Schedule collision detected."),
                1 if is_sample else 0
            ))
    conn.commit()
    conn.close()


def get_database_stats() -> Dict[str, Any]:
    """Returns verified counts of real vs sample records in SQLite without inventing data."""
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*), SUM(CASE WHEN is_sample = 1 THEN 1 ELSE 0 END) FROM notices")
    row_n = cur.fetchone()
    total_notices = row_n[0] or 0
    sample_notices = row_n[1] or 0
    real_notices = total_notices - sample_notices

    cur.execute("SELECT COUNT(*), SUM(CASE WHEN is_sample = 1 THEN 1 ELSE 0 END) FROM exams")
    row_e = cur.fetchone()
    total_exams = row_e[0] or 0
    sample_exams = row_e[1] or 0
    real_exams = total_exams - sample_exams

    cur.execute("SELECT COUNT(*), SUM(CASE WHEN is_sample = 1 THEN 1 ELSE 0 END), SUM(CASE WHEN read = 0 THEN 1 ELSE 0 END) FROM notifications")
    row_notif = cur.fetchone()
    total_notifs = row_notif[0] or 0
    sample_notifs = row_notif[1] or 0
    real_notifs = total_notifs - sample_notifs
    unread_notifs = row_notif[2] or 0

    conn.close()
    return {
        "total_notices": total_notices,
        "real_notices": real_notices,
        "sample_notices": sample_notices,
        "total_exams": total_exams,
        "real_exams": real_exams,
        "sample_exams": sample_exams,
        "total_notifications": total_notifs,
        "real_notifications": real_notifs,
        "sample_notifications": sample_notifs,
        "unread_notifications": unread_notifs,
        "has_demo_data": bool(sample_notices > 0 or sample_exams > 0 or sample_notifs > 0)
    }


def reset_to_demo_data():
    """Resets the database entirely to initial realistic demo dataset."""
    init_db(reset=True)
