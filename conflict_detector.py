"""
Campus Connect - Algorithmic Schedule Conflict & Overlap Detection Engine
Detects:
1. Venue Clashes (physical room collision during overlapping hours)
2. Department / Cohort Clashes (simultaneous mandatory sessions for same department)
3. Holiday & University Recess Collisions
"""

from typing import List, Dict, Any, Optional, Tuple
import datetime


def time_to_minutes(time_str: str) -> Optional[int]:
    """Converts 'HH:MM' 24-hr time to minutes since midnight. Returns None if invalid or not specified."""
    if not time_str or "not specified" in time_str.lower() or "unknown" in time_str.lower():
        return None
    try:
        parts = time_str.strip().split(':')
        h, m = int(parts[0]), int(parts[1])
        if 0 <= h <= 23 and 0 <= m <= 59:
            return h * 60 + m
        return None
    except Exception:
        return None


def minutes_to_time(mins: int) -> str:
    """Converts minutes since midnight back to 'HH:MM' string."""
    h = mins // 60
    m = mins % 60
    return f"{h:02d}:{m:02d}"


def normalize_venue_name(venue: str) -> str:
    """
    Normalizes venue strings to group equivalent locations,
    e.g. 'Auditorium 1 - Main Complex' -> 'auditorium 1'
    """
    v = venue.lower().strip()
    # Normalize common abbreviations
    v = v.replace('audi-1', 'auditorium 1').replace('audi 1', 'auditorium 1')
    v = v.replace('audi-2', 'auditorium 2').replace('audi 2', 'auditorium 2')
    v = v.replace('block', '').replace('complex', '').replace('-', ' ')
    v = ' '.join(v.split())
    # Extract core room name
    if 'auditorium 1' in v:
        return 'auditorium 1'
    if 'auditorium 2' in v:
        return 'auditorium 2'
    if 'hall b' in v:
        return 'hall b'
    if 'seminar hall 2' in v:
        return 'seminar hall 2'
    if 'electrical machines lab' in v:
        return 'electrical machines lab'
    return v


def check_time_overlap(s1: int, e1: int, s2: int, e2: int) -> Tuple[bool, int, int, int]:
    """
    Checks if interval [s1, e1) overlaps with [s2, e2).
    Returns (has_overlap, overlap_start_mins, overlap_end_mins, overlap_duration_mins)
    """
    overlap_start = max(s1, s2)
    overlap_end = min(e1, e2)
    if overlap_start < overlap_end:
        return True, overlap_start, overlap_end, overlap_end - overlap_start
    return False, 0, 0, 0


def detect_all_conflicts(notices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Audits a list of active academic notices and timetable entries for conflicts.
    Only audits notices with status 'ACTIVE' (ignores superseded versions).
    """
    active_notices = [n for n in notices if n.get("status", "ACTIVE") != "SUPERSEDED"]
    conflicts = []

    # Check for holiday conflicts first
    holiday_notices = [n for n in active_notices if n.get("category") == "Holiday & Recess" or "holiday" in n.get("title", "").lower()]
    for hol in holiday_notices:
        hol_date = str(hol.get("date", "")).strip()
        if not hol_date or "not specified" in hol_date.lower():
            continue
        for n in active_notices:
            if n.get("id") == hol.get("id"):
                continue
            n_date = str(n.get("date", "")).strip()
            if not n_date or "not specified" in n_date.lower():
                continue
            if n_date == hol_date and n.get("category") in ["Examination", "Class Test", "Laboratory Exam"]:
                conflicts.append({
                    "id": f"CONF-HOL-{n.get('id')}",
                    "type": "HOLIDAY_COLLISION",
                    "severity": "CRITICAL",
                    "date": hol_date,
                    "event_a": hol,
                    "event_b": n,
                    "overlap_window": "Full Day",
                    "duration_minutes": 720,
                    "explanation": f"Assessment '{n.get('title')}' is scheduled on a declared university holiday/recess ('{hol.get('title')}').",
                    "recommendation": f"Reschedule '{n.get('title')}' to an alternate instructional day per Academic Council policy.",
                    "status": "UNRESOLVED"
                })

    # Pairwise comparison for venue and department clashes
    n_count = len(active_notices)
    for i in range(n_count):
        for j in range(i + 1, n_count):
            item_a = active_notices[i]
            item_b = active_notices[j]

            # Conflict only possible if both dates are specified and identical
            date_a = str(item_a.get("date", "")).strip()
            date_b = str(item_b.get("date", "")).strip()
            if not date_a or not date_b or "not specified" in date_a.lower() or "unknown" in date_a.lower():
                continue
            if date_a != date_b:
                continue

            # Skip holiday notices here as handled above
            if item_a.get("category") == "Holiday & Recess" or item_b.get("category") == "Holiday & Recess":
                continue

            s_a = time_to_minutes(item_a.get("start_time", ""))
            e_a = time_to_minutes(item_a.get("end_time", ""))
            s_b = time_to_minutes(item_b.get("start_time", ""))
            e_b = time_to_minutes(item_b.get("end_time", ""))

            # Both notices must have valid specified time windows to determine conflict
            if s_a is None or e_a is None or s_b is None or e_b is None:
                continue

            has_overlap, o_start, o_end, o_dur = check_time_overlap(s_a, e_a, s_b, e_b)

            if not has_overlap:
                continue

            overlap_str = f"{minutes_to_time(o_start)} to {minutes_to_time(o_end)} ({o_dur} mins)"
            norm_v_a = normalize_venue_name(item_a.get("venue", ""))
            norm_v_b = normalize_venue_name(item_b.get("venue", ""))

            # Venues must be specified and known
            if not norm_v_a or not norm_v_b or "not specified" in norm_v_a or "unknown" in norm_v_a:
                continue

            # 1. Venue Clash: Same location
            if norm_v_a == norm_v_b and norm_v_a != "campus wide":
                conflicts.append({
                    "id": f"CONF-VEN-{item_a.get('id')}-{item_b.get('id')}",
                    "type": "VENUE_CLASH",
                    "severity": "CRITICAL",
                    "date": item_a.get("date"),
                    "venue": item_a.get("venue"),
                    "event_a": item_a,
                    "event_b": item_b,
                    "overlap_window": overlap_str,
                    "duration_minutes": o_dur,
                    "explanation": (
                        f"Physical Venue Collision in '{item_a.get('venue')}'. Both '{item_a.get('title')}' "
                        f"({item_a.get('start_time')}-{item_a.get('end_time')}) and '{item_b.get('title')}' "
                        f"({item_b.get('start_time')}-{item_b.get('end_time')}) are simultaneously booked "
                        f"for {o_dur} minutes on {item_a.get('date')}."
                    ),
                    "recommendation": (
                        f"Recommendation: Relocate '{item_b.get('title')}' to Seminar Hall 2 or Newton Block Room 101, "
                        f"or postpone Event B start time to {minutes_to_time(e_a)} after Event A concludes."
                    ),
                    "status": "UNRESOLVED"
                })

            # 2. Department Cohort Clash: Same department, different events at the same time
            elif item_a.get("department") == item_b.get("department") and item_a.get("department") != "Central Academic Administration":
                conflicts.append({
                    "id": f"CONF-COH-{item_a.get('id')}-{item_b.get('id')}",
                    "type": "DEPARTMENT_COHORT_CLASH",
                    "severity": "HIGH",
                    "date": item_a.get("date"),
                    "department": item_a.get("department"),
                    "event_a": item_a,
                    "event_b": item_b,
                    "overlap_window": overlap_str,
                    "duration_minutes": o_dur,
                    "explanation": (
                        f"Department Schedule Overlap: Department of '{item_a.get('department')}' has two "
                        f"conflicting academic events scheduled concurrently: '{item_a.get('title')}' and '{item_b.get('title')}'. "
                        f"Students or faculty may be unable to attend both."
                    ),
                    "recommendation": (
                        f"Recommendation: Check target student batch years. If overlapping batches, stagger "
                        f"start times by at least 2 hours."
                    ),
                    "status": "UNRESOLVED"
                })

    return conflicts
