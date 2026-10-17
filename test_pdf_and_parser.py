"""
Campus Connect - Automated Validation & Verification Suite for PDF, TXT, and Strict Parsing
Verifies:
1. Text-based PDF extraction (PyMuPDF / pypdf) without decoding binary as UTF-8
2. Scanned / image-only PDF detection and OCR advisory path
3. Robust TXT file decoding with fallback encodings
4. Strict non-hallucinating entity extraction (no fake dates, times, venues, or random codes)
5. Rejection of corrupted / arbitrary binary
"""

import unittest
import os
import sys

# Ensure local workspace is on sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from parser import (
    extract_text_from_pdf,
    decode_text_file,
    parse_academic_notice,
    parse_date,
    parse_time_window,
    parse_venue,
    parse_department,
    PYMUPDF_AVAILABLE,
    PYPDF_AVAILABLE,
    OCR_LIB_AVAILABLE
)
from conflict_detector import detect_all_conflicts

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TESTS_DIR = os.path.join(BASE_DIR, "tests")


class TestNoticeIntelPDFAndParser(unittest.TestCase):

    def setUp(self):
        self.text_pdf_path = os.path.join(TESTS_DIR, "sample_text_notice.pdf")
        self.scanned_pdf_path = os.path.join(TESTS_DIR, "sample_scanned_notice.pdf")
        self.utf8_txt_path = os.path.join(TESTS_DIR, "sample_utf8_notice.txt")
        self.incomplete_txt_path = os.path.join(TESTS_DIR, "sample_incomplete_notice.txt")

    def test_text_based_pdf_extraction(self):
        """Test 1: Extract readable text from text-based PDF containing selectable text."""
        self.assertTrue(os.path.exists(self.text_pdf_path), "Sample text PDF must exist")

        with open(self.text_pdf_path, "rb") as f:
            pdf_bytes = f.read()

        extracted_text, status_msg, is_scanned = extract_text_from_pdf(pdf_bytes)

        # Check that it extracted readable text (not binary garbage)
        self.assertFalse(is_scanned, "Text-based PDF should not be marked as scanned")
        self.assertNotIn("%PDF-", extracted_text, "Extracted text must NOT be raw PDF binary")
        self.assertNotIn("stream", extracted_text, "Extracted text must NOT contain PDF stream tags")

        # Verify key document contents extracted from PDF stream
        self.assertIn("COMPUTER SCIENCE", extracted_text.upper())
        self.assertIn("CS405", extracted_text)
        self.assertIn("2026-11-12", extracted_text)
        self.assertIn("Lecture Hall 3", extracted_text)
        self.assertIn("09:30", extracted_text)
        print("\n[TEST 1 PASSED] Text-based PDF extraction succeeded. Chars extracted:", len(extracted_text))

    def test_scanned_pdf_detection(self):
        """Test 2: Detect when a PDF has little/no extractable text and route to OCR advisory."""
        self.assertTrue(os.path.exists(self.scanned_pdf_path), "Sample scanned PDF must exist")

        with open(self.scanned_pdf_path, "rb") as f:
            pdf_bytes = f.read()

        extracted_text, status_msg, is_scanned = extract_text_from_pdf(pdf_bytes)

        # Should detect that the PDF is scanned/image-only
        self.assertTrue(is_scanned, "PDF with 0 text operators should be classified as scanned")
        self.assertIn("Scanned / Image-Only PDF detected", status_msg)
        self.assertIn("OCR", status_msg)
        print("[TEST 2 PASSED] Scanned PDF correctly detected with OCR advisory:", status_msg[:65], "...")

    def test_txt_file_decoding_utf8(self):
        """Test 3: Decode TXT file safely using proper text decoding."""
        self.assertTrue(os.path.exists(self.utf8_txt_path))

        with open(self.utf8_txt_path, "rb") as f:
            raw_bytes = f.read()

        text, msg = decode_text_file(raw_bytes)
        self.assertIn("EE302 POWER SYSTEMS", text)
        self.assertIn("2026-11-20", text)
        self.assertIn("10:00 AM to 12:00 PM", text)
        self.assertIn("Electrical Seminar Hall 1", text)
        print("[TEST 3 PASSED] UTF-8 TXT decoding succeeded. Msg:", msg)

    def test_txt_file_decoding_cp1252_fallback(self):
        """Test 4: Decode Windows CP-1252 encoded file with special characters without error."""
        sample_cp1252 = "DEPARTMENT OF CIVIL ENGINEERING\nRef: CIV/2026/01\nNOTE: Student assessment — Room 101 • Mandatory\n".encode("cp1252")
        text, msg = decode_text_file(sample_cp1252)
        self.assertIn("DEPARTMENT OF CIVIL ENGINEERING", text)
        self.assertIn("Room 101", text)
        print("[TEST 4 PASSED] Windows CP-1252 fallback decoding succeeded. Msg:", msg)

    def test_strict_parsing_complete_pdf_text(self):
        """Test 5: Connect parsing to PDF text, extracting event, date, times, venue, and dept."""
        with open(self.text_pdf_path, "rb") as f:
            pdf_bytes = f.read()

        extracted_text, _, _ = extract_text_from_pdf(pdf_bytes)
        parsed = parse_academic_notice(extracted_text)

        # Verify parsed entities
        self.assertIn("CS405", parsed["title"])
        self.assertEqual(parsed["reference_code"], "CSE/EXAM/2026/88")
        self.assertEqual(parsed["date"], "2026-11-12")
        self.assertEqual(parsed["start_time"], "09:30")
        self.assertEqual(parsed["end_time"], "12:30")
        self.assertIn("Lecture Hall 3", parsed["venue"])
        self.assertIn("Computer Science", parsed["department"])
        self.assertFalse(parsed["has_missing_fields"])
        self.assertEqual(len(parsed["missing_fields"]), 0)
        self.assertGreaterEqual(parsed["extraction_confidence"], 0.85)
        print("[TEST 5 PASSED] Strict parsing of complete notice succeeded. Confidence:", parsed["extraction_confidence"])

    def test_strict_parsing_incomplete_notice_no_hallucination(self):
        """Test 6: Incomplete notice must NOT invent fake dates, venues, or times."""
        with open(self.incomplete_txt_path, "rb") as f:
            raw_bytes = f.read()

        text, _ = decode_text_file(raw_bytes)
        parsed = parse_academic_notice(text)

        # Missing fields must be flagged, NOT filled with fabricated defaults!
        self.assertTrue(parsed["has_missing_fields"], "Missing fields must be flagged")
        self.assertIn("Scheduled Date", parsed["missing_fields"])
        self.assertIn("Start Time", parsed["missing_fields"])
        self.assertIn("End Time", parsed["missing_fields"])
        self.assertIn("Venue / Room", parsed["missing_fields"])

        # Strict equality checks: Must NOT be fake defaults like 2026-10-24 or 10:00 or Auditorium 1
        self.assertEqual(parsed["date"], "[Not Specified]")
        self.assertEqual(parsed["start_time"], "[Not Specified]")
        self.assertEqual(parsed["end_time"], "[Not Specified]")
        self.assertEqual(parsed["venue"], "[Unknown / Not Specified]")
        self.assertNotEqual(parsed["date"], "2026-10-24", "Must not invent today's date or 2026-10-24")
        self.assertNotEqual(parsed["start_time"], "10:00", "Must not invent 10:00")
        self.assertNotEqual(parsed["venue"], "Auditorium 1 - Main Complex", "Must not invent Auditorium 1")

        # But existing fields MUST be accurately identified
        self.assertEqual(parsed["reference_code"], "MECH/GEN/2026/02")
        self.assertIn("Mechanical Engineering", parsed["department"])
        print("[TEST 6 PASSED] Strict non-hallucination verified. Missing fields properly flagged:", parsed["missing_fields"])

    def test_corrupted_binary_rejection(self):
        """Test 7: Reject corrupted non-PDF binary gracefully without unhandled exceptions."""
        corrupted_bytes = b"NOT_A_PDF_HEADER_RANDOM_BINARY_DATA\x00\x01\x02\xff\xfe"
        extracted_text, status_msg, is_scanned = extract_text_from_pdf(corrupted_bytes)
        self.assertEqual(extracted_text, "")
        self.assertIn("valid PDF header", status_msg)
        print("[TEST 7 PASSED] Corrupted binary gracefully rejected:", status_msg)

    def test_strict_time_bounds_and_rejection_of_invalid_hours(self):
        """Test 8: Strict time parsing rejects impossible hours like 26:00 and date/ref ranges like 26-04."""
        # Case A: Date and reference fragments like 26-04 must NOT be extracted as time
        text_with_date_fragments = (
            "CIRCULAR No. 26-04\n"
            "Date: 2026-10-26\n"
            "Ref: CSE/2026/04\n"
            "Annual Technical Seminar in Hall 2\n"
        )
        t1, t2 = parse_time_window(text_with_date_fragments)
        self.assertIsNone(t1, "Should not parse 26-04 as start time")
        self.assertIsNone(t2, "Should not parse 26-04 as end time")

        # Case B: Impossible hour 26:00 or 26:00 to 04:00 must be rejected
        text_with_invalid_hours = "Time: 26:00 to 04:00 in Room 101"
        t1_inv, t2_inv = parse_time_window(text_with_invalid_hours)
        self.assertIsNone(t1_inv, "Hour 26 is invalid (must be 0..23)")
        self.assertIsNone(t2_inv, "Invalid time range must return (None, None)")

        # Case C: Valid formatted time with AM/PM
        text_valid = "Session Time: 10:30 AM to 12:30 PM\nVenue: Auditorium 1"
        t1_val, t2_val = parse_time_window(text_valid)
        self.assertEqual(t1_val, "10:30")
        self.assertEqual(t2_val, "12:30")

        # Case D: Valid 24-hr time
        text_24h = "Timings: 14:00 - 16:30 in Lab 1"
        t1_24, t2_24 = parse_time_window(text_24h)
        self.assertEqual(t1_24, "14:00")
        self.assertEqual(t2_24, "16:30")
        print("[TEST 8 PASSED] Strict time parsing & invalid hour rejection verified.")

    def test_unspecified_fields_do_not_cause_false_positive_conflicts(self):
        """Test 9: Notices with unspecified dates or unknown venues must not trigger false clashes."""
        notices_unspecified = [
            {
                "id": "NOT-TEST-01",
                "title": "General Draft Notice 1",
                "date": "[Not Specified]",
                "start_time": "[Not Specified]",
                "end_time": "[Not Specified]",
                "venue": "[Unknown / Not Specified]",
                "status": "ACTIVE",
                "department": "Computer Science"
            },
            {
                "id": "NOT-TEST-02",
                "title": "General Draft Notice 2",
                "date": "[Not Specified]",
                "start_time": "[Not Specified]",
                "end_time": "[Not Specified]",
                "venue": "[Unknown / Not Specified]",
                "status": "ACTIVE",
                "department": "Mechanical Engineering"
            }
        ]
        conflicts = detect_all_conflicts(notices_unspecified)
        self.assertEqual(len(conflicts), 0, "Unspecified dates/venues must not trigger false positive conflicts")
        print("[TEST 9 PASSED] Zero false-positive conflicts on unspecified fields verified.")


if __name__ == "__main__":
    unittest.main()
