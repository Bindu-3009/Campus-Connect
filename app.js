/**
 * Campus Connect - Client-Side Intelligence & Application Controller
 * Recreates the complete hackathon system with zero external runtime dependencies.
 */

// Initial Seed Data
const INITIAL_NOTICES = [
  {
    id: "NOT-2026-001",
    title: "CS301: Data Structures Midterm Examination (Original)",
    reference_code: "CSE/EXAM/2026/01",
    version: 1,
    is_revision: false,
    parent_notice_id: null,
    department: "Computer Science & Engineering",
    category: "Examination",
    date: "2026-10-24",
    start_time: "10:00",
    end_time: "12:00",
    venue: "Hall B - Newton Block",
    raw_text: `DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING\nRef: CSE/EXAM/2026/01        Date: 2026-10-10\nNOTICE: CS301 MIDTERM EXAMINATION\nEvent: CS301 Midterm Examination\nDate: 2026-10-24\nTime: 10:00 AM to 12:00 PM\nVenue: Hall B - Newton Block\nReport 30 mins early.`,
    status: "SUPERSEDED",
    is_sample: true,
    notes: "Original circular; later amended due to venue capacity upgrade."
  },
  {
    id: "NOT-2026-002",
    title: "CS301: Data Structures Midterm Examination (REVISED v2)",
    reference_code: "CSE/EXAM/2026/01-R1",
    version: 2,
    is_revision: true,
    parent_notice_id: "NOT-2026-001",
    department: "Computer Science & Engineering",
    category: "Examination",
    date: "2026-10-24",
    start_time: "10:30",
    end_time: "12:30",
    venue: "Auditorium 1 - Main Complex",
    raw_text: `DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING\nRef: CSE/EXAM/2026/01-R1     Date: 2026-10-15\nREVISED NOTICE: CS301 MIDTERM SCHEDULE AMENDMENT\nIn partial modification of previous notice Ref: CSE/EXAM/2026/01:\nEvent: CS301 Midterm Examination\nDate: 2026-10-24\nTime: 10:30 AM to 12:30 PM (Modified)\nVenue: Auditorium 1 - Main Complex (Modified)`,
    status: "ACTIVE",
    is_sample: true,
    notes: "Revision modifies Start Time, End Time, and Venue to Auditorium 1."
  },
  {
    id: "NOT-2026-003",
    title: "AI & Robotics Society: Annual AI Symposium & Keynote",
    reference_code: "AIR/SYM/2026/11",
    version: 1,
    is_revision: false,
    parent_notice_id: null,
    department: "Interdisciplinary Robotics & AI Cell",
    category: "Guest Lecture & Seminar",
    date: "2026-10-24",
    start_time: "11:00",
    end_time: "13:30",
    venue: "Auditorium 1 - Main Complex",
    raw_text: `INTERDISCIPLINARY ROBOTICS & AI CELL\nRef: AIR/SYM/2026/11         Date: 2026-10-12\nCIRCULAR: ANNUAL AI KEYNOTE & ROBOTICS EXHIBITION\nEvent: Annual AI Symposium & Keynote\nDate: 2026-10-24\nTime: 11:00 AM to 01:30 PM\nVenue: Auditorium 1 - Main Complex\nDistinguished guest speaker keynote.`,
    status: "ACTIVE",
    is_sample: true,
    notes: "Clashes with CS301 Revised Exam in Auditorium 1 between 11:00 AM and 12:30 PM!"
  },
  {
    id: "NOT-2026-004",
    title: "EE204: Electrical Machines Laboratory Viva-Voce",
    reference_code: "EEE/LAB/2026/04",
    version: 1,
    is_revision: false,
    parent_notice_id: null,
    department: "Electrical & Electronics Engineering",
    category: "Laboratory Exam",
    date: "2026-10-25",
    start_time: "09:00",
    end_time: "13:00",
    venue: "Electrical Machines Lab - EEE Block",
    raw_text: `DEPARTMENT OF ELECTRICAL & ELECTRONICS ENGINEERING\nRef: EEE/LAB/2026/04         Date: 2026-10-14\nNOTICE: EE204 ELECTRICAL MACHINES VIVA\nDate: 2026-10-25\nTime: 09:00 AM to 01:00 PM\nVenue: Electrical Machines Lab - EEE Block`,
    status: "ACTIVE",
    is_sample: true,
    notes: "Clear timetable slot."
  },
  {
    id: "NOT-2026-005",
    title: "ME305: Mechanical Thermodynamics Tutorial & Class Test",
    reference_code: "MECH/TEST/2026/09",
    version: 1,
    is_revision: false,
    parent_notice_id: null,
    department: "Mechanical Engineering",
    category: "Class Test",
    date: "2026-10-26",
    start_time: "14:00",
    end_time: "16:00",
    venue: "Seminar Hall 2 - Mechanical Block",
    raw_text: `DEPARTMENT OF MECHANICAL ENGINEERING\nRef: MECH/TEST/2026/09       Date: 2026-10-16\nANNOUNCEMENT: ME305 APPLIED THERMODYNAMICS SURPRISE TEST\nDate: 2026-10-26\nTime: 02:00 PM to 04:00 PM\nVenue: Seminar Hall 2 - Mechanical Block`,
    status: "ACTIVE",
    is_sample: true,
    notes: "Clear timetable slot."
  },
  {
    id: "NOT-2026-006",
    title: "Central Academic Council: Fall Mid-Semester Holiday Schedule",
    reference_code: "CAC/CIR/2026/19",
    version: 1,
    is_revision: false,
    parent_notice_id: null,
    department: "Central Academic Administration",
    category: "Holiday & Recess",
    date: "2026-10-28",
    start_time: "08:00",
    end_time: "20:00",
    venue: "Campus-Wide",
    raw_text: `CENTRAL ACADEMIC ADMINISTRATION\nRef: CAC/CIR/2026/19         Date: 2026-10-16\nCIRCULAR: AUTUMN BREAK & REVISED WORKING SATURDAYS\nUniversity holiday on 2026-10-28. No exams or lectures allowed.`,
    status: "ACTIVE",
    is_sample: true,
    notes: "Campus holiday circular."
  }
];

const INITIAL_EXAMS = [
  { course_code: "CS301", course_title: "Data Structures & Algorithms", exam_type: "Midterm", department: "Computer Science & Engineering", date: "2026-10-24", start_time: "10:30", end_time: "12:30", venue: "Auditorium 1 - Main Complex", total_students: 140, status: "SCHEDULED (REVISED)", conflict_flag: true, conflict_reason: "Clash with Annual AI Symposium in Auditorium 1" },
  { course_code: "EE204", course_title: "Electrical Machines Lab Viva", exam_type: "Lab Viva", department: "Electrical & Electronics Engineering", date: "2026-10-25", start_time: "09:00", end_time: "13:00", venue: "Electrical Machines Lab - EEE Block", total_students: 65, status: "CONFIRMED", conflict_flag: false, conflict_reason: "None" },
  { course_code: "ME305", course_title: "Applied Thermodynamics Test", exam_type: "Class Assessment", department: "Mechanical Engineering", date: "2026-10-26", start_time: "14:00", end_time: "16:00", venue: "Seminar Hall 2 - Mechanical Block", total_students: 92, status: "CONFIRMED", conflict_flag: false, conflict_reason: "None" },
  { course_code: "MA201", course_title: "Linear Algebra & Probability", exam_type: "Midterm", department: "Mathematics & Data Science", date: "2026-10-27", start_time: "10:00", end_time: "12:00", venue: "Lecture Hall Complex Room 101", total_students: 180, status: "CONFIRMED", conflict_flag: false, conflict_reason: "None" },
  { course_code: "PH102", course_title: "Engineering Physics Electromagnetics", exam_type: "Midterm", department: "Physics & Nanotechnology", date: "2026-10-29", start_time: "14:00", end_time: "16:00", venue: "Physics Hall A", total_students: 110, status: "CONFIRMED", conflict_flag: false, conflict_reason: "None" }
];

const INITIAL_NOTIFICATIONS = [
  { id: "NOTIF-01", type: "CRITICAL_CONFLICT", title: "Severe Venue Clash Detected!", message: "CS301 Revised Exam and AI Symposium are both booked in Auditorium 1 on 2026-10-24 during 11:00 AM - 12:30 PM.", timestamp: "2026-10-17 10:15 AM", read: false },
  { id: "NOTIF-02", type: "REVISION_ALERT", title: "Notice Revision Tracked: CS301 Midterm", message: "Notice Ref: CSE/EXAM/2026/01 amended to CSE/EXAM/2026/01-R1. Venue modified to Auditorium 1; start time delayed by 30 mins.", timestamp: "2026-10-15 04:30 PM", read: true },
  { id: "NOTIF-03", type: "CALENDAR_ALERT", title: "Autumn Holiday Scheduled", message: "Academic Council declared 2026-10-28 as University Autumn Holiday. Department assessments must be rescheduled.", timestamp: "2026-10-16 02:00 PM", read: true }
];

// App State
let state = {
  notices: JSON.parse(localStorage.getItem("noticeintel_notices")) || INITIAL_NOTICES,
  exams: JSON.parse(localStorage.getItem("noticeintel_exams")) || INITIAL_EXAMS,
  notifications: JSON.parse(localStorage.getItem("noticeintel_notifs")) || INITIAL_NOTIFICATIONS
};

function persistState() {
  localStorage.setItem("noticeintel_notices", JSON.stringify(state.notices));
  localStorage.setItem("noticeintel_exams", JSON.stringify(state.exams));
  localStorage.setItem("noticeintel_notifs", JSON.stringify(state.notifications));
}

function resetToSampleData() {
  state.notices = JSON.parse(JSON.stringify(INITIAL_NOTICES));
  state.exams = JSON.parse(JSON.stringify(INITIAL_EXAMS));
  state.notifications = JSON.parse(JSON.stringify(INITIAL_NOTIFICATIONS));
  persistState();
  initApp();
  alert("Demo dataset reloaded successfully!");
}

// ---------------------------------------------------------
// Navigation & Routing
// ---------------------------------------------------------
function navigateTo(screenId) {
  document.querySelectorAll(".screen-view").forEach(s => s.style.display = "none");
  const target = document.getElementById(`screen-${screenId}`);
  if (target) {
    target.style.display = "block";
  }

  // Update active sidebar nav
  const navItems = document.querySelectorAll(".nav-item");
  navItems.forEach(item => {
    item.classList.remove("active");
    if (item.getAttribute("onclick") && item.getAttribute("onclick").includes(screenId)) {
      item.classList.add("active");
    }
  });

  // Screen specific initializers
  if (screenId === "dashboard") renderDashboard();
  if (screenId === "revisions") renderRevisionsScreen();
  if (screenId === "conflicts") auditAllConflicts();
  if (screenId === "exams") renderExamsScreen();
  if (screenId === "notifications") renderNotificationsScreen();
  if (screenId === "upload") populateParentNoticeSelect();
}

// ---------------------------------------------------------
// Dashboard Renderer
// ---------------------------------------------------------
function renderDashboard() {
  const activeNotices = state.notices.filter(n => n.status !== "SUPERSEDED");
  const revisedNotices = state.notices.filter(n => n.is_revision);
  const conflicts = calculateConflicts();

  // Update KPI Cards
  document.getElementById("kpiActiveNotices").innerText = activeNotices.length;
  document.getElementById("kpiRevisions").innerText = revisedNotices.length;
  document.getElementById("kpiConflicts").innerText = conflicts.length;
  document.getElementById("kpiExams").innerText = state.exams.length;

  // Badges in Nav
  const navConfBadge = document.getElementById("navConflictBadge");
  if (navConfBadge) navConfBadge.innerText = conflicts.length;
  const unreadNotifs = state.notifications.filter(n => !n.read).length;
  const navNotifBadge = document.getElementById("navNotifBadge");
  if (navNotifBadge) navNotifBadge.innerText = unreadNotifs;

  // Conflict Banner
  const banner = document.getElementById("dashboardConflictBanner");
  if (conflicts.length > 0) {
    banner.style.display = "flex";
    banner.querySelector(".alert-content strong").innerText = `🚨 ${conflicts.length} Schedule Conflict(s) Detected!`;
    banner.querySelector(".alert-content p").innerText = conflicts[0].explanation;
  } else {
    banner.style.display = "none";
  }

  // Render Recent Notices
  const noticesContainer = document.getElementById("recentNoticesContainer");
  noticesContainer.innerHTML = state.notices.slice(0, 4).map(n => {
    const isSup = n.status === "SUPERSEDED";
    const statusBadge = isSup ? `<span class="badge badge-superseded">Superseded</span>` :
      n.is_revision ? `<span class="badge badge-revised">Revised v${n.version}</span>` :
      `<span class="badge badge-active">Active</span>`;
    const sampleTag = n.is_sample ? `<span class="badge badge-sample">Sample Data</span>` : "";

    return `
      <div class="notice-item">
        <div class="notice-top">
          <div>
            <span class="notice-code">${n.reference_code}</span>
            <span class="notice-dept">• ${n.department}</span>
            <div class="notice-title">${n.title}</div>
          </div>
          <div>${statusBadge} ${sampleTag}</div>
        </div>
        <div class="notice-meta">
          <span>📅 ${n.date}</span>
          <span>⏰ ${n.start_time} - ${n.end_time}</span>
          <span>📍 ${n.venue}</span>
        </div>
      </div>
    `;
  }).join("");

  // Render Exam Preview
  const examTable = document.getElementById("examPreviewTableBody");
  examTable.innerHTML = state.exams.slice(0, 4).map(ex => `
    <tr>
      <td><strong>${ex.course_code}</strong></td>
      <td>${ex.course_title}</td>
      <td>${ex.date}</td>
      <td>${ex.start_time} - ${ex.end_time}</td>
      <td>${ex.venue}</td>
      <td>${ex.conflict_flag ? '<span class="badge badge-clash">⚠️ Clash</span>' : '<span class="badge badge-active">Normal</span>'}</td>
    </tr>
  `).join("");

  // Render Recent Revisions Feed
  const revContainer = document.getElementById("recentRevisionsContainer");
  if (revisedNotices.length > 0) {
    revContainer.innerHTML = revisedNotices.map(rev => {
      const parent = state.notices.find(n => n.id === rev.parent_notice_id) || state.notices[0];
      const diff = computeFieldDiffs(parent, rev);
      return `
        <div style="background:#f8fafc; border-left:4px solid #db2777; border:1px solid #e2e8f0; border-left-width:4px; padding:12px; border-radius:6px; margin-bottom:10px;">
          <div style="font-size:0.82rem; font-weight:700; color:#9d174d;">🔄 REVISED: ${rev.title}</div>
          <div style="font-size:0.75rem; color:#64748b; margin:4px 0;">From Ref: <code>${parent.reference_code}</code> to <code>${rev.reference_code}</code></div>
          <div style="font-size:0.8rem; color:#1e293b;">
            <strong>Modified:</strong> ${diff.modifiedFields.join(", ")}<br>
            <strong>Impact:</strong> <span style="color:#be123c; font-weight:700;">${diff.impactLevel}</span>
          </div>
          <button class="quick-demo-btn" style="margin-top:8px;" onclick="navigateTo('revisions')">View Full Matrix →</button>
        </div>
      `;
    }).join("");
  } else {
    revContainer.innerHTML = `<p style="font-size:0.85rem; color:#64748b;">No notice revisions on file.</p>`;
  }
}

// ---------------------------------------------------------
// Extraction NLP Engine (Rule-Based & Regex)
// ---------------------------------------------------------
// ---------------------------------------------------------
// Extraction NLP Engine (Rule-Based & Regex) - Strict No-Hallucination
// ---------------------------------------------------------
function extractNoticeFields(text) {
  const cleaned = text.trim();

  // 1. Reference Code
  let refMatch = cleaned.match(/(?:Ref(?:\.?\s*No\.?)?|Notice\s*No\.?)[:\s]+([A-Za-z0-9/_.\-]+)/i);
  let refCode = refMatch ? refMatch[1].trim() : "";

  // 2. Date
  let dateMatch = cleaned.match(/\b(202\d[-/.](?:0[1-9]|1[0-2])[-/.](?:0[1-9]|[12]\d|3[01]))\b/);
  let eventDate = "";
  if (dateMatch) {
    eventDate = dateMatch[1].replace(/\//g, "-").replace(/\./g, "-");
  } else {
    // Check named months
    const monthRegex = /(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec)/i;
    const namedMatch = cleaned.match(new RegExp(`(${monthRegex.source})\\s+([0-3]?\\d)(?:st|nd|rd|th)?,?\\s+(202\\d)`, 'i'));
    if (namedMatch) {
      const months = { jan: 1, feb: 2, mar: 3, apr: 4, may: 5, jun: 6, jul: 7, aug: 8, sep: 9, oct: 10, nov: 11, dec: 12 };
      const mStr = namedMatch[1].substring(0, 3).toLowerCase();
      const mNum = months[mStr] || 1;
      const dNum = parseInt(namedMatch[2]);
      const yNum = parseInt(namedMatch[3]);
      eventDate = `${yNum}-${String(mNum).padStart(2, '0')}-${String(dNum).padStart(2, '0')}`;
    }
  }

  // 3. Time Window - Strict Multi-Pass (Validates 00:00 - 23:59, prevents matching date/ref codes like 26-04)
  function normTime(hStr, mStr, mer) {
    let h = parseInt(hStr, 10);
    let m = mStr ? parseInt(mStr, 10) : 0;
    if (isNaN(h) || isNaN(m) || m < 0 || m > 59) return null;
    if (mer) {
      const u = mer.toUpperCase();
      if (h < 1 || h > 12) return null;
      if (u === "PM" && h < 12) h += 12;
      else if (u === "AM" && h === 12) h = 0;
    } else {
      if (h < 0 || h > 23) return null;
    }
    return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`;
  }

  let startTime = "", endTime = "";
  // Check labeled lines first: e.g. "Time: 10:00 AM to 12:00 PM"
  const timeLabelMatch = cleaned.match(/(?:Time|Timing|Timings|Hours|Session|Slot|Schedule)[:\s]+([^\n\r]+)/i);
  const timeSearchText = timeLabelMatch ? timeLabelMatch[1] : cleaned;

  const tRegex = /\b([01]?\d|2[0-3])(?::([0-5]\d))?\s*(AM|PM|am|pm)?\s*(?:to|-|until|till)\s*([01]?\d|2[0-3])(?::([0-5]\d))?\s*(AM|PM|am|pm)?\b/i;
  const tMatch = timeSearchText.match(tRegex);
  if (tMatch) {
    let [ , h1, m1, mer1, h2, m2, mer2 ] = tMatch;
    // Only accept if at least one side has colon or AM/PM (avoids bare number ranges like 26-04)
    if (m1 || m2 || mer1 || mer2 || timeLabelMatch) {
      if (!mer1 && mer2) {
        if (parseInt(h1, 10) < 12 && parseInt(h2, 10) < 12 && parseInt(h1, 10) > parseInt(h2, 10)) {
          mer1 = mer2.toUpperCase() === 'PM' ? 'AM' : 'PM';
        } else {
          mer1 = mer2;
        }
      }
      const t1 = normTime(h1, m1, mer1);
      const t2 = normTime(h2, m2, mer2);
      if (t1 && t2) {
        startTime = t1;
        endTime = t2;
      }
    }
  }

  // 4. Venue
  let venue = "";
  let venueMatch = cleaned.match(/(?:Venue|Location|Room|Hall|Place)[:\s]+([^\n\r,;]+)/i);
  if (venueMatch) {
    let vCandidate = venueMatch[1].replace(/\(.*?\)/g, "").trim();
    if (vCandidate.length >= 2 && !/date|time|notice/i.test(vCandidate)) {
      venue = vCandidate;
    }
  }
  if (!venue) {
    let kwMatch = cleaned.match(/((?:Auditorium|Seminar Hall|Lecture Hall|Lab(?:oratory)?|Room|Hall)\s+[A-Za-z0-9-]+(?:\s*-\s*[A-Za-z0-9\s]+)?)/i);
    if (kwMatch && kwMatch[1].trim().length >= 3) {
      venue = kwMatch[1].trim();
    }
  }

  // 5. Department
  let dept = "";
  let deptMatch = cleaned.match(/(?:Department|Dept\.?|School|Faculty|Office)\s+of\s+([^\n\r,\.]+)/i);
  if (deptMatch) {
    let dClean = deptMatch[1].replace(/(?:Ref|Date|Notice).*$/i, "").trim();
    if (dClean.length > 3) dept = `Department of ${dClean}`;
  }
  if (!dept) {
    const knownDepts = [
      "Computer Science & Engineering",
      "Electrical & Electronics Engineering",
      "Mechanical Engineering",
      "Civil Engineering",
      "Mathematics & Data Science",
      "Physics & Nanotechnology",
      "Interdisciplinary Robotics & AI Cell",
      "Central Academic Administration"
    ];
    for (let d of knownDepts) {
      if (cleaned.toLowerCase().includes(d.toLowerCase())) {
        dept = d;
        break;
      }
    }
  }

  // 6. Title / Event
  let title = "";
  let titleMatch = cleaned.match(/(?:Event|Subject|Title)[:\s]+([^\n\r]+)/i);
  if (titleMatch && titleMatch[1].trim().length > 3) {
    title = titleMatch[1].trim();
  } else {
    let noticeHeadMatch = cleaned.match(/(?:NOTICE|CIRCULAR|ANNOUNCEMENT)[:\s]+([^\n\r]+)/i);
    if (noticeHeadMatch && noticeHeadMatch[1].trim().length > 5 && !noticeHeadMatch[1].trim().toLowerCase().startsWith("ref")) {
      title = noticeHeadMatch[1].trim();
    } else {
      let courseMatch = cleaned.match(/\b([A-Z]{2,4}\s*\d{3})\b[:\s\-]+([^\n\r]+)/);
      if (courseMatch) {
        title = `${courseMatch[1].trim()}: ${courseMatch[2].trim().substring(0, 50)}`;
      }
    }
  }

  // 7. Revision detection
  let isRev = /revised|amendment|modification|postpone|-R1|-R2|corrigendum/i.test(cleaned);

  // Missing fields audit
  let missing = [];
  if (!title) missing.push("Event Title");
  if (!refCode) missing.push("Reference Code");
  if (!dept) missing.push("Department");
  if (!eventDate) missing.push("Scheduled Date");
  if (!startTime) missing.push("Start Time");
  if (!endTime) missing.push("End Time");
  if (!venue) missing.push("Venue / Room");

  let verifiedCount = 7 - missing.length;
  let confidenceScore = Math.round((verifiedCount / 7) * 100);

  return {
    title: title || "[Unknown / Not Specified in Document]",
    refCode: refCode || "[Not Specified]",
    department: dept || "[Unknown / Not Specified]",
    date: eventDate || "[Not Specified]",
    startTime: startTime || "[Not Specified]",
    endTime: endTime || "[Not Specified]",
    venue: venue || "[Unknown / Not Specified]",
    isRevision: isRev,
    missingFields: missing,
    hasMissingFields: missing.length > 0,
    confidence: confidenceScore
  };
}

function triggerFieldExtraction() {
  const text = document.getElementById("noticeRawTextInput").value;
  if (!text.trim()) {
    document.getElementById("extractionAuditAlert").style.display = "none";
    return;
  }

  const res = extractNoticeFields(text);
  document.getElementById("extractTitle").value = res.title.startsWith("[Unknown") ? "" : res.title;
  document.getElementById("extractTitle").placeholder = res.title.startsWith("[Unknown") ? "Event title not detected in text - please enter" : "";

  document.getElementById("extractRefCode").value = res.refCode.startsWith("[Not") ? "" : res.refCode;
  document.getElementById("extractRefCode").placeholder = res.refCode.startsWith("[Not") ? "Reference code not detected - enter" : "";

  document.getElementById("extractDept").value = res.department.startsWith("[Unknown") ? "" : res.department;
  document.getElementById("extractDept").placeholder = res.department.startsWith("[Unknown") ? "Department not detected - enter" : "";

  document.getElementById("extractDate").value = res.date.startsWith("[Not") ? "" : res.date;
  document.getElementById("extractDate").placeholder = res.date.startsWith("[Not") ? "YYYY-MM-DD not detected - enter" : "";

  document.getElementById("extractVenue").value = res.venue.startsWith("[Unknown") ? "" : res.venue;
  document.getElementById("extractVenue").placeholder = res.venue.startsWith("[Unknown") ? "Venue not detected - enter" : "";

  document.getElementById("extractStartTime").value = res.startTime.startsWith("[Not") ? "" : res.startTime;
  document.getElementById("extractStartTime").placeholder = res.startTime.startsWith("[Not") ? "HH:MM" : "";

  document.getElementById("extractEndTime").value = res.endTime.startsWith("[Not") ? "" : res.endTime;
  document.getElementById("extractEndTime").placeholder = res.endTime.startsWith("[Not") ? "HH:MM" : "";

  document.getElementById("extractIsRevision").checked = res.isRevision;

  toggleParentSelect(res.isRevision);
  document.getElementById("extractionConfidenceBadge").innerText = `Confidence: ${res.confidence}%`;

  // Display audit alert
  const alertBox = document.getElementById("extractionAuditAlert");
  if (alertBox) {
    if (res.hasMissingFields) {
      alertBox.style.display = "block";
      alertBox.style.backgroundColor = "#fffbeb";
      alertBox.style.border = "1px solid #fde68a";
      alertBox.style.color = "#92400e";
      alertBox.innerHTML = `⚠️ <strong>Missing Fields in Document:</strong> ${res.missingFields.join(", ")} were not found in the circular text. NoticeIntel does not fabricate values. Please review and fill them in below before saving.`;
    } else {
      alertBox.style.display = "block";
      alertBox.style.backgroundColor = "#f0fdf4";
      alertBox.style.border = "1px solid #bbf7d0";
      alertBox.style.color = "#166534";
      alertBox.innerHTML = `✅ <strong>All Core Fields Verified:</strong> Successfully identified Title, Date, Timing, Venue, and Issuing Department.`;
    }
  }
}

function loadSampleToForm(type) {
  let sampleNotice = INITIAL_NOTICES[0];
  if (type === "revised") sampleNotice = INITIAL_NOTICES[1];
  if (type === "clash") sampleNotice = INITIAL_NOTICES[2];

  document.getElementById("noticeRawTextInput").value = sampleNotice.raw_text;
  triggerFieldExtraction();
}

async function handleFileUpload(event) {
  const file = event.target.files[0];
  if (!file) return;

  const fileName = file.name.toLowerCase();
  const alertBox = document.getElementById("extractionAuditAlert");

  if (fileName.endsWith(".pdf")) {
    // DO NOT decode PDF binary as raw text string!
    // Check if PDF.js is available
    if (typeof pdfjsLib !== "undefined") {
      const reader = new FileReader();
      reader.onload = async function(e) {
        try {
          const typedarray = new Uint8Array(e.target.result);
          const pdf = await pdfjsLib.getDocument({ data: typedarray }).promise;
          let fullText = "";

          for (let i = 1; i <= pdf.numPages; i++) {
            const page = await pdf.getPage(i);
            const textContent = await page.getTextContent();
            const pageText = textContent.items.map(item => item.str).join(" ");
            if (pageText.trim()) {
              fullText += (fullText ? "\n\n" : "") + pageText.trim();
            }
          }

          if (fullText.trim().length < 30) {
            // Scanned / Image-Only PDF detected
            if (alertBox) {
              alertBox.style.display = "block";
              alertBox.style.backgroundColor = "#fff1f2";
              alertBox.style.border = "1px solid #fecdd3";
              alertBox.style.color = "#881337";
              alertBox.innerHTML = `⚠️ <strong>Scanned / Image-Only PDF Detected:</strong> 0 characters of selectable text found. This document consists of scanned images without an embedded text layer. OCR is required to extract text from images. Please run the Streamlit Python backend (<code style="background:#fee2e2; padding:2px 5px; border-radius:3px;">streamlit run app.py</code>) with Tesseract OCR enabled, or paste the notice text directly below.`;
            }
            document.getElementById("noticeRawTextInput").value = "";
          } else {
            document.getElementById("noticeRawTextInput").value = fullText.trim();
            triggerFieldExtraction();
          }
        } catch (err) {
          alert("Error extracting text from PDF: " + err.message + ". Please paste notice text directly.");
        }
      };
      reader.readAsArrayBuffer(file);
    } else {
      alert("PDF.js library is loading or offline. To extract PDFs with PyMuPDF and local OCR, run the Streamlit app: 'streamlit run app.py'. You may also paste notice text directly.");
    }
  } else {
    // Text File: Decode safely as UTF-8
    const reader = new FileReader();
    reader.onload = function(e) {
      document.getElementById("noticeRawTextInput").value = e.target.result;
      triggerFieldExtraction();
    };
    reader.readAsText(file, "UTF-8");
  }
}

function toggleParentSelect(isRev) {
  const group = document.getElementById("parentSelectGroup");
  if (group) {
    group.style.display = isRev ? "block" : "none";
  }
}

function populateParentNoticeSelect() {
  const select = document.getElementById("extractParentId");
  if (!select) return;
  select.innerHTML = state.notices.map(n => `<option value="${n.id}">${n.id}: ${n.title} (${n.reference_code})</option>`).join("");
}

function saveNoticeFromForm(event) {
  event.preventDefault();

  const title = document.getElementById("extractTitle").value;
  const refCode = document.getElementById("extractRefCode").value;
  const dept = document.getElementById("extractDept").value;
  const date = document.getElementById("extractDate").value;
  const venue = document.getElementById("extractVenue").value;
  const startTime = document.getElementById("extractStartTime").value;
  const endTime = document.getElementById("extractEndTime").value;
  const isRev = document.getElementById("extractIsRevision").checked;
  const parentId = isRev ? document.getElementById("extractParentId").value : null;
  const rawText = document.getElementById("noticeRawTextInput").value;

  const newId = `NOT-2026-${String(state.notices.length + 1).padStart(3, '0')}`;

  // If revision, mark parent as superseded
  if (isRev && parentId) {
    const parentNotice = state.notices.find(n => n.id === parentId);
    if (parentNotice) {
      parentNotice.status = "SUPERSEDED";
    }
  }

  const newNotice = {
    id: newId,
    title: title.trim() || "Untitled Academic Notice",
    reference_code: refCode.trim() || "UNASSIGNED-REF",
    version: isRev ? 2 : 1,
    is_revision: isRev,
    parent_notice_id: parentId,
    department: dept.trim() || "[Unknown / Not Specified]",
    category: "Examination",
    date: date.trim() || "[Not Specified]",
    start_time: startTime.trim() || "[Not Specified]",
    end_time: endTime.trim() || "[Not Specified]",
    venue: venue.trim() || "[Unknown / Not Specified]",
    raw_text: rawText || "Custom user input notice",
    status: "ACTIVE",
    is_sample: false,
    notes: "Uploaded by user via web interface"
  };

  state.notices.unshift(newNotice);

  // Add notification
  state.notifications.unshift({
    id: `NOTIF-${newId}`,
    type: isRev ? "REVISION_ALERT" : "NOTICE_ADDED",
    title: `${isRev ? 'Notice Revision Added' : 'New Notice'}: ${title.substring(0, 30)}`,
    message: `Reference: ${refCode} scheduled for ${date} in ${venue}.`,
    timestamp: new Date().toLocaleDateString() + " " + new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}),
    read: false
  });

  persistState();
  alert(`Notice successfully saved with ID: ${newId}! Audit scan triggered.`);
  navigateTo("dashboard");
}

// ---------------------------------------------------------
// Revision Comparison & Diff Engine
// ---------------------------------------------------------
function computeFieldDiffs(oldN, newN) {
  const fields = [
    { key: "title", label: "Notice / Subject Title" },
    { key: "date", label: "Scheduled Date" },
    { key: "start_time", label: "Start Time" },
    { key: "end_time", label: "End Time" },
    { key: "venue", label: "Venue / Room" },
    { key: "department", label: "Issuing Department" },
    { key: "reference_code", label: "Reference Code" }
  ];

  let modifiedFields = [];
  let diffs = fields.map(f => {
    let oldVal = oldN[f.key] || "";
    let newVal = newN[f.key] || "";
    let isMod = oldVal.toString().trim().toLowerCase() !== newVal.toString().trim().toLowerCase();
    if (isMod) modifiedFields.push(f.label);

    return {
      field: f.label,
      oldVal,
      newVal,
      isModified: isMod
    };
  });

  let impactLevel = "LOW";
  if (modifiedFields.includes("Scheduled Date")) impactLevel = "CRITICAL";
  else if (modifiedFields.includes("Venue / Room")) impactLevel = "HIGH";
  else if (modifiedFields.length > 0) impactLevel = "MODERATE";

  return {
    diffs,
    modifiedFields,
    impactLevel,
    summary: `Circular updated across ${modifiedFields.length} field(s): ${modifiedFields.join(", ")}.`
  };
}

function renderRevisionsScreen() {
  const picker = document.getElementById("revisionPicker");
  const revs = state.notices.filter(n => n.is_revision);

  if (revs.length === 0) {
    document.getElementById("diffInspectionContainer").innerHTML = `<p>No revised notices available.</p>`;
    return;
  }

  picker.innerHTML = revs.map(r => `<option value="${r.id}">${r.id}: ${r.title} (${r.reference_code})</option>`).join("");
  renderRevisionDiffView(revs[0].id);
}

function renderRevisionDiffView(revId) {
  const rev = state.notices.find(n => n.id === revId);
  if (!rev) return;
  const parent = state.notices.find(n => n.id === rev.parent_notice_id) || state.notices[0];

  const diffData = computeFieldDiffs(parent, rev);
  const container = document.getElementById("diffInspectionContainer");

  const impactColor = diffData.impactLevel === "CRITICAL" ? "#dc2626" : diffData.impactLevel === "HIGH" ? "#ea580c" : "#2563eb";

  container.innerHTML = `
    <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:16px; margin: 16px 0;">
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <div>
          <span style="font-size:0.75rem; text-transform:uppercase; font-weight:700; color:#64748b;">AMENDMENT AUDIT</span>
          <h3 style="margin:4px 0; color:#0f172a;">${parent.reference_code} (v1) ➔ ${rev.reference_code} (v2)</h3>
        </div>
        <span style="background:${impactColor}15; color:${impactColor}; font-weight:700; padding:4px 10px; border-radius:9999px; font-size:0.85rem;">
          IMPACT: ${diffData.impactLevel}
        </span>
      </div>
      <p style="font-size:0.85rem; color:#334155; margin-top:8px;">💡 ${diffData.summary}</p>
    </div>

    <table class="diff-table">
      <thead>
        <tr>
          <th>Field Name</th>
          <th>Status</th>
          <th>Original Value (v1)</th>
          <th>Revised Value (v2)</th>
        </tr>
      </thead>
      <tbody>
        ${diffData.diffs.map(d => `
          <tr>
            <td style="font-weight:600;">${d.field}</td>
            <td>${d.isModified ? '<span style="background:#fee2e2; color:#991b1b; padding:2px 6px; border-radius:4px; font-size:0.75rem; font-weight:700;">CHANGED</span>' : '<span style="background:#f1f5f9; color:#64748b; padding:2px 6px; border-radius:4px; font-size:0.75rem;">UNCHANGED</span>'}</td>
            <td><span class="${d.isModified ? 'diff-mod-old' : ''}">${d.oldVal}</span></td>
            <td><span class="${d.isModified ? 'diff-mod-new' : ''}">${d.newVal}</span></td>
          </tr>
        `).join("")}
      </tbody>
    </table>
  `;
}

// ---------------------------------------------------------
// Conflict Detection Engine
// ---------------------------------------------------------
function toMins(t) {
  const parts = t.split(":");
  return parseInt(parts[0]) * 60 + parseInt(parts[1]);
}

function calculateConflicts() {
  const active = state.notices.filter(n => n.status !== "SUPERSEDED");
  const conflicts = [];

  for (let i = 0; i < active.length; i++) {
    for (let j = i + 1; j < active.length; j++) {
      const a = active[i];
      const b = active[j];

      if (a.date !== b.date) continue;

      const sA = toMins(a.start_time), eA = toMins(a.end_time);
      const sB = toMins(b.start_time), eB = toMins(b.end_time);

      const oStart = Math.max(sA, sB);
      const oEnd = Math.min(eA, eB);

      if (oStart < oEnd) {
        const dur = oEnd - oStart;
        const normA = a.venue.toLowerCase().replace(/audi-1/g, "auditorium 1").replace(/complex|block|-/g, "").trim();
        const normB = b.venue.toLowerCase().replace(/audi-1/g, "auditorium 1").replace(/complex|block|-/g, "").trim();

        if (normA === normB && normA !== "campus wide") {
          conflicts.push({
            id: `CONF-${a.id}-${b.id}`,
            type: "VENUE_CLASH",
            severity: "CRITICAL",
            date: a.date,
            venue: a.venue,
            overlapWindow: `${Math.floor(oStart/60)}:${String(oStart%60).padStart(2,'0')} to ${Math.floor(oEnd/60)}:${String(oEnd%60).padStart(2,'0')} (${dur} mins)`,
            eventA: a,
            eventB: b,
            explanation: `Simultaneous room booking in '${a.venue}'. '${a.title}' (${a.start_time}-${a.end_time}) and '${b.title}' (${b.start_time}-${b.end_time}) overlap for ${dur} minutes on ${a.date}.`,
            recommendation: `Relocate '${b.title}' to Seminar Hall 2 or postpone start to ${a.end_time}.`
          });
        }
      }
    }
  }
  return conflicts;
}

function auditAllConflicts() {
  const conflicts = calculateConflicts();
  const container = document.getElementById("conflictsListContainer");

  if (conflicts.length === 0) {
    container.innerHTML = `<div style="background:#f0fdf4; border:1px solid #bbf7d0; border-radius:8px; padding:20px; color:#166534; font-weight:600;">✅ Zero Schedule Conflicts Detected! Timetable is fully harmonized.</div>`;
    return;
  }

  container.innerHTML = conflicts.map(c => `
    <div style="background:#ffffff; border:1px solid #fecdd3; border-left:6px solid #e11d48; border-radius:10px; padding:18px; margin-bottom:16px;">
      <div style="display:flex; justify-content:space-between; align-items:flex-start;">
        <div>
          <span class="badge badge-clash">⚠️ ${c.type.replace('_', ' ')}</span>
          <span style="font-size:0.85rem; font-weight:700; color:#881337; margin-left:8px;">ID: ${c.id}</span>
          <h3 style="margin:6px 0; font-size:1.15rem; color:#0f172a;">${c.explanation}</h3>
        </div>
        <span style="background:#ffe4e6; color:#9f1239; font-weight:700; font-size:0.75rem; padding:4px 8px; border-radius:6px;">SEVERITY: ${c.severity}</span>
      </div>

      <div style="display:grid; grid-template-columns: 1fr 1fr; gap:16px; margin:14px 0; background:#fff1f2; padding:12px; border-radius:8px;">
        <div>
          <div style="font-size:0.75rem; font-weight:700; color:#9f1239;">FIRST EVENT:</div>
          <div style="font-weight:600; color:#1e293b;">${c.eventA.title}</div>
          <div style="font-size:0.8rem; color:#475569;">⏰ ${c.eventA.start_time} - ${c.eventA.end_time} at <code>${c.eventA.venue}</code></div>
        </div>
        <div>
          <div style="font-size:0.75rem; font-weight:700; color:#9f1239;">CLASHING EVENT:</div>
          <div style="font-weight:600; color:#1e293b;">${c.eventB.title}</div>
          <div style="font-size:0.8rem; color:#475569;">⏰ ${c.eventB.start_time} - ${c.eventB.end_time} at <code>${c.eventB.venue}</code></div>
        </div>
      </div>

      <div style="background:#f0fdf4; border:1px solid #bbf7d0; border-radius:6px; padding:10px; font-size:0.85rem; color:#166534;">
        <strong>💡 Automated Solution:</strong> ${c.recommendation}
      </div>
    </div>
  `).join("");
}

// ---------------------------------------------------------
// Exam Timetable Renderer & Filter
// ---------------------------------------------------------
function renderExamsScreen() {
  const depts = ["ALL", ...new Set(state.exams.map(e => e.department))];
  const deptSelect = document.getElementById("examDeptFilter");
  deptSelect.innerHTML = depts.map(d => `<option value="${d}">${d === 'ALL' ? 'All Departments' : d}</option>`).join("");
  filterExamTable();
}

function filterExamTable() {
  const q = (document.getElementById("examTableFilter").value || "").toLowerCase();
  const dept = document.getElementById("examDeptFilter").value;

  const filtered = state.exams.filter(ex => {
    const matchQ = ex.course_code.toLowerCase().includes(q) || ex.course_title.toLowerCase().includes(q) || ex.venue.toLowerCase().includes(q);
    const matchDept = dept === "ALL" || ex.department === dept;
    return matchQ && matchDept;
  });

  const tbody = document.getElementById("masterExamTableBody");
  tbody.innerHTML = filtered.map(ex => `
    <tr>
      <td><strong>${ex.course_code}</strong></td>
      <td>${ex.course_title}</td>
      <td>${ex.exam_type}</td>
      <td>${ex.department}</td>
      <td>${ex.date}</td>
      <td>${ex.start_time} - ${ex.end_time}</td>
      <td>${ex.venue}</td>
      <td>${ex.total_students}</td>
      <td>${ex.conflict_flag ? '<span class="badge badge-clash">⚠️ CLASH</span>' : '<span class="badge badge-active">CONFIRMED</span>'}</td>
    </tr>
  `).join("");
}

function exportExamsCSV() {
  let csv = "Course Code,Course Title,Type,Department,Date,Start Time,End Time,Venue,Students,Status\n";
  state.exams.forEach(ex => {
    csv += `"${ex.course_code}","${ex.course_title}","${ex.exam_type}","${ex.department}","${ex.date}","${ex.start_time}","${ex.end_time}","${ex.venue}",${ex.total_students},"${ex.status}"\n`;
  });

  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `academic_exam_timetable_2026.csv`;
  a.click();
}

// ---------------------------------------------------------
// Academic Assistant Chatbot
// ---------------------------------------------------------
function handleChatSubmit(event) {
  event.preventDefault();
  const input = document.getElementById("chatInputText");
  const text = input.value.trim();
  if (!text) return;

  sendChatMessage(text);
  input.value = "";
}

function sendChatMessage(text) {
  const chatList = document.getElementById("chatMessageList");

  // User Bubble
  chatList.innerHTML += `<div class="chat-bubble user">${text}</div>`;

  // Bot Answer
  const answer = generateBotResponse(text);
  setTimeout(() => {
    chatList.innerHTML += `<div class="chat-bubble bot">${answer}</div>`;
    chatList.scrollTop = chatList.scrollHeight;
  }, 200);
}

function generateBotResponse(q) {
  const query = q.toLowerCase();
  const conflicts = calculateConflicts();

  if (query.includes("clash") || query.includes("conflict") || query.includes("overlap")) {
    if (conflicts.length === 0) return "✅ <strong>No Conflicts Found</strong>: All scheduled exams and academic events have separate rooms and time windows.";
    return `⚠️ <strong>Attention: ${conflicts.length} Conflict(s) Detected</strong>:<br>
    • <strong>Auditorium 1 Venue Collision:</strong> CS301 Revised Exam and AI Symposium are both scheduled on 2026-10-24 during 11:00 AM - 12:30 PM.<br>
    💡 <em>Recommended Solution: Relocate AI Symposium to Seminar Hall 2.</em>`;
  }

  if (query.includes("cs301")) {
    return `📋 <strong>CS301 Data Structures & Algorithms</strong>:<br>
    • <strong>Date:</strong> 2026-10-24<br>
    • <strong>Hours:</strong> 10:30 AM to 12:30 PM (Amended in Revision v2)<br>
    • <strong>Venue:</strong> Auditorium 1 - Main Complex<br>
    • <strong>Warning:</strong> Venue collision with AI Symposium flagged in Auditorium 1.`;
  }

  if (query.includes("revis") || query.includes("amend") || query.includes("changed")) {
    return `🔄 <strong>Notice Revision History</strong>:<br>
    • <strong>CS301 Midterm Notice</strong> was amended from Ref <code>CSE/EXAM/2026/01</code> (v1) to <code>CSE/EXAM/2026/01-R1</code> (v2).<br>
    • <strong>Changes:</strong> Start Time moved from 10:00 to 10:30 AM; Venue relocated from Hall B to Auditorium 1.`;
  }

  if (query.includes("holiday") || query.includes("break") || query.includes("oct 28")) {
    return `🌴 <strong>University Holiday Notice (Ref: CAC/CIR/2026/19)</strong>:<br>
    • <strong>Date:</strong> 2026-10-28<br>
    • <strong>Scope:</strong> Campus-Wide Autumn Break. All departmental exams must be rescheduled.`;
  }

  return `🤖 <strong>Campus Connect Assistant Response:</strong><br>
  I analyzed all <strong>${state.notices.length} registered circulars</strong> and <strong>${state.exams.length} examinations</strong>.<br>
  You can ask me about specific course exam dates (e.g. <em>CS301, EE204</em>), venue bookings, circular revisions, or schedule clash reports!`;
}

function runQuickQuery(val) {
  if (!val) return;
  const resDiv = document.getElementById("quickDashboardResult");
  resDiv.style.display = "block";
  resDiv.innerHTML = generateBotResponse(val);
}

// ---------------------------------------------------------
// Notifications Screen
// ---------------------------------------------------------
function renderNotificationsScreen() {
  const container = document.getElementById("notificationsContainer");
  container.innerHTML = state.notifications.map(n => `
    <div style="background:${n.read ? '#ffffff' : '#f8fafc'}; border:1px solid ${n.read ? '#e2e8f0' : '#93c5fd'}; border-radius:8px; padding:12px; margin-bottom:10px;">
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <div>
          <span class="badge ${n.type.includes('CONFLICT') ? 'badge-clash' : 'badge-revised'}">${n.type.replace('_', ' ')}</span>
          <strong style="font-size:0.88rem; color:#0f172a; margin-left:6px;">${n.title}</strong>
        </div>
        <span style="font-size:0.75rem; color:#64748b;">${n.timestamp}</span>
      </div>
      <p style="font-size:0.82rem; color:#334155; margin-top:6px;">${n.message}</p>
    </div>
  `).join("");
}

function markAllNotificationsRead() {
  state.notifications.forEach(n => n.read = true);
  persistState();
  renderNotificationsScreen();
  renderDashboard();
}

function handleGlobalSearch(e) {
  if (e.key === "Enter") {
    const q = e.target.value.trim();
    if (!q) return;
    navigateTo("exams");
    document.getElementById("examTableFilter").value = q;
    filterExamTable();
  }
}

// Boot up app on page load
function initApp() {
  renderDashboard();
}

window.addEventListener("DOMContentLoaded", initApp);
