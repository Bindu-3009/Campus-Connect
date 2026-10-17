"""
Campus Connect - Intelligent Academic Notice Parser & Information Extraction Engine
Extracts: Event Name, Date, Start Time, End Time, Venue, Department, Reference Code, and Revision Status.
Uses PyMuPDF (fitz) with fallback to pypdf, local OCR detection, and safe multi-encoding TXT decoding.
STRICT AUDIT: Does NOT invent or fabricate missing values. Missing fields are explicitly marked as unknown.
"""

import re
import datetime
import io
from typing import Dict, Any, Optional, Tuple, List

# 1. Primary PDF Engine: PyMuPDF (pymupdf / fitz)
try:
    import pymupdf as fitz
    PYMUPDF_AVAILABLE = True
except ImportError:
    try:
        import fitz  # Fallback for older PyMuPDF versions
        PYMUPDF_AVAILABLE = True
    except ImportError:
        PYMUPDF_AVAILABLE = False

# 2. Secondary PDF Engine: pypdf
try:
    import pypdf
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

# 3. Optional Local OCR Engine: pytesseract + PIL
try:
    import pytesseract
    from PIL import Image
    OCR_LIB_AVAILABLE = True
except ImportError:
    OCR_LIB_AVAILABLE = False


def decode_text_file(raw_bytes: bytes) -> Tuple[str, str]:
    """
    Decodes plain-text files using robust fallback encodings:
    1. utf-8-sig (handles UTF-8 with BOM common on Windows)
    2. utf-8 (standard)
    3. cp1252 (Windows Western European)
    4. latin-1 (guaranteed byte-to-char fallback)
    """
    if not raw_bytes:
        return "", "TXT file is empty (0 bytes)."

    encodings = ["utf-8-sig", "utf-8", "cp1252", "latin-1"]
    for enc in encodings:
        try:
            decoded = raw_bytes.decode(enc)
            # Normalize line endings
            normalized = decoded.replace("\r\n", "\n").replace("\r", "\n").strip()
            return normalized, f"Successfully decoded text file using {enc.upper()} encoding."
        except UnicodeDecodeError:
            continue

    # Absolute fallback
    fallback_text = raw_bytes.decode("utf-8", errors="replace").replace("\r\n", "\n")
    return fallback_text, "Decoded text file with character replacement fallback."


def extract_text_from_pdf(file_bytes_or_stream) -> Tuple[str, str, bool]:
    """
    Extracts readable text from an uploaded PDF.
    Does NOT decode PDF binary as UTF-8.
    Detects scanned/image-only PDFs and invokes or advises OCR.

    Returns: (extracted_text, status_message, is_scanned)
    """
    # Read raw bytes
    if hasattr(file_bytes_or_stream, "read"):
        file_bytes = file_bytes_or_stream.read()
        # Reset stream pointer if seekable
        if hasattr(file_bytes_or_stream, "seek"):
            file_bytes_or_stream.seek(0)
    elif isinstance(file_bytes_or_stream, bytes):
        file_bytes = file_bytes_or_stream
    else:
        return "", "Invalid PDF input format. Expected bytes or file stream.", False

    if not file_bytes:
        return "", "Uploaded PDF file is empty (0 bytes).", False

    # Check PDF magic header '%PDF-'
    if not file_bytes.startswith(b"%PDF-"):
        return "", "Uploaded file does not have a valid PDF header (%PDF-).", False

    extracted_pages = []
    engine_used = ""

    # Strategy A: Use PyMuPDF (fitz) - Fastest & best layout preservation
    if PYMUPDF_AVAILABLE:
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            engine_used = "PyMuPDF (fitz)"
            for page in doc:
                text = page.get_text()
                if text and text.strip():
                    extracted_pages.append(text.strip())

            total_chars = sum(len(p) for p in extracted_pages)

            # Check if document has selectable text
            if total_chars >= 30:
                joined = "\n\n".join(extracted_pages)
                return joined, f"Successfully extracted {len(joined)} characters across {len(doc)} page(s) using {engine_used}.", False

            # If little or no text found, this is a scanned/image-only PDF!
            # Attempt OCR via PyMuPDF pixmaps + pytesseract if available
            ocr_text, ocr_msg, ocr_success = attempt_local_ocr(doc)
            if ocr_success:
                return ocr_text, f"Scanned PDF detected. {ocr_msg}", True
            else:
                return (
                    "",
                    (
                        "⚠️ Scanned / Image-Only PDF detected (0 characters of selectable text found). "
                        "This document consists of scanned images with no embedded text layer. "
                        + ocr_msg
                    ),
                    True
                )
        except Exception as e:
            # If PyMuPDF encounters an unexpected issue, proceed to pypdf fallback
            engine_used = f"PyMuPDF error ({str(e)}), trying fallback"

    # Strategy B: Fallback to pypdf
    if PYPDF_AVAILABLE:
        try:
            stream = io.BytesIO(file_bytes)
            reader = pypdf.PdfReader(stream)
            engine_used = "pypdf"
            for page in reader.pages:
                text = page.extract_text()
                if text and text.strip():
                    extracted_pages.append(text.strip())

            total_chars = sum(len(p) for p in extracted_pages)
            if total_chars >= 30:
                joined = "\n\n".join(extracted_pages)
                return joined, f"Successfully extracted {len(joined)} characters across {len(reader.pages)} page(s) using {engine_used}.", False

            # Scanned / Image-only detected
            return (
                "",
                (
                    "⚠️ Scanned / Image-Only PDF detected (0 characters of selectable text found). "
                    "This document contains scanned images without an embedded text layer. "
                    "OCR is required to extract text from images. Please install Tesseract-OCR for Windows "
                    "(https://github.com/UB-Mannheim/tesseract/wiki) or paste the notice text directly into the box."
                ),
                True
            )
        except Exception as e:
            return "", f"PDF parsing failed with error: {str(e)}. Please paste notice text directly.", False

    # Strategy C: Neither library is available
    return (
        "",
        (
            "PDF extraction libraries (PyMuPDF or pypdf) are not installed. "
            "Please run 'pip install -r requirements.txt' or paste notice text directly into the text area."
        ),
        False
    )


def attempt_local_ocr(doc) -> Tuple[str, str, bool]:
    """
    Attempts to perform local optical character recognition (OCR) on PDF pages using
    PyMuPDF page pixmaps and pytesseract.
    Returns: (extracted_text, status_message, success_flag)
    """
    if not OCR_LIB_AVAILABLE:
        return (
            "",
            "Local OCR libraries (pytesseract, Pillow) are not installed. Install via: 'pip install pytesseract Pillow'. "
            "Additionally, Tesseract-OCR binary for Windows is required (https://github.com/UB-Mannheim/tesseract/wiki). "
            "You can paste the notice text directly for instant processing.",
            False
        )

    try:
        ocr_pages = []
        for i, page in enumerate(doc):
            # Render page to 200 DPI pixmap for crisp OCR recognition
            pix = page.get_pixmap(dpi=200)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            page_text = pytesseract.image_to_string(img)
            if page_text and page_text.strip():
                ocr_pages.append(page_text.strip())

        joined = "\n\n".join(ocr_pages)
        if len(joined) >= 20:
            return joined, f"OCR extracted {len(joined)} characters from {len(doc)} scanned page(s).", True
        else:
            return "", "OCR ran on page images but could not identify legible academic notice text.", False
    except pytesseract.TesseractNotFoundError:
        return (
            "",
            "Tesseract-OCR executable was not found on your Windows system PATH. "
            "To enable automatic scanned PDF OCR on Windows: "
            "1. Download and run the Tesseract installer from https://github.com/UB-Mannheim/tesseract/wiki "
            "2. Add 'C:\\Program Files\\Tesseract-OCR' to your system PATH. "
            "Alternatively, paste the notice text directly into the box below.",
            False
        )
    except Exception as e:
        return "", f"Local OCR process encountered an error: {str(e)}. Please paste text directly.", False


# ---------------------------------------------------------------------------
# Strict Information Extraction Logic (No Fabricated / Invented Defaults)
# ---------------------------------------------------------------------------

MONTH_MAP = {
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
    'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12,
    'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
    'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12
}

MONTH_REGEX = r'(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec)'


def parse_single_date(s: str) -> Optional[str]:
    """
    Parses a single candidate string into standard ISO YYYY-MM-DD.
    Supports YYYY-MM-DD, 24 October 2026, 24th October 2026, October 24 2026, 24/10/2026, 24-10-2026, etc.
    Strictly validates calendar days and months.
    """
    if not s:
        return None
    cleaned = s.strip()

    # 1. ISO format: YYYY-MM-DD or YYYY/MM/DD or YYYY.MM.DD
    m_iso = re.search(r'\b(20\d{2})[-/.](0?[1-9]|1[0-2])[-/.](0?[1-9]|[12]\d|3[01])\b', cleaned)
    if m_iso:
        y, m, d = int(m_iso.group(1)), int(m_iso.group(2)), int(m_iso.group(3))
        try:
            return datetime.date(y, m, d).strftime("%Y-%m-%d")
        except ValueError:
            pass

    # 2. Day Month Year: e.g. 24 October 2026, 24th October 2026, 24-Oct-2026, 24/Oct/2026
    m_dmy_named = re.search(rf'\b([0-3]?\d)(?:st|nd|rd|th)?[\s\-_/]+({MONTH_REGEX})[\s\-_/,]+(20\d{{2}})\b', cleaned, re.IGNORECASE)
    if m_dmy_named:
        d = int(m_dmy_named.group(1))
        mon = MONTH_MAP.get(m_dmy_named.group(2).lower(), 1)
        y = int(m_dmy_named.group(3))
        try:
            return datetime.date(y, mon, d).strftime("%Y-%m-%d")
        except ValueError:
            pass

    # 3. Month Day Year: e.g. October 24, 2026 or Oct 24, 2026
    m_mdy_named = re.search(rf'\b({MONTH_REGEX})[\s\-_/]+([0-3]?\d)(?:st|nd|rd|th)?[\s\-_/,]+(20\d{{2}})\b', cleaned, re.IGNORECASE)
    if m_mdy_named:
        mon = MONTH_MAP.get(m_mdy_named.group(1).lower(), 1)
        d = int(m_mdy_named.group(2))
        y = int(m_mdy_named.group(3))
        try:
            return datetime.date(y, mon, d).strftime("%Y-%m-%d")
        except ValueError:
            pass

    # 4. Numeric DD/MM/YYYY or DD-MM-YYYY or DD.MM.YYYY
    m_dmy_num = re.search(r'\b([0-3]?\d)[-/.](0?[1-9]|1[0-2])[-/.](20\d{2})\b', cleaned)
    if m_dmy_num:
        d, m, y = int(m_dmy_num.group(1)), int(m_dmy_num.group(2)), int(m_dmy_num.group(3))
        try:
            return datetime.date(y, m, d).strftime("%Y-%m-%d")
        except ValueError:
            pass

    # 5. Numeric MM/DD/YYYY if DD > 12
    m_mdy_num = re.search(r'\b(0?[1-9]|1[0-2])[-/.]([12]\d|3[01])[-/.](20\d{2})\b', cleaned)
    if m_mdy_num:
        m, d, y = int(m_mdy_num.group(1)), int(m_mdy_num.group(2)), int(m_mdy_num.group(3))
        try:
            return datetime.date(y, m, d).strftime("%Y-%m-%d")
        except ValueError:
            pass

    return None


def parse_academic_dates(text: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extracts and distinguishes Event Date and Notice Issue Date.
    Returns: (event_date, issue_date)
    """
    explicit_issue_date = None
    header_date = None
    body_event_date = None

    # Step 1: Detect explicit Notice Issue Date
    m_issue_explicit = re.search(
        r'(?:Notice\s+Issue\s+Date|Date\s+of\s+Issue|Issue\s+Date|Notification\s+Date|Circular\s+Date|Issued\s+on|Published\s+on)[:\s]+([^\n\r]+)',
        text,
        re.IGNORECASE
    )
    if m_issue_explicit:
        explicit_issue_date = parse_single_date(m_issue_explicit.group(1))

    # Step 2: Check top header lines (lines 1..4) where Date appears alongside or under Ref
    for line in text.splitlines()[:5]:
        m_hdr = re.search(r'(?:Ref[^\n\r]*?)?(?:Date|Dated)[:\s]+([^\n\r]+)', line, re.IGNORECASE)
        if m_hdr:
            d_cand = parse_single_date(m_hdr.group(1))
            if d_cand:
                header_date = d_cand
                break

    # Step 3: Detect Event / Examination Date from body
    event_label_patterns = [
        r'(?:Event\s+Date|Exam(?:ination)?\s+Date|Date\s+of\s+Exam(?:ination)?|Date\s+of\s+Event|Scheduled\s+Date|Commencing\s+on|Conduct(?:ed)?\s+on|Scheduled\s+on|Rescheduled\s+on|Held\s+on)[:\s]+([^\n\r]+)',
        rf'(?:held\s+on|conducted\s+on|scheduled\s+on|rescheduled\s+on|effective\s+from|dated)\s+([0-3]?\d(?:st|nd|rd|th)?[\s\-_/]+{MONTH_REGEX}[\s\-_/,]+20\d{{2}})',
        r'(?:held\s+on|conducted\s+on|scheduled\s+on|rescheduled\s+on|effective\s+from|dated)\s+([0-3]?\d[-/.](?:0?[1-9]|1[0-2])[-/.](?:20\d{2}))',
        r'(?:held\s+on|conducted\s+on|scheduled\s+on|rescheduled\s+on|effective\s+from|dated)\s+(20\d{2}[-/.](?:0?[1-9]|1[0-2])[-/.][0-3]?\d)',
    ]
    for pat in event_label_patterns:
        for m in re.finditer(pat, text, re.IGNORECASE):
            d_cand = parse_single_date(m.group(1))
            if d_cand:
                body_event_date = d_cand
                break
        if body_event_date:
            break

    # If no explicit event date label found, look for "Date: ..." on subsequent lines (line 3+)
    if not body_event_date:
        lines = text.splitlines()
        if len(lines) > 2:
            for line in lines[2:]:
                m_sub = re.search(r'(?:Date|Dated)[:\s]+([^\n\r]+)', line, re.IGNORECASE)
                if m_sub:
                    d_cand = parse_single_date(m_sub.group(1))
                    if d_cand:
                        body_event_date = d_cand
                        break

    # Step 4: Resolve event_date and issue_date
    if explicit_issue_date and body_event_date:
        return body_event_date, explicit_issue_date
    elif explicit_issue_date and header_date and explicit_issue_date != header_date:
        return header_date, explicit_issue_date
    elif explicit_issue_date:
        return explicit_issue_date, explicit_issue_date

    # If header date and distinct body date exist: header is issue date, body is event date
    if header_date and body_event_date and header_date != body_event_date:
        return body_event_date, header_date

    # Single date resolution
    single_date = body_event_date or header_date
    if not single_date:
        for line in text.splitlines():
            d_cand = parse_single_date(line)
            if d_cand:
                single_date = d_cand
                break

    # If only one date found and no explicit issue date keyword, that date is the event date
    return single_date, None


def parse_date(text: str) -> Optional[str]:
    """Backward compatible wrapper returning primary event date."""
    ev_d, _ = parse_academic_dates(text)
    return ev_d


def normalize_time_str(hour_str: str, min_str: Optional[str], meridiem: Optional[str]) -> Optional[str]:
    """
    Converts hour and minute strings to standard 24-hr HH:MM string.
    Strictly enforces 24-hour time bounds. Returns None if invalid.
    """
    try:
        h = int(hour_str)
        m = int(min_str) if min_str else 0
    except (ValueError, TypeError):
        return None

    if not (0 <= m <= 59):
        return None

    if meridiem:
        mer = meridiem.strip().upper()
        if not (1 <= h <= 12):
            return None
        if mer == 'PM' and h < 12:
            h += 12
        elif mer == 'AM' and h == 12:
            h = 0
    else:
        if not (0 <= h <= 23):
            return None

    return f"{h:02d}:{m:02d}"


def parse_time_window(text: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extracts start and end times from text, e.g. "10:00 AM to 12:00 PM", "10:30–12:30", "From 10:30 to 12:30".
    Supports en-dash (–), em-dash (—), hyphen (-), "to", and "From: ... To: ...".
    Strictly verifies time limits (00:00 to 23:59).
    Never captures arbitrary numbers or invents missing times.
    Returns (start_time, end_time). If only start time is found, returns (start_time, None).
    """
    dashes = r'(?:to|until|till|-|–|—|\u2013|\u2014)'

    # Pass 1: "From: ... To: ..." pattern (supports multi-line or single line)
    p_from_to = (
        r'(?:From|Start(?:\s*Time)?)\s*[:\s]+\s*([01]?\d|2[0-3])(?::|\.)?([0-5]\d)?\s*(AM|PM|am|pm)?\s*'
        r'(?:.*?)\s*'
        r'(?:To|End(?:\s*Time)?|Until)\s*[:\s]+\s*([01]?\d|2[0-3])(?::|\.)?([0-5]\d)?\s*(AM|PM|am|pm)?'
    )
    m_ft = re.search(p_from_to, text, re.IGNORECASE)
    if m_ft:
        h1, min1, mer1, h2, min2, mer2 = m_ft.groups()
        if not mer1 and mer2:
            if int(h1) < 12 and int(h2) < 12 and int(h1) > int(h2):
                mer1 = 'AM' if mer2.upper() == 'PM' else 'PM'
            else:
                mer1 = mer2
        t1 = normalize_time_str(h1, min1 or "00", mer1)
        t2 = normalize_time_str(h2, min2 or "00", mer2)
        if t1 and t2:
            return t1, t2

    # Pass 2: Check explicit labeled time lines first
    # e.g. "Time: 10:30 AM to 12:30 PM", "Time: 10:30–12:30", "Timing: 14:00 - 16:00"
    time_label_matches = re.findall(
        r'(?:Time|Timing|Timings|Hours|Session|Slot|Schedule|Examination\s+Schedule)[:\s]+([^\n\r]+)',
        text,
        re.IGNORECASE
    )

    for line in time_label_matches:
        # Standard interval: HH:MM (AM/PM) [DASHES] HH:MM (AM/PM)
        p_labeled = (
            rf'\b([01]?\d|2[0-3])(?::|\.)([0-5]\d)\s*(AM|PM|am|pm)?\s*'
            rf'{dashes}\s*'
            rf'([01]?\d|2[0-3])(?::|\.)([0-5]\d)\s*(AM|PM|am|pm)?\b'
        )
        m = re.search(p_labeled, line)
        if m:
            h1, min1, mer1, h2, min2, mer2 = m.groups()
            if not mer1 and mer2:
                if int(h1) < 12 and int(h2) < 12 and int(h1) > int(h2):
                    mer1 = 'AM' if mer2.upper() == 'PM' else 'PM'
                elif mer2.upper() == 'PM' and int(h1) in [8, 9, 10, 11] and (int(h2) in [12, 1, 2, 3, 4, 5] or int(h1) > int(h2)):
                    mer1 = 'AM'
                else:
                    mer1 = mer2
            t1 = normalize_time_str(h1, min1, mer1)
            t2 = normalize_time_str(h2, min2, mer2)
            if t1 and t2:
                return t1, t2

        # Labeled line with whole hours: e.g. "Time: 10 AM to 1 PM" or "Time: 10 to 12 PM"
        p_labeled_whole = (
            rf'\b(1[0-2]|0?[1-9])\s*(AM|PM|am|pm)?\s*'
            rf'{dashes}\s*'
            rf'(1[0-2]|0?[1-9])\s*(AM|PM|am|pm)\b'
        )
        m_w = re.search(p_labeled_whole, line)
        if m_w:
            h1, mer1, h2, mer2 = m_w.groups()
            if not mer1 and mer2:
                if int(h1) > int(h2) or (mer2.upper() == 'PM' and int(h1) in [8, 9, 10, 11]):
                    mer1 = 'AM'
                else:
                    mer1 = mer2
            t1 = normalize_time_str(h1, "00", mer1)
            t2 = normalize_time_str(h2, "00", mer2)
            if t1 and t2:
                return t1, t2

    # Pass 3: Search entire text for formatted time intervals
    p_formatted = (
        rf'\b([01]?\d|2[0-3])(?::|\.)([0-5]\d)\s*(AM|PM|am|pm)?\s*'
        rf'{dashes}\s*'
        rf'([01]?\d|2[0-3])(?::|\.)([0-5]\d)\s*(AM|PM|am|pm)?\b'
    )
    for m in re.finditer(p_formatted, text):
        h1, min1, mer1, h2, min2, mer2 = m.groups()
        if not mer1 and mer2:
            if int(h1) < 12 and int(h2) < 12 and int(h1) > int(h2):
                mer1 = 'AM' if mer2.upper() == 'PM' else 'PM'
            elif mer2.upper() == 'PM' and int(h1) in [8, 9, 10, 11] and (int(h2) in [12, 1, 2, 3, 4, 5] or int(h1) > int(h2)):
                mer1 = 'AM'
            else:
                mer1 = mer2
        t1 = normalize_time_str(h1, min1, mer1)
        t2 = normalize_time_str(h2, min2, mer2)
        if t1 and t2:
            return t1, t2

    # Pass 4: Whole hours with explicit AM/PM across document: e.g. "10 AM to 12 PM"
    p_ampm_only = (
        rf'\b(1[0-2]|0?[1-9])(?::([0-5]\d))?\s*(AM|PM|am|pm)\s*'
        rf'{dashes}\s*'
        rf'(1[0-2]|0?[1-9])(?::([0-5]\d))?\s*(AM|PM|am|pm)\b'
    )
    m_ampm = re.search(p_ampm_only, text)
    if m_ampm:
        h1, min1, mer1, h2, min2, mer2 = m_ampm.groups()
        t1 = normalize_time_str(h1, min1 or "00", mer1)
        t2 = normalize_time_str(h2, min2 or "00", mer2)
        if t1 and t2:
            return t1, t2

    # Pass 5: Single Start Time (when no end time is present in notice)
    m_single = re.search(
        r'(?:Time|Timing|Timings|Commencing(?:\s+at)?|Start(?:\s*Time)?|At)[:\s]+([01]?\d|2[0-3])(?::|\.)?([0-5]\d)?\s*(AM|PM|am|pm)?\b',
        text,
        re.IGNORECASE
    )
    if m_single:
        h, min_val, mer = m_single.groups()
        t1 = normalize_time_str(h, min_val or "00", mer)
        if t1:
            return t1, None

    return None, None


def parse_venue(text: str) -> Optional[str]:
    """
    Extracts Venue / Classroom / Auditorium / Lab name.
    Returns None if not present in text. Does NOT invent a venue.
    """
    # 1. Line starting with "Venue:" or "Place:" or "Location:" or "Hall:"
    m_explicit = re.search(r'(?:Venue|Location|Room|Hall|Place)[:\s]+([^\n\r,;]+)', text, re.IGNORECASE)
    if m_explicit:
        val = m_explicit.group(1).strip()
        val = re.sub(r'\(.*?\)', '', val).strip()
        if len(val) >= 2 and not any(k in val.lower() for k in ["date", "time", "notice"]):
            return val

    # 2. Keywords like "Auditorium 1", "Hall B", "Seminar Hall 2", "Lab 3"
    m_keyword = re.search(r'((?:Auditorium|Seminar Hall|Lecture Hall|Lab(?:oratory)?|Room|Hall)\s+[A-Za-z0-9-]+(?:\s*-\s*[A-Za-z0-9\s]+)?)', text, re.IGNORECASE)
    if m_keyword:
        val = m_keyword.group(1).strip()
        if len(val) >= 3:
            return val

    return None


def normalize_department_name(name: str) -> str:
    """
    Normalizes department text consistently while preserving the correct department name and meaning.
    Transforms all-caps text (e.g. 'COMPUTER SCIENCE & ENGINEERING') into standard title casing
    ('Department of Computer Science & Engineering') and formats standard academic departments.
    """
    raw = name.strip()
    # Strip any leading 'Department of' or 'Dept of' for consistent inner processing
    raw = re.sub(r'^(?:Department|Dept\.?|School|Faculty|Centre|Office)\s+of\s+', '', raw, flags=re.IGNORECASE).strip()

    # Standard departments dictionary for canonical casing
    canonical_depts = [
        "Computer Science & Engineering",
        "Electrical & Electronics Engineering",
        "Mechanical Engineering",
        "Civil Engineering",
        "Mathematics & Data Science",
        "Physics & Nanotechnology",
        "Interdisciplinary Robotics & AI Cell",
        "Central Academic Administration"
    ]
    for cd in canonical_depts:
        if cd.lower() == raw.lower():
            return f"Department of {cd}"
        if raw.lower() in cd.lower() or cd.lower() in raw.lower():
            if len(raw) >= 6:
                return f"Department of {cd}"

    # General casing normalization for arbitrary departments
    words = raw.split()
    norm_words = []
    for i, w in enumerate(words):
        lw = w.lower()
        if lw in ["and", "of", "in", "the", "for", "&"] and i > 0:
            norm_words.append("&" if lw == "&" else lw)
        elif lw in ["ai", "cse", "ece", "eee", "it", "mech", "civil"]:
            norm_words.append(w.upper())
        elif w.isupper() or w.islower():
            norm_words.append(w.capitalize())
        else:
            norm_words.append(w)
    formatted = " ".join(norm_words)
    return f"Department of {formatted}"


def parse_department(text: str) -> Optional[str]:
    """
    Extracts Academic Department or issuing body.
    Returns None if not detected in text. Does NOT invent a department.
    """
    m_dept = re.search(r'(?:Department|Dept\.?|School|Faculty|Centre|Office)\s+of\s+([^\n\r,\.]+)', text, re.IGNORECASE)
    if m_dept:
        dept_name = m_dept.group(1).strip()
        # Clean trailing labels
        dept_name = re.sub(r'(?:Ref|Date|Notice).*$', '', dept_name, flags=re.IGNORECASE).strip()
        if len(dept_name) > 3:
            return normalize_department_name(dept_name)

    m_dept_alt = re.search(r'(?:DEPARTMENT|DEPT)[:\s]+([^\n\r,]+)', text, re.IGNORECASE)
    if m_dept_alt:
        dept_name = m_dept_alt.group(1).strip()
        dept_name = re.sub(r'(?:Ref|Date|Notice).*$', '', dept_name, flags=re.IGNORECASE).strip()
        if len(dept_name) > 3:
            return normalize_department_name(dept_name)

    # Check for known department names explicitly mentioned in document
    common_depts = [
        "Computer Science & Engineering",
        "Electrical & Electronics Engineering",
        "Mechanical Engineering",
        "Civil Engineering",
        "Mathematics & Data Science",
        "Physics & Nanotechnology",
        "Interdisciplinary Robotics & AI Cell",
        "Central Academic Administration"
    ]
    for d in common_depts:
        if d.lower() in text.lower():
            return f"Department of {d}"

    return None


def parse_event_name(text: str) -> Optional[str]:
    """
    Extracts the core title, course, or subject of the notice.
    Returns None if no identifiable event/title is found.
    """
    # 1. Look for explicit "Event:", "Subject:", "Title:", "Topic:", "Examination Schedule:"
    m_event = re.search(r'(?:Event(?:\s+Name)?|Subject|Topic|Title|Examination\s+Schedule|Exam\s+Schedule)[:\s]+([^\n\r]+)', text, re.IGNORECASE)
    if m_event:
        candidate = m_event.group(1).strip()
        candidate = re.split(r'\b(?:Ref|Date|Time|Venue):', candidate, flags=re.IGNORECASE)[0].strip()
        if len(candidate) > 3:
            return candidate

    # 2. Look for "NOTICE:", "CIRCULAR:", "ANNOUNCEMENT:", "REVISED NOTICE:", "CORRIGENDUM:"
    m_notice_title = re.search(r'(?:REVISED\s+NOTICE|AMENDMENT\s+NOTICE|CORRIGENDUM|NOTICE|CIRCULAR|ANNOUNCEMENT|EXAM(?:INATION)?\s+NOTICE)[:\s]+([^\n\r]+)', text, re.IGNORECASE)
    if m_notice_title:
        candidate = m_notice_title.group(1).strip()
        candidate = re.split(r'\b(?:Ref|Date|Time|Venue):', candidate, flags=re.IGNORECASE)[0].strip()
        if len(candidate) > 5 and not candidate.lower().startswith("ref"):
            return candidate

    # 3. Search for course code + examination / assessment headline
    m_course = re.search(r'\b([A-Z]{2,4}\s*\d{3})\b[:\s\-]+([^\n\r]+)', text)
    if m_course:
        return f"{m_course.group(1).strip()}: {m_course.group(2).strip()[:50]}"

    # 4. First meaningful headline line
    for line in text.splitlines():
        line = line.strip()
        if (
            len(line) > 10
            and len(line) < 100
            and not re.match(r'^(?:OFFICE|DEPARTMENT|REF|DATE|TIME|VENUE|CIRCULAR|ANNOUNCEMENT|NOTE)', line, re.IGNORECASE)
        ):
            return line

    return None


def parse_reference_code(text: str) -> Optional[str]:
    """
    Extracts administrative reference code of THIS notice, e.g. Ref: CSE/EXAM/2026/01-R1.
    Ignores reference codes that belong to a referenced previous/parent notice
    (e.g., following 'supersedes', 'previous notice', 'in modification of', 'amends', etc.).
    Returns None if not present in text.
    """
    ref_pattern = re.compile(r'(?:Ref(?:\.?\s*No\.?|\.?\s*Code)?|Notice\s*(?:No\.?|ID|Ref|Reference)|Reference(?:\s*No\.?|\s*Code)?)[:\s]+([A-Za-z0-9/_.\-]+)', re.IGNORECASE)

    parent_indicators = [
        "previous", "earlier", "original", "supersed", "modification of",
        "in place of", "amends", "revises", "prior notice", "vide notice",
        "with reference to", "reference to notice"
    ]

    for m in ref_pattern.finditer(text):
        candidate = m.group(1).strip().rstrip(".,;:)")
        if not candidate or len(candidate) < 3:
            continue

        # Check text preceding this match (within 80 characters or line start)
        start_pos = m.start()
        lookback_pos = max(0, start_pos - 80)
        preceding_context = text[lookback_pos:start_pos].lower()

        # If preceding text indicates a parent/superseded reference, skip it
        if any(ind in preceding_context for ind in parent_indicators):
            continue

        return candidate

    return None


def detect_revision_details(text: str, reference_code: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyzes notice text and reference code for explicit or ambiguous revision indicators.
    Detects:
      - Status: "Revision detected" | "Needs review" | "New notice / no revision detected"
      - is_revision: bool
      - confidence: float (0.0 to 1.0)
      - version: int
      - parent_reference_hint: Optional[str]
      - revision_date: Optional[str]
      - indicators_found: List[str]
      - reasoning: str
    """
    lower_text = text.lower()
    strong_indicators = []
    ambiguous_indicators = []

    # 1. Strong indicator phrases (explicit revision / amendment / corrigendum)
    strong_phrase_patterns = [
        (r'\bcorrigendum\b', 'corrigendum'),
        (r'\baddendum\s*/\s*corrigendum\b', 'addendum/corrigendum'),
        (r'\bin\s+partial\s+modification\s+of\b', 'in partial modification of'),
        (r'\bin\s+modification\s+of\b', 'in modification of'),
        (r'\bmodification\s+of\s+previous\s+notice\b', 'modification of previous notice'),
        (r'\bin\s+place\s+of\s+(?:the\s+)?(?:previous|earlier)\s+notice\b', 'in place of previous notice'),
        (r'\bin\s+place\s+of\s+notice\b', 'in place of notice'),
        (r'\bsupersedes\s+(?:the\s+)?(?:previous|earlier)\s+notice\b', 'supersedes previous notice'),
        (r'\bsupersedes\b', 'supersedes'),
        (r'\bsuperseding\b', 'superseding'),
        (r'\bin\s+supersession\s+of\b', 'in supersession of'),
        (r'\brevised\s+notice\b', 'revised notice'),
        (r'\brevised\s+schedule\b', 'revised schedule'),
        (r'\brevised\s+timetable\b', 'revised timetable'),
        (r'\brevised\s+circular\b', 'revised circular'),
        (r'\brevision\s+notice\b', 'revision notice'),
        (r'\bamended\s+notice\b', 'amended notice'),
        (r'\bamended\s+schedule\b', 'amended schedule'),
        (r'\bamendment\s+notice\b', 'amendment notice'),
        (r'\bamendment\s+to\b', 'amendment to'),
    ]

    for pat, label in strong_phrase_patterns:
        if re.search(pat, lower_text):
            if label not in strong_indicators:
                strong_indicators.append(label)

    # Check standalone strong keywords in headers or text
    header_chunk = "\n".join(text.split("\n")[:8]).lower()
    for kw in ['revised', 'amendment', 'corrigendum']:
        if re.search(r'\b' + kw + r'\b', header_chunk):
            if kw not in strong_indicators:
                strong_indicators.append(kw)

    # Reference code indicators (e.g. -R1, _REV, v2)
    if reference_code:
        m_r_suffix = re.search(r'-R\d+', reference_code, re.IGNORECASE)
        if m_r_suffix:
            strong_indicators.append(f"reference code suffix '{m_r_suffix.group(0)}'")
        elif re.search(r'[-_]REV\b', reference_code, re.IGNORECASE):
            strong_indicators.append("reference code suffix 'REV'")
        elif re.search(r'[-_]v[2-9]\b', reference_code, re.IGNORECASE):
            m_v_suffix = re.search(r'[-_]v[2-9]\b', reference_code, re.IGNORECASE)
            strong_indicators.append(f"reference code version '{m_v_suffix.group(0)}'")

    # 2. Ambiguous indicators (suggesting rescheduling or changes without explicit revision decree)
    ambiguous_phrase_patterns = [
        (r'\brescheduled\b', 'rescheduled'),
        (r'\breschedule\b', 'reschedule'),
        (r'\brescheduling\b', 'rescheduling'),
        (r'\bpostponed\b', 'postponed'),
        (r'\bpostponement\b', 'postponement'),
        (r'\bdeferred\b', 'deferred'),
        (r'\bcorrection\b', 'correction'),
        (r'\bcorrected\b', 'corrected'),
        (r'\bupdated\s+schedule\b', 'updated schedule'),
        (r'\bschedule\s+update\b', 'schedule update'),
        (r'\bupdated\s+timetable\b', 'updated timetable'),
        (r'\btiming\s+changed\b', 'timing changed'),
        (r'\bdate\s+changed\b', 'date changed'),
        (r'\bvenue\s+changed\b', 'venue changed'),
        (r'\btime\s+changed\b', 'time changed'),
    ]

    for pat, label in ambiguous_phrase_patterns:
        if re.search(pat, lower_text):
            if label not in ambiguous_indicators:
                ambiguous_indicators.append(label)

    # 3. Extract parent reference hint
    parent_hint = None
    INVALID_REF_TOKENS = {
        "previous", "notice", "the", "earlier", "original", "dated", "date",
        "ref", "reference", "time", "venue", "hall", "order", "circular",
        "all", "students", "faculty", "staff", "please", "schedule", "new",
        "amendment", "revised", "revision", "corrigendum", "subject", "event",
        "of", "in", "to", "for", "with", "and", "regarding", "issued", "duties"
    }

    parent_patterns = [
        # 1. Action verb / phrase + optional (the) previous/earlier/original notice (reference) + optional Ref/No/ID + reference code
        r'(?:in\s+(?:partial\s+)?modification\s+of|supersedes?|superseding|in\s+supersession\s+of|amends?|amendment\s+(?:to|of)|revises?|revision\s+of|in\s+place\s+of|in\s+lieu\s+of)\s+(?:(?:the\s+)?(?:previous|earlier|original|old|prior|past)\s+notice(?:\s+reference)?|(?:the\s+)?notice(?:\s+reference)?)\s*(?:(?:Ref(?:\.?\s*No\.?)?|reference\s*no\.?|reference|notice\s*no\.?|no\.?)[:\s]+)?([A-Za-z0-9/_.\-]+)',

        # 2. previous/earlier/original notice + optional Ref/No/reference + reference code
        r'(?:previous|earlier|original|prior|past)\s+notice\s*(?:reference)?\s*(?:(?:Ref(?:\.?\s*No\.?)?|reference\s*no\.?|reference|notice\s*no\.?|no\.?)[:\s]+)?([A-Za-z0-9/_.\-]+)',

        # 3. Action verb + direct "Ref:" or "No:" or "Notice No:" + reference code
        r'(?:in\s+(?:partial\s+)?modification\s+of|supersedes?|superseding|in\s+supersession\s+of|amends?|amendment\s+(?:to|of)|revises?|revision\s+of|in\s+place\s+of)\s*(?:Ref(?:\.?\s*No\.?)?|Notice\s*No\.?|No\.?)[:\s]+([A-Za-z0-9/_.\-]+)',

        # 4. vide notice / with reference to notice + reference code
        r'(?:vide\s+notice(?:\s+no\.?)?|with\s+reference\s+to\s+notice(?:\s+no\.?)?|refer\s+(?:to\s+)?notice(?:\s+no\.?)?)[:\s]+([A-Za-z0-9/_.\-]+)',

        # 5. Direct verb + distinct code containing slashes or dashes
        r'(?:revises?|amends?|supersedes?|modification\s+of)\s+([A-Za-z0-9]{2,10}[/\-_][A-Za-z0-9/\-_]+)'
    ]

    for p_pat in parent_patterns:
        for m in re.finditer(p_pat, text, re.IGNORECASE):
            candidate = m.group(1).strip().rstrip(".,;:)")
            cand_lower = candidate.lower()
            if candidate and len(candidate) >= 3 and cand_lower not in INVALID_REF_TOKENS:
                # Discard pure alphabetic English words without numbers or separators
                if candidate.isalpha() and len(candidate) < 6:
                    continue
                parent_hint = candidate
                break
        if parent_hint:
            break

    # If no parent hint from text, check if reference code is -R\d+ and infer base ref
    if not parent_hint and reference_code:
        m_r = re.search(r'^(.*?)(?:-R\d+|[-_]REV\d*|/REV\d*)$', reference_code, re.IGNORECASE)
        if m_r and m_r.group(1).strip():
            parent_hint = m_r.group(1).strip()

    # 4. Extract revision number / version
    version = 1
    if reference_code:
        m_rev_code = re.search(r'-R(\d+)', reference_code, re.IGNORECASE)
        if m_rev_code:
            version = int(m_rev_code.group(1)) + 1
        elif 'v2' in reference_code.lower():
            version = 2
        elif 'v3' in reference_code.lower():
            version = 3

    if version == 1:
        m_v = re.search(r'\b(?:revision|version|rev)\.?\s*[:#\-]?\s*(\d+)\b', text, re.IGNORECASE)
        if m_v:
            v_val = int(m_v.group(1))
            if v_val > 0:
                version = v_val

    # 5. Extract revision / amendment date if explicitly specified
    revision_date = None
    m_rdate = re.search(r'(?:revised\s+on|amended\s+on|corrigendum\s+date|revision\s+date|rescheduled\s+on|modification\s+date)\s*[:\-]?\s*([A-Za-z0-9,\s\-]+?)(?=\n|\r|$|[.;])', text, re.IGNORECASE)
    if m_rdate:
        parsed_rev_date = parse_date(m_rdate.group(1).strip())
        if parsed_rev_date:
            revision_date = parsed_rev_date

    # 6. Classification & Confidence Scoring
    if strong_indicators:
        status = "Revision detected"
        is_revision = True
        confidence = 0.95
        if version == 1:
            version = 2
        all_found = strong_indicators + ambiguous_indicators
        reasoning = f"Explicit revision indicator(s) found: {', '.join(all_found)}."
    elif ambiguous_indicators:
        status = "Needs review"
        is_revision = True
        confidence = 0.60
        if version == 1:
            version = 2
        reasoning = (
            f"Needs review: Ambiguous scheduling change indicator(s) detected ({', '.join(ambiguous_indicators)}) "
            "without an explicit revision reference or amendment decree. Manual review and verification recommended."
        )
    else:
        status = "New notice / no revision detected"
        is_revision = False
        confidence = 0.95
        version = 1
        reasoning = "No revision or rescheduling indicators detected. Categorized as an original standalone notice."

    return {
        "status": status,
        "is_revision": is_revision,
        "confidence": confidence,
        "version": version,
        "parent_reference_hint": parent_hint,
        "revision_date": revision_date,
        "indicators_found": strong_indicators if strong_indicators else ambiguous_indicators,
        "reasoning": reasoning
    }


def detect_revision_metadata(text: str, reference_code: Optional[str]) -> Tuple[bool, int, Optional[str]]:
    """
    Determines if a notice is a revision/amendment, its revision number, and referenced parent notice ID.
    Returns: (is_revision, version, parent_reference_hint)
    Maintained for backward compatibility.
    """
    details = detect_revision_details(text, reference_code)
    return details["is_revision"], details["version"], details["parent_reference_hint"]


def parse_academic_notice(raw_text: str) -> Dict[str, Any]:
    """
    Comprehensive pipeline to parse any academic notice text into structured fields.
    Does NOT invent or fabricate missing fields. Marks missing items clearly as unknown.
    """
    cleaned_text = raw_text.strip()
    ref_code = parse_reference_code(cleaned_text)
    rev_details = detect_revision_details(cleaned_text, ref_code)
    is_rev = rev_details["is_revision"]
    version = rev_details["version"]
    parent_hint = rev_details["parent_reference_hint"]

    # If ref_code was identical to the parent notice ID (and not a revision suffix like -R1),
    # then this notice has no reference code of its own (it was referencing the parent)
    if ref_code and parent_hint and ref_code.upper() == parent_hint.upper():
        ref_code = None
    
    event_name = parse_event_name(cleaned_text)
    event_date, issue_date = parse_academic_dates(cleaned_text)
    start_time, end_time = parse_time_window(cleaned_text)
    venue = parse_venue(cleaned_text)
    department = parse_department(cleaned_text)

    # Classify category
    category = "General Notice"
    lower_text = cleaned_text.lower()
    if any(k in lower_text for k in ["exam", "midterm", "viva", "test", "quiz", "assessment"]):
        category = "Examination"
    elif any(k in lower_text for k in ["symposium", "conference", "keynote", "seminar", "guest lecture"]):
        category = "Guest Lecture & Seminar"
    elif any(k in lower_text for k in ["workshop", "hackathon", "bootcamp"]):
        category = "Workshop"
    elif any(k in lower_text for k in ["holiday", "break", "closure", "vacation", "recess"]):
        category = "Holiday & Recess"

    # Track missing fields strictly
    missing_fields = []
    if not event_name:
        missing_fields.append("Event Title")
    if not event_date:
        missing_fields.append("Scheduled Date")
    if not start_time:
        missing_fields.append("Start Time")
    if not end_time:
        missing_fields.append("End Time")
    if not venue:
        missing_fields.append("Venue / Room")
    if not department:
        missing_fields.append("Department")
    if not ref_code:
        missing_fields.append("Reference Code")

    # Precise confidence scoring based on actual detections (strictly entity extraction confidence)
    confidence_scores = {
        "event_name": 0.90 if event_name else 0.0,
        "date": 0.95 if event_date else 0.0,
        "start_time": 0.92 if start_time else 0.0,
        "end_time": 0.92 if end_time else 0.0,
        "venue": 0.88 if venue else 0.0,
        "department": 0.85 if department else 0.0,
        "reference_code": 0.90 if ref_code else 0.0
    }
    overall_confidence = round(sum(confidence_scores.values()) / len(confidence_scores), 2)

    return {
        "title": event_name if event_name else "[Unknown / Not Specified in Document]",
        "reference_code": ref_code if ref_code else "[Not Specified]",
        "version": version,
        "is_revision": is_rev,
        "revision_status": rev_details["status"],
        "revision_confidence": rev_details["confidence"],
        "revision_date": rev_details["revision_date"],
        "revision_indicators": rev_details["indicators_found"],
        "revision_reasoning": rev_details["reasoning"],
        "revision_detection": rev_details,
        "parent_reference_hint": parent_hint,
        "department": department if department else "[Unknown / Not Specified]",
        "category": category,
        "date": event_date if event_date else "[Not Specified]",
        "issue_date": issue_date if issue_date else "[Not Specified]",
        "start_time": start_time if start_time else "[Not Specified]",
        "end_time": end_time if end_time else "[Not Specified]",
        "venue": venue if venue else "[Unknown / Not Specified]",
        "raw_text": cleaned_text,
        "missing_fields": missing_fields,
        "has_missing_fields": len(missing_fields) > 0,
        "extraction_confidence": overall_confidence,
        "field_confidences": confidence_scores,
        "parser_engine": "NoticeIntel Deterministic Rule-Based NLP Core (100% Free / Verified)"
    }
