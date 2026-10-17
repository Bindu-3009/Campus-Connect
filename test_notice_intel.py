"""
Campus Connect - Comprehensive Automated Unit & Feature Test Suite
Tests:
1. Academic notice text parsing & field extraction
2. Revision detection & field-by-field diff comparison
3. Timeline overlap & venue collision detection
4. SQLite persistence & demo data lifecycle
5. Academic assistant chatbot intent and context retrieval
"""

import unittest
import os
import shutil
import tempfile
from parser import (
    parse_academic_notice, parse_date, parse_time_window, parse_venue,
    detect_revision_details, parse_reference_code, parse_single_date, parse_academic_dates
)
from revision_engine import compare_notice_versions
from conflict_detector import detect_all_conflicts, time_to_minutes, check_time_overlap
import database
from chatbot_engine import generate_local_response, query_assistant
from sample_data import SAMPLE_NOTICES, SAMPLE_EXAMS


class TestNoticeIntelCore(unittest.TestCase):

    def test_parser_clean_notice(self):
        sample_text = """DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING
Ref: CSE/EXAM/2026/01                                    Date: 2026-10-24
NOTICE: CS301 MIDTERM EXAMINATION
Time: 10:00 AM to 12:00 PM
Venue: Hall B - Newton Block
All students must report 30 minutes prior."""
        parsed = parse_academic_notice(sample_text)
        self.assertEqual(parsed["date"], "2026-10-24")
        self.assertEqual(parsed["start_time"], "10:00")
        self.assertEqual(parsed["end_time"], "12:00")
        self.assertIn("Hall B", parsed["venue"])
        self.assertIn("Computer Science", parsed["department"])
        self.assertEqual(parsed["reference_code"], "CSE/EXAM/2026/01")
        self.assertFalse(parsed["is_revision"])

    def test_parser_revised_notice(self):
        sample_revised = """DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING
Ref: CSE/EXAM/2026/01-R1                                 Date: 2026-10-24
REVISED NOTICE: CS301 MIDTERM SCHEDULE AMENDMENT
In partial modification of previous notice Ref: CSE/EXAM/2026/01:
Time: 10:30 AM to 12:30 PM
Venue: Auditorium 1 - Main Complex"""
        parsed = parse_academic_notice(sample_revised)
        self.assertTrue(parsed["is_revision"])
        self.assertEqual(parsed["version"], 2)
        self.assertEqual(parsed["start_time"], "10:30")
        self.assertEqual(parsed["end_time"], "12:30")
        self.assertIn("Auditorium 1", parsed["venue"])

    def test_revision_diff_engine(self):
        old_notice = SAMPLE_NOTICES[0]  # CS301 Original (Hall B, 10:00-12:00)
        new_notice = SAMPLE_NOTICES[1]  # CS301 Revised (Auditorium 1, 10:30-12:30)

        diff_result = compare_notice_versions(old_notice, new_notice)
        self.assertGreater(diff_result["total_changes"], 0)
        self.assertIn("Venue / Room", diff_result["modified_fields"])
        self.assertIn("Start Time", diff_result["modified_fields"])
        self.assertIn("End Time", diff_result["modified_fields"])
        self.assertIn(diff_result["impact_level"], ["HIGH", "CRITICAL"])

    def test_conflict_detection_venue_clash(self):
        # CS301 Revised is in Auditorium 1 on 2026-10-24 from 10:30 to 12:30
        # AI Symposium is in Auditorium 1 on 2026-10-24 from 11:00 to 13:30
        test_notices = [
            SAMPLE_NOTICES[1],  # Active CS301 Revised
            SAMPLE_NOTICES[2],  # Active AI Symposium
        ]
        conflicts = detect_all_conflicts(test_notices)
        self.assertEqual(len(conflicts), 1)
        c = conflicts[0]
        self.assertEqual(c["type"], "VENUE_CLASH")
        self.assertEqual(c["severity"], "CRITICAL")
        self.assertEqual(c["date"], "2026-10-24")
        self.assertIn("Auditorium 1", c["explanation"])
        self.assertEqual(c["duration_minutes"], 90)  # 11:00 to 12:30 = 90 mins

    def test_no_conflict_when_venues_differ(self):
        # EE204 is in Machines Lab on 2026-10-25
        # ME305 is in Seminar Hall 2 on 2026-10-26
        test_notices = [
            SAMPLE_NOTICES[3],  # EE204 on 2026-10-25
            SAMPLE_NOTICES[4],  # ME305 on 2026-10-26
        ]
        conflicts = detect_all_conflicts(test_notices)
        self.assertEqual(len(conflicts), 0)

    def test_database_crud(self):
        # Initialize database
        database.init_db(reset=True)
        notices = database.get_all_notices()
        self.assertGreaterEqual(len(notices), 5)

        exams = database.get_all_exams()
        self.assertGreaterEqual(len(exams), 4)

        # Add custom notice
        custom_id = database.add_notice({
            "title": "Quantum Computing Workshop",
            "reference_code": "PHY/QC/2026/01",
            "version": 1,
            "department": "Physics & Nanotechnology",
            "category": "Workshop",
            "date": "2026-11-05",
            "start_time": "14:00",
            "end_time": "17:00",
            "venue": "Physics Lab 2",
            "raw_text": "Workshop on Quantum Gates",
            "is_sample": False
        })
        self.assertIsNotNone(custom_id)
        fetched = database.get_notice_by_id(custom_id)
        self.assertEqual(fetched["title"], "Quantum Computing Workshop")

    def test_notifications_and_data_integrity(self):
        """Test notification tagging, data integrity flags, and real vs sample tracking."""
        database.init_db(reset=True)
        stats = database.get_database_stats()
        self.assertTrue(stats["has_demo_data"])
        self.assertGreaterEqual(stats["sample_notices"], 1)
        self.assertGreaterEqual(stats["sample_notifications"], 1)

        # Check initial sample notifications
        notifs = database.get_notifications()
        sample_notif = next((n for n in notifs if n["id"] == "NOTIF-01"), None)
        self.assertIsNotNone(sample_notif)
        self.assertTrue(sample_notif["is_sample"])

        # Add a real user notice
        real_id = database.add_notice({
            "title": "Machine Learning Lab Midterm",
            "reference_code": "CS/ML/2026/01",
            "version": 1,
            "department": "Computer Science & Engineering",
            "category": "Examination",
            "date": "2026-11-10",
            "start_time": "10:00",
            "end_time": "12:00",
            "venue": "Lab 3",
            "raw_text": "ML lab midterm announcement",
            "is_sample": False
        })
        # Verify a real notification was logged with is_sample=False
        updated_notifs = database.get_notifications()
        real_notif = next((n for n in updated_notifs if n["id"] == f"NOTIF-{real_id}"), None)
        self.assertIsNotNone(real_notif)
        self.assertFalse(real_notif["is_sample"])

        # Verify read toggle
        database.mark_notification_read(real_notif["id"])
        check_read = next(n for n in database.get_notifications() if n["id"] == real_notif["id"])
        self.assertTrue(check_read["read"])

        database.mark_notification_unread(real_notif["id"])
        check_unread = next(n for n in database.get_notifications() if n["id"] == real_notif["id"])
        self.assertFalse(check_unread["read"])

        # Check updated database stats
        new_stats = database.get_database_stats()
        self.assertGreaterEqual(new_stats["real_notices"], 1)
        self.assertGreaterEqual(new_stats["real_notifications"], 1)

    def test_chatbot_assistant(self):
        notices = SAMPLE_NOTICES
        exams = SAMPLE_EXAMS
        conflicts = detect_all_conflicts(notices)

        # 1. Ask about conflict
        resp_conflict = generate_local_response("Are there any clashes or venue conflicts?", notices, exams, conflicts)
        self.assertIn("Conflict", resp_conflict["answer"])

        # 2. Ask about specific course
        resp_course = generate_local_response("When is the CS301 exam scheduled?", notices, exams, conflicts)
        self.assertIn("CS301", resp_course["answer"])

        # 3. Ask about revisions
        resp_rev = generate_local_response("What notices were revised recently?", notices, exams, conflicts)
        self.assertIn("Revision", resp_rev["answer"])

        # 4. Test query_assistant with Optional[str] api_key
        resp_assistant = query_assistant("Are there any clashes or venue conflicts?", notices, exams, conflicts, api_key=None)
        self.assertIn("answer", resp_assistant)
        self.assertIn("Conflict", resp_assistant["answer"])

        resp_assistant_key = query_assistant("When is the CS301 exam?", notices, exams, conflicts, api_key="demo_key")
        self.assertIn("answer", resp_assistant_key)
        self.assertIn("CS301", resp_assistant_key["answer"])

    def test_chatbot_empty_input_and_uploaded_notices(self):
        notices = SAMPLE_NOTICES
        exams = SAMPLE_EXAMS
        conflicts = detect_all_conflicts(notices)

        # 1. Empty string or whitespace must return a helpful validation message, not crash or do nothing
        resp_empty = query_assistant("", notices, exams, conflicts, api_key=None)
        self.assertIn("Empty", resp_empty["answer"])

        resp_whitespace = query_assistant("   \n\t  ", notices, exams, conflicts, api_key=None)
        self.assertIn("Empty", resp_whitespace["answer"])

        # 2. Retrieval of custom uploaded notice by title or keyword
        custom_notices = notices + [{
            "id": "NOT-CUSTOM-99",
            "title": "Robotics & Autonomous Drones Workshop",
            "reference_code": "ROBO/WK/2026/01",
            "version": 1,
            "is_revision": False,
            "department": "Interdisciplinary Robotics Cell",
            "category": "Workshop",
            "date": "2026-11-15",
            "start_time": "14:00",
            "end_time": "17:00",
            "venue": "Makerspace Lab 4",
            "status": "ACTIVE",
            "raw_text": "All drone team participants must report to Makerspace Lab 4"
        }]

        resp_custom = query_assistant("Tell me about the Robotics workshop", custom_notices, exams, conflicts, api_key=None)
        self.assertIn("Robotics", resp_custom["answer"])
        self.assertIn("ROBO/WK/2026/01", resp_custom["sources"])
        self.assertEqual(resp_custom["engine"], "Campus Connect Offline Knowledge Matcher")

        # 3. Retrieval by reference code
        resp_ref = query_assistant("Show notice ROBO/WK/2026/01", custom_notices, exams, conflicts, api_key=None)
        self.assertIn("ROBO/WK/2026/01", resp_ref["answer"])
        self.assertIn("Makerspace Lab 4", resp_ref["answer"])

    # -------------------------------------------------------------
    # Revision & Amendment Intelligence Test Suite
    # -------------------------------------------------------------

    def test_revision_clear_revised_notice(self):
        """Test Case 1: Clear revised notice with strong indicator keywords and reference code."""
        text = """DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING
Ref: CSE/EXAM/2026/01-R1                                 Date: 2026-10-24
REVISED NOTICE: CS301 MIDTERM SCHEDULE AMENDMENT
In partial modification of previous notice Ref: CSE/EXAM/2026/01:
Revised on: 2026-10-23
Time: 10:30 AM to 12:30 PM
Venue: Auditorium 1 - Main Complex"""

        parsed = parse_academic_notice(text)
        self.assertEqual(parsed["revision_status"], "Revision detected")
        self.assertTrue(parsed["is_revision"])
        self.assertGreaterEqual(parsed["revision_confidence"], 0.90)
        self.assertEqual(parsed["version"], 2)
        self.assertEqual(parsed["parent_reference_hint"], "CSE/EXAM/2026/01")
        self.assertEqual(parsed["revision_date"], "2026-10-23")
        # Entity extraction confidence is separate from revision confidence
        self.assertIn("extraction_confidence", parsed)
        self.assertIn("revision_confidence", parsed)
        self.assertNotEqual(parsed["extraction_confidence"], 0.0)

    def test_revision_new_notice(self):
        """Test Case 2: New notice with no revision or rescheduling indicators."""
        text = """DEPARTMENT OF MECHANICAL ENGINEERING
Ref: ME/SEMINAR/2026/02                                  Date: 2026-10-26
NOTICE: ROBOTICS & AUTOMATION GUEST LECTURE
All students are invited to attend.
Time: 02:00 PM to 04:00 PM
Venue: Seminar Hall 2"""

        parsed = parse_academic_notice(text)
        self.assertEqual(parsed["revision_status"], "New notice / no revision detected")
        self.assertFalse(parsed["is_revision"])
        self.assertGreaterEqual(parsed["revision_confidence"], 0.90)
        self.assertEqual(parsed["version"], 1)
        self.assertIsNone(parsed["parent_reference_hint"])

    def test_revision_ambiguous_notice(self):
        """Test Case 3: Ambiguous notice with rescheduling indicators but no explicit revision decree."""
        text = """DEPARTMENT OF ELECTRICAL ENGINEERING
Ref: EE/LAB/2026/05                                      Date: 2026-10-28
NOTICE: Power Systems Lab Schedule Update
The upcoming lab session has been rescheduled to afternoon due to grid maintenance.
Time: 03:00 PM to 05:00 PM
Venue: Machines Lab"""

        parsed = parse_academic_notice(text)
        self.assertEqual(parsed["revision_status"], "Needs review")
        self.assertTrue(parsed["is_revision"])
        self.assertEqual(parsed["revision_confidence"], 0.60)
        self.assertIn("rescheduled", parsed["revision_indicators"])
        self.assertIn("Needs review", parsed["revision_reasoning"])

    def test_revision_match_existing_original_id(self):
        """Test Case 4: Notice that references an existing original notice in local SQLite DB."""
        database.init_db(reset=True)
        # Sample DB contains CSE/EXAM/2026/01 under id 'NOT-2026-001'
        matched = database.find_matching_parent_notice("CSE/EXAM/2026/01")
        self.assertIsNotNone(matched)
        self.assertEqual(matched["id"], "NOT-2026-001")
        self.assertEqual(matched["reference_code"], "CSE/EXAM/2026/01")

        # Test case-insensitive and normalized matching (e.g. dashes vs slashes)
        matched_norm = database.find_matching_parent_notice("cse-exam-2026-01")
        self.assertIsNotNone(matched_norm)
        self.assertEqual(matched_norm["id"], "NOT-2026-001")

        # Test match by ID directly
        matched_by_id = database.find_matching_parent_notice("NOT-2026-001")
        self.assertIsNotNone(matched_by_id)
        self.assertEqual(matched_by_id["reference_code"], "CSE/EXAM/2026/01")

    def test_revision_match_unknown_id(self):
        """Test Case 5: Notice with an unknown or missing original notice ID never fabricates a match."""
        database.init_db(reset=True)
        # 1. Nonexistent reference code
        matched_unknown = database.find_matching_parent_notice("UNKNOWN/REF/9999")
        self.assertIsNone(matched_unknown)

        # 2. None or placeholder values
        self.assertIsNone(database.find_matching_parent_notice(None))
        self.assertIsNone(database.find_matching_parent_notice("[Not Specified]"))
        self.assertIsNone(database.find_matching_parent_notice("   "))

    def test_revision_scanned_pdf_ocr(self):
        """Test Case 6: Scanned PDF text extracted via OCR processes revision indicators correctly."""
        ocr_extracted_text = """NATIONAL INSTITUTE OF TECHNOLOGY
ACADEMIC SECTION
CORRIGENDUM / REVISED SCHEDULE
Supersedes previous notice Ref: CSE/EXAM/2026/01
Midterm Examination rescheduled on 2026-10-24
Time: 10:30 AM to 12:30 PM
Venue: Auditorium 1
All students note the revised venue."""

        parsed = parse_academic_notice(ocr_extracted_text)
        self.assertEqual(parsed["revision_status"], "Revision detected")
        self.assertTrue(parsed["is_revision"])
        self.assertEqual(parsed["parent_reference_hint"], "CSE/EXAM/2026/01")

        # Connect to database matching
        database.init_db(reset=True)
        matched_parent = database.find_matching_parent_notice(parsed["parent_reference_hint"])
        self.assertIsNotNone(matched_parent)

        # Connect to revision diff engine
        diff = compare_notice_versions(matched_parent, parsed)
        self.assertGreater(diff["total_changes"], 0)
        self.assertIn("Venue / Room", diff["modified_fields"])
        self.assertIn(diff["impact_level"], ["HIGH", "CRITICAL"])

    def test_parse_reference_code_isolation(self):
        """Test Case 7: parse_reference_code isolates own reference code and ignores parent references."""
        # 1. Document with only a superseded reference (no own reference code)
        text_only_parent = "CORRIGENDUM: Supersedes previous notice Ref: CSE/EXAM/2026/01"
        self.assertIsNone(parse_reference_code(text_only_parent))

        # 2. Document with both own reference code and previous notice reference
        text_both = """DEPARTMENT OF CSE
Ref: CSE/EXAM/2026/01-R2
In partial modification of previous notice Ref: CSE/EXAM/2026/01"""
        self.assertEqual(parse_reference_code(text_both), "CSE/EXAM/2026/01-R2")

    def test_date_format_variations(self):
        """Test date format variations: 24 October 2026, 24/10/2026, 24th October 2026, October 24, 2026, 24-10-2026."""
        self.assertEqual(parse_single_date("24 October 2026"), "2026-10-24")
        self.assertEqual(parse_single_date("24/10/2026"), "2026-10-24")
        self.assertEqual(parse_single_date("24th October 2026"), "2026-10-24")
        self.assertEqual(parse_single_date("October 24, 2026"), "2026-10-24")
        self.assertEqual(parse_single_date("2026-10-24"), "2026-10-24")
        self.assertEqual(parse_single_date("24-10-2026"), "2026-10-24")

        # In context of full notice text with named month
        sample_dmy = """DEPARTMENT OF MATHEMATICS
Ref: MATH/EXAM/2026/05
NOTICE: Linear Algebra Endterm Examination
Date: 24 October 2026
Time: 10:00 AM to 12:00 PM
Venue: Hall C"""
        parsed = parse_academic_notice(sample_dmy)
        self.assertEqual(parsed["date"], "2026-10-24")

        # In context of full notice text with slash format
        sample_slash = """DEPARTMENT OF MATHEMATICS
Ref: MATH/EXAM/2026/06
NOTICE: Discrete Mathematics Quiz
Exam Date: 24/10/2026
Time: 14:00 to 16:00
Venue: Room 102"""
        parsed_slash = parse_academic_notice(sample_slash)
        self.assertEqual(parsed_slash["date"], "2026-10-24")

    def test_time_format_variations(self):
        """Test time format variations: en-dash, From/To, 24-hour, and labeled intervals."""
        # 1. En-dash (10:30–12:30)
        t1, t2 = parse_time_window("Examination Timings: 10:30\u201312:30 in Hall A")
        self.assertEqual(t1, "10:30")
        self.assertEqual(t2, "12:30")

        # 2. From: ... To: ...
        t1, t2 = parse_time_window("From: 10:30 To: 12:30")
        self.assertEqual(t1, "10:30")
        self.assertEqual(t2, "12:30")

        # 3. 24-hour interval
        t1, t2 = parse_time_window("Time: 14:00 to 16:00")
        self.assertEqual(t1, "14:00")
        self.assertEqual(t2, "16:00")

        # 4. Standard 12-hour AM/PM
        t1, t2 = parse_time_window("Time: 10:30 AM to 12:30 PM")
        self.assertEqual(t1, "10:30")
        self.assertEqual(t2, "12:30")

    def test_event_date_vs_notice_issue_date_separation(self):
        """Test distinguishing notice issue date (header/circular date) from event date (exam date)."""
        notice_text = """DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING
Ref: CSE/EXAM/2026/01-R1                                    Date: 2026-10-15
REVISED NOTICE: CS301 MIDTERM SCHEDULE AMENDMENT
Date of Exam: 24 October 2026
Time: 10:30–12:30
Venue: Auditorium 1"""
        parsed = parse_academic_notice(notice_text)
        self.assertEqual(parsed["date"], "2026-10-24")
        self.assertEqual(parsed["issue_date"], "2026-10-15")

        # Explicit "Notice Issue Date:"
        notice_explicit = """DEPARTMENT OF PHYSICS
Notice Issue Date: 2026-10-12
NOTICE: Quantum Mechanics Seminar
Scheduled Date: 24/10/2026
Time: 11:00 AM to 01:00 PM
Venue: Seminar Hall 1"""
        parsed_exp = parse_academic_notice(notice_explicit)
        self.assertEqual(parsed_exp["date"], "2026-10-24")
        self.assertEqual(parsed_exp["issue_date"], "2026-10-12")

    def test_uninvented_missing_time(self):
        """Test that single times do not invent or fabricate end times."""
        notice_single_time = """DEPARTMENT OF CIVIL ENGINEERING
Ref: CE/COLL/2026/02
NOTICE: Department Orientation Ceremony
Date: 2026-10-28
Time: 10:30 AM
Venue: Main Auditorium"""
        parsed = parse_academic_notice(notice_single_time)
        self.assertEqual(parsed["start_time"], "10:30")
        self.assertEqual(parsed["end_time"], "[Not Specified]")
        self.assertIn("End Time", parsed["missing_fields"])

    def test_full_field_extraction_and_completeness(self):
        """Test that all key scheduling fields are extracted directly without manual typing."""
        notice_full = """DEPARTMENT OF MECHANICAL ENGINEERING
Ref: MECH/EXAM/2026/10                                    Notice Issue Date: 2026-10-18
EXAMINATION SCHEDULE: ME305 Thermodynamics Midterm
Exam Date: 24 October 2026
Time: 10:30–12:30
Venue: Seminar Hall 2 - Newton Complex"""
        parsed = parse_academic_notice(notice_full)
        self.assertIn("Thermodynamics", parsed["title"])
        self.assertEqual(parsed["reference_code"], "MECH/EXAM/2026/10")
        self.assertEqual(parsed["issue_date"], "2026-10-18")
        self.assertEqual(parsed["date"], "2026-10-24")
        self.assertEqual(parsed["start_time"], "10:30")
        self.assertEqual(parsed["end_time"], "12:30")
        self.assertIn("Seminar Hall 2", parsed["venue"])
        self.assertIn("Mechanical Engineering", parsed["department"])
        self.assertFalse(parsed["is_revision"])
        self.assertFalse(parsed["has_missing_fields"])
        self.assertGreaterEqual(parsed["extraction_confidence"], 0.85)


if __name__ == '__main__':
    unittest.main()
