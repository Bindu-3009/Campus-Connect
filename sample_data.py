"""
Campus Connect - Sample Academic Notices & Demo Dataset
Clearly labeled as [SAMPLE / DEMO DATA] for ethical demonstration and evaluation.
"""

SAMPLE_NOTICES = [
    {
        "id": "NOT-2026-001",
        "title": "CS301: Data Structures Midterm Examination (Original)",
        "reference_code": "CSE/EXAM/2026/01",
        "version": 1,
        "is_revision": False,
        "parent_notice_id": None,
        "department": "Computer Science & Engineering",
        "category": "Examination",
        "date": "2026-10-24",
        "start_time": "10:00",
        "end_time": "12:00",
        "venue": "Hall B - Newton Block",
        "raw_text": """OFFICE OF THE CONTROLLER OF EXAMINATIONS
DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING
Ref: CSE/EXAM/2026/01                                    Date: 2026-10-10

NOTICE: MIDTERM EXAMINATION SCHEDULE (OCTOBER 2026)

All 3rd Year B.Tech Computer Science students are hereby notified that the
Midterm Examination for CS301 (Data Structures & Algorithms) is scheduled as below:

- Event: CS301 Midterm Examination
- Date: 2026-10-24 (Saturday)
- Time: 10:00 AM to 12:00 PM
- Venue: Hall B - Newton Block
- Reporting Time: 09:30 AM
- Permitted Materials: Non-programmable Scientific Calculators only.

Students must carry their valid University Smart Cards.

Sd/-
Dr. Sarah Jenkins
Head, Department of Computer Science & Engineering""",
        "status": "SUPERSEDED",
        "is_sample": True,
        "notes": "Original notice; later amended due to venue capacity upgrade."
    },
    {
        "id": "NOT-2026-002",
        "title": "CS301: Data Structures Midterm Examination (REVISED v2)",
        "reference_code": "CSE/EXAM/2026/01-R1",
        "version": 2,
        "is_revision": True,
        "parent_notice_id": "NOT-2026-001",
        "department": "Computer Science & Engineering",
        "category": "Examination",
        "date": "2026-10-24",
        "start_time": "10:30",
        "end_time": "12:30",
        "venue": "Auditorium 1 - Main Complex",
        "raw_text": """OFFICE OF THE CONTROLLER OF EXAMINATIONS
DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING
Ref: CSE/EXAM/2026/01-R1                                 Date: 2026-10-15

REVISED NOTICE: CS301 MIDTERM SCHEDULE AMENDMENT

In partial modification of previous notice Ref: CSE/EXAM/2026/01 dated 2026-10-10,
please note the following revisions for CS301 (Data Structures & Algorithms) due to
higher student enrollment and lab seating restructuring:

- Event: CS301 Midterm Examination
- Date: 2026-10-24 (Unchanged)
- Time: 10:30 AM to 12:30 PM (Modified: Shifted by 30 minutes)
- Venue: Auditorium 1 - Main Complex (Modified: Shifted from Hall B)
- Instructions: Seating arrangement will be posted at the Auditorium entrance.

All other terms and guidelines remain unchanged.

Sd/-
Dr. Sarah Jenkins
Head, Department of Computer Science & Engineering""",
        "status": "ACTIVE",
        "is_sample": True,
        "notes": "Revision modifies Start Time, End Time, and Venue to Auditorium 1."
    },
    {
        "id": "NOT-2026-003",
        "title": "AI & Robotics Society: Annual AI Symposium & Keynote",
        "reference_code": "AIR/SYM/2026/11",
        "version": 1,
        "is_revision": False,
        "parent_notice_id": None,
        "department": "Interdisciplinary Robotics & AI Cell",
        "category": "Guest Lecture & Seminar",
        "date": "2026-10-24",
        "start_time": "11:00",
        "end_time": "13:30",
        "venue": "Auditorium 1 - Main Complex",
        "raw_text": """INTERDISCIPLINARY ROBOTICS & AI CELL (AIR)
Ref: AIR/SYM/2026/11                                     Date: 2026-10-12

CIRCULAR: ANNUAL AI KEYNOTE & ROBOTICS EXHIBITION

All engineering students and faculty members are cordially invited to the
Annual Symposium on Frontier Artificial Intelligence featuring distinguished
visiting speakers:

- Event: Annual AI Symposium & Keynote
- Date: 2026-10-24
- Time: 11:00 AM to 01:30 PM
- Venue: Auditorium 1 - Main Complex
- Chief Guest: Prof. Alan Vance (AI Research Institute)

Lunch will be served at 01:45 PM for registered attendees.

Sd/-
Prof. Vikram Nair
Faculty Advisor, AIR Cell""",
        "status": "ACTIVE",
        "is_sample": True,
        "notes": "Direct venue clash with CS301 Revised Exam in Auditorium 1 between 11:00 AM and 12:30 PM!"
    },
    {
        "id": "NOT-2026-004",
        "title": "EE204: Electrical Machines Laboratory Viva-Voce",
        "reference_code": "EEE/LAB/2026/04",
        "version": 1,
        "is_revision": False,
        "parent_notice_id": None,
        "department": "Electrical & Electronics Engineering",
        "category": "Laboratory Exam",
        "date": "2026-10-25",
        "start_time": "09:00",
        "end_time": "13:00",
        "venue": "Electrical Machines Lab - EEE Block",
        "raw_text": """DEPARTMENT OF ELECTRICAL & ELECTRONICS ENGINEERING
Ref: EEE/LAB/2026/04                                     Date: 2026-10-14

NOTICE: EE204 ELECTRICAL MACHINES COMPREHENSIVE VIVA

All 2nd Year Electrical Engineering students must attend the mandatory Viva-Voce
assessment as per the timetable below:

- Event: EE204 Laboratory Viva-Voce
- Date: 2026-10-25
- Time: 09:00 AM to 01:00 PM
- Venue: Electrical Machines Lab - EEE Block
- Batches: Batch A1 (09:00-11:00) & Batch A2 (11:00-13:00)

Wear prescribed lab coats and safety footwear.

Sd/-
Prof. M. R. Kulkarni
Course Coordinator""",
        "status": "ACTIVE",
        "is_sample": True,
        "notes": "No conflict; running smoothly."
    },
    {
        "id": "NOT-2026-005",
        "title": "ME305: Mechanical Thermodynamics Tutorial & Class Test",
        "reference_code": "MECH/TEST/2026/09",
        "version": 1,
        "is_revision": False,
        "parent_notice_id": None,
        "department": "Mechanical Engineering",
        "category": "Class Test",
        "date": "2026-10-26",
        "start_time": "14:00",
        "end_time": "16:00",
        "venue": "Seminar Hall 2 - Mechanical Block",
        "raw_text": """DEPARTMENT OF MECHANICAL ENGINEERING
Ref: MECH/TEST/2026/09                                   Date: 2026-10-16

ANNOUNCEMENT: ME305 APPLIED THERMODYNAMICS SURPRISE TEST

The 3rd Year Mechanical Engineering students are advised that the assessment
and tutorial session will take place as follows:

- Event: ME305 Applied Thermodynamics Tutorial & Test
- Date: 2026-10-26
- Time: 02:00 PM to 04:00 PM (14:00 to 16:00)
- Venue: Seminar Hall 2 - Mechanical Block
- Topics: Rankine Cycle, Steam Turbines, Refrigeration.

Attendance is compulsory.

Sd/-
Dr. H. C. Verma
Dean, Mechanical Sciences""",
        "status": "ACTIVE",
        "is_sample": True,
        "notes": "Clear timetable slot."
    },
    {
        "id": "NOT-2026-006",
        "title": "Central Academic Council: Fall Mid-Semester Holiday Schedule",
        "reference_code": "CAC/CIR/2026/19",
        "version": 1,
        "is_revision": False,
        "parent_notice_id": None,
        "department": "Central Academic Administration",
        "category": "General Administrative Circular",
        "date": "2026-10-28",
        "start_time": "08:00",
        "end_time": "20:00",
        "venue": "Campus-Wide",
        "raw_text": """CENTRAL ACADEMIC ADMINISTRATION
Ref: CAC/CIR/2026/19                                     Date: 2026-10-16

CIRCULAR: AUTUMN BREAK & REVISED WORKING SATURDAYS

In accordance with the Academic Council Resolution No. 44, the university will
observe Autumn Break on 2026-10-28. No examinations or formal lectures shall
be scheduled on this date across all undergraduate and postgraduate schools.

- Event: Autumn University Holiday
- Date: 2026-10-28
- Time: 08:00 AM to 08:00 PM
- Venue: Campus-Wide

Any departmental test scheduled on 2026-10-28 must be rescheduled with immediate notice.

Sd/-
Registrar & Secretary to the Academic Council""",
        "status": "ACTIVE",
        "is_sample": True,
        "notes": "Campus-wide holiday circular."
    }
]

SAMPLE_EXAMS = [
    {
        "course_code": "CS301",
        "course_title": "Data Structures & Algorithms",
        "exam_type": "Midterm",
        "department": "Computer Science & Engineering",
        "date": "2026-10-24",
        "start_time": "10:30",
        "end_time": "12:30",
        "venue": "Auditorium 1 - Main Complex",
        "invigilator": "Dr. Sarah Jenkins",
        "total_students": 140,
        "status": "SCHEDULED (REVISED)",
        "conflict_flag": True,
        "conflict_reason": "Clash with Annual AI Symposium in Auditorium 1"
    },
    {
        "course_code": "EE204",
        "course_title": "Electrical Machines Lab Viva",
        "exam_type": "Lab Viva",
        "department": "Electrical & Electronics Engineering",
        "date": "2026-10-25",
        "start_time": "09:00",
        "end_time": "13:00",
        "venue": "Electrical Machines Lab - EEE Block",
        "invigilator": "Prof. M. R. Kulkarni",
        "total_students": 65,
        "status": "CONFIRMED",
        "conflict_flag": False,
        "conflict_reason": "None"
    },
    {
        "course_code": "ME305",
        "course_title": "Applied Thermodynamics Test",
        "exam_type": "Class Assessment",
        "department": "Mechanical Engineering",
        "date": "2026-10-26",
        "start_time": "14:00",
        "end_time": "16:00",
        "venue": "Seminar Hall 2 - Mechanical Block",
        "invigilator": "Dr. H. C. Verma",
        "total_students": 92,
        "status": "CONFIRMED",
        "conflict_flag": False,
        "conflict_reason": "None"
    },
    {
        "course_code": "MA201",
        "course_title": "Linear Algebra & Probability",
        "exam_type": "Midterm",
        "department": "Mathematics & Data Science",
        "date": "2026-10-27",
        "start_time": "10:00",
        "end_time": "12:00",
        "venue": "Lecture Hall Complex Room 101",
        "invigilator": "Dr. Angela Merkel",
        "total_students": 180,
        "status": "CONFIRMED",
        "conflict_flag": False,
        "conflict_reason": "None"
    },
    {
        "course_code": "PH102",
        "course_title": "Engineering Physics Electromagnetics",
        "exam_type": "Midterm",
        "department": "Physics & Nanotechnology",
        "date": "2026-10-29",
        "start_time": "14:00",
        "end_time": "16:00",
        "venue": "Physics Hall A",
        "invigilator": "Prof. Richard Feynman",
        "total_students": 110,
        "status": "CONFIRMED",
        "conflict_flag": False,
        "conflict_reason": "None"
    }
]

SAMPLE_NOTIFICATIONS = [
    {
        "id": "NOTIF-01",
        "type": "CRITICAL_CONFLICT",
        "title": "Severe Venue Clash Detected!",
        "message": "CS301 Revised Exam and AI Symposium are both booked in Auditorium 1 on 2026-10-24 during 11:00 AM - 12:30 PM.",
        "timestamp": "2026-10-17 10:15 AM",
        "read": False,
        "action_url": "conflicts",
        "is_sample": True
    },
    {
        "id": "NOTIF-02",
        "type": "REVISION_ALERT",
        "title": "Notice Revision Tracked: CS301 Midterm",
        "message": "Notice Ref: CSE/EXAM/2026/01 amended to CSE/EXAM/2026/01-R1. Venue modified to Auditorium 1; start time delayed by 30 mins.",
        "timestamp": "2026-10-15 04:30 PM",
        "read": True,
        "action_url": "revisions",
        "is_sample": True
    },
    {
        "id": "NOTIF-03",
        "type": "CALENDAR_ALERT",
        "title": "Autumn Holiday Scheduled",
        "message": "Academic Council declared 2026-10-28 as University Autumn Holiday. Department assessments must be rescheduled.",
        "timestamp": "2026-10-16 02:00 PM",
        "read": True,
        "action_url": "exams",
        "is_sample": True
    }
]
