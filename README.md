# Campus Connect — AI-Based Revision-Aware Academic Notice Intelligence and Conflict Detection System

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

> **Campus Connect** solves academic scheduling chaos by combining rule-based information extraction, circular amendment tracking (field-by-field diff comparison), physical venue & cohort collision detection, and a context-aware academic assistant chatbot.

---

## 🎨 Visual Design & Layout Reference

Campus Connect faithfully recreates modern academic intelligence dashboards:
- **Dark Navy Sidebar (`#0F172A`)**: Persistent navigation with active route highlights, brand insignia, system health indicators, and instant demo data controls.
- **Crisp White Dashboard (`#F8FAFC` canvas with `#FFFFFF` cards)**: Elevated white cards, subtle borders (`#E2E8F0`), and clean typography.
- **Four Signature Pastel KPI Stat Cards**:
  - 📘 **Pastel Blue (`#E0F2FE` / `#0284C7`)**: Active Notices & Circulars
  - 🌸 **Pastel Pink (`#FFE4E6` / `#E11D48`)**: Revisions Tracked Across Versions
  - 🟣 **Pastel Purple (`#EDE9FE` / `#7C3AED`)**: Schedule Clashes & Timeline Collisions
  - 🍏 **Pastel Green (`#DCFCE7` / `#16A34A`)**: Upcoming Confirmed Exams
- **Interactive Widgets**:
  - Recent Academic Notices stream with status badges (`[Active]`, `[Revised v2]`, `[Superseded]`).
  - Recent Revision Panel featuring live field diff highlights.
  - Master Exam Timetable with clash flags and instant CSV export.
  - Academic Assistant Chatbot with verified circular citations.

---

## 🌟 Key Functional Features

1. **Notices & PDF Upload with AI Extraction**:
   - Extract `Event Name`, `Date`, `Start Time`, `End Time`, `Venue`, `Department`, and `Reference Code`.
   - Supports PDF file uploads (via `pypdf`) and direct text pasting.
   - 1-click **Sample Notice Loaders** for instant hackathon demonstrations.
2. **Revision History & Field-by-Field Comparison**:
   - Detects when an incoming circular modifies an earlier one (e.g. `CSE/EXAM/2026/01` $\to$ `CSE/EXAM/2026/01-R1`).
   - Side-by-side color-coded matrix: Changed fields in pink/green, unchanged in gray.
   - Calculates student schedule impact rating (`LOW`, `MODERATE`, `HIGH`, `CRITICAL`).
3. **Schedule Conflict & Timeline Clash Detection**:
   - Algorithmic interval collision engine: $\max(start_A, start_B) < \min(end_A, end_B)$.
   - Flags **Venue Clashes** (e.g. CS301 Exam and AI Symposium booked in Auditorium 1 simultaneously).
   - Flags **Department Cohort Clashes** and **Holiday Collisions**.
   - Generates actionable automated resolution proposals.
4. **Master Upcoming Exam Schedule**:
   - Multi-criteria search and department filter.
   - One-click CSV export for university administration.
5. **Academic Assistant Chatbot (100% Free & Offline)**:
   - Built-in contextual knowledge retriever that answers queries about exam dates, room bookings, and notice revisions without requiring external paid API keys.
   - Optional toggle for OpenAI / Gemini API keys for augmented natural language.
6. **Notifications Feed & Profile**:
   - Audit alert stream for high-priority conflicts and revision amendments.
   - One-click reset to pristine demo dataset.

---

## 🛠️ Technology Stack Choice & Justification

| Layer | Technology | Rationale |
|---|---|---|
| **Python Web App** | Streamlit | Beginner-friendly, zero HTML boilerplate needed for Python logic, 1-click free public hosting on Streamlit Community Cloud. |
| **Zero-Install Client App** | HTML5 / CSS3 / ES6 | Allows instant double-click demonstration in any browser without Python, pip, or command-line setup. |
| **Information Extraction** | Rule-Based NLP + Regex | 100% deterministic, zero latency, runs offline with zero paid API costs, immune to hallucination. |
| **Database** | SQLite + LocalStorage | Self-contained, portable, zero server configuration needed. |

---

## 🔬 Limitations & Ethical Transparency

- **Sample / Demo Data Labeling**: All preloaded notices and examination schedules are explicitly tagged with `[SAMPLE / DEMO DATA]` badges to ensure academic integrity.
- **OCR Limitations**: If a PDF is image-only or scanned, server-side OCR (e.g., Tesseract) requires external binaries. Campus Connect transparently alerts the user and provides a zero-friction text paste fallback.
- **AI Chatbot Privacy**: The offline intelligence engine runs locally in-process without transmitting student schedules or sensitive academic circulars to third-party cloud servers.

---

## 🚀 Running the Project Locally

### Option 1: Standalone Browser App (Instant, 0 Dependencies)
1. Navigate to the project folder:
   ```
   c:\Users\user\Desktop\AcademicNoticeAI
   ```
2. Double-click **`index.html`** to open in Chrome, Edge, or Firefox.
3. All 7 screens, demo notice loaders, conflict engine, revision diffs, and chatbot are immediately functional.

---

### Option 2: Full Python Streamlit Application
1. **Open your terminal or command prompt** in the project directory:
   ```bash
   cd c:\Users\user\Desktop\AcademicNoticeAI
   ```
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run automated test suite**:
   ```bash
   python -m unittest test_notice_intel.py
   ```
4. **Launch the Streamlit app**:
   ```bash
   streamlit run app.py
   ```
5. Open your browser at `http://localhost:8501`.

---

## 🌐 Step-by-Step GitHub & Streamlit Community Cloud Deployment

Follow these simple steps to deploy Campus Connect to a free public URL on Streamlit Community Cloud:

### Step 1: Push Project to GitHub
1. Open Command Prompt (`cmd.exe`) in `c:\Users\user\Desktop\AcademicNoticeAI`:
   ```bash
   git init
   git add .
   git commit -m "Initial commit of Campus Connect Hackathon Project"
   ```
2. Go to [GitHub](https://github.com) and create a new public repository named `CampusConnect`.
3. Link and push your code:
   ```bash
   git remote add origin https://github.com/<YOUR-GITHUB-USERNAME>/CampusConnect.git
   git branch -M main
   git push -u origin main
   ```

### Step 2: Deploy to Streamlit Community Cloud (Free)
1. Go to [share.streamlit.io](https://share.streamlit.io/) and log in with your GitHub account.
2. Click **"New app"**.
3. Select your repository: `<YOUR-GITHUB-USERNAME>/CampusConnect`.
4. Set **Branch**: `main`.
5. Set **Main file path**: `app.py`.
6. Click **"Deploy!"**.
7. Streamlit Cloud will build and launch your application at a permanent public URL (e.g. `https://campusconnect.streamlit.app`).

---

## 🧪 Automated Test Suite

Run the unit tests to verify PDF parsing, TXT decoding, OCR detection, diffs, and non-hallucinating field extraction:
```bash
# Run the PDF, TXT & strict parsing test suite:
python -m unittest test_pdf_and_parser.py

# Run all project test suites:
python -m unittest discover -s . -p "test_*.py"
```

### Tests Covered:
1. `test_text_based_pdf_extraction`: Validates that text-based PDFs are parsed via PyMuPDF/pypdf and never decoded as raw UTF-8 binary.
2. `test_scanned_pdf_detection`: Validates that PDFs with 0 selectable text characters trigger OCR detection with clear setup advisory.
3. `test_txt_file_decoding_utf8`: Validates UTF-8 text circular extraction.
4. `test_txt_file_decoding_cp1252_fallback`: Validates Windows-1252 text files with special symbols.
5. `test_strict_parsing_complete_pdf_text`: Validates real field extraction (title, ref, date, times, venue, dept) from PDF text.
6. `test_strict_parsing_incomplete_notice_no_hallucination`: Validates that missing circular fields are marked as unknown and NEVER silently fabricated.
7. `test_corrupted_binary_rejection`: Validates robust rejection of invalid binary streams.

---

## 🔍 OCR Setup for Scanned Documents (Optional)

Campus Connect automatically extracts selectable text from PDFs without any third-party services.
For image-only scanned circulars:
1. Download the Tesseract-OCR installer for Windows from: [UB-Mannheim Tesseract Wiki](https://github.com/UB-Mannheim/tesseract/wiki)
2. Run the installer and add `C:\Program Files\Tesseract-OCR` to your Windows system PATH.
3. Campus Connect will automatically utilize local Tesseract OCR to process scanned circulars.
4. Alternatively, paste the circular text directly into the Notice Raw Text box for 100% free, zero-dependency processing.
