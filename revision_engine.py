"""
Campus Connect - Revision History & Field-by-Field Diff Comparison Engine
Analyzes differences between notice versions, categorizes change types,
and calculates student/faculty impact severity.
"""

from typing import Dict, Any, List, Optional


COMPARABLE_FIELDS = [
    {"key": "title", "label": "Event / Notice Title", "weight": 2},
    {"key": "date", "label": "Scheduled Date", "weight": 5},
    {"key": "start_time", "label": "Start Time", "weight": 3},
    {"key": "end_time", "label": "End Time", "weight": 3},
    {"key": "venue", "label": "Venue / Room", "weight": 4},
    {"key": "department", "label": "Issuing Department", "weight": 2},
    {"key": "reference_code", "label": "Administrative Reference", "weight": 1},
    {"key": "version", "label": "Notice Version Number", "weight": 1},
]


def compare_notice_versions(old_notice: Dict[str, Any], new_notice: Dict[str, Any]) -> Dict[str, Any]:
    """
    Performs field-by-field comparison between an original notice and its revised counterpart.
    Returns:
        {
            "field_diffs": [
                {
                    "field_key": str,
                    "field_label": str,
                    "old_value": Any,
                    "new_value": Any,
                    "status": "MODIFIED" | "UNCHANGED" | "ADDED" | "REMOVED",
                    "impact_severity": "HIGH" | "MEDIUM" | "LOW" | "NONE"
                }, ...
            ],
            "total_changes": int,
            "modified_fields": List[str],
            "impact_level": "CRITICAL" | "HIGH" | "MODERATE" | "LOW" | "NO CHANGE",
            "advisory_summary": str
        }
    """
    field_diffs = []
    total_impact_score = 0
    modified_field_names = []

    for field in COMPARABLE_FIELDS:
        key = field["key"]
        label = field["label"]
        weight = field["weight"]

        old_val = str(old_notice.get(key, "")).strip()
        new_val = str(new_notice.get(key, "")).strip()

        if not old_val and new_val:
            status = "ADDED"
            severity = "MEDIUM"
            total_impact_score += weight
            modified_field_names.append(label)
        elif old_val and not new_val:
            status = "REMOVED"
            severity = "MEDIUM"
            total_impact_score += weight
            modified_field_names.append(label)
        elif old_val.lower() != new_val.lower():
            status = "MODIFIED"
            if key in ["date", "venue"]:
                severity = "HIGH"
            elif key in ["start_time", "end_time"]:
                severity = "MEDIUM"
            else:
                severity = "LOW"
            total_impact_score += weight
            modified_field_names.append(label)
        else:
            status = "UNCHANGED"
            severity = "NONE"

        field_diffs.append({
            "field_key": key,
            "field_label": label,
            "old_value": old_val if old_val else "(empty)",
            "new_value": new_val if new_val else "(empty)",
            "status": status,
            "impact_severity": severity
        })

    # Determine overall impact level
    total_changes = len(modified_field_names)
    if any(d["field_key"] == "date" and d["status"] == "MODIFIED" for d in field_diffs):
        impact_level = "CRITICAL"
    elif any(d["field_key"] in ["venue", "start_time"] and d["status"] == "MODIFIED" for d in field_diffs):
        impact_level = "HIGH"
    elif total_changes > 0:
        impact_level = "MODERATE"
    else:
        impact_level = "NO CHANGE"

    # Construct human-readable advisory summary
    if total_changes == 0:
        advisory_summary = "Both notice versions are identical in core scheduling and venue fields."
    else:
        advisory_summary = (
            f"Notice revision detected with {total_changes} altered field(s): {', '.join(modified_field_names)}. "
        )
        if "Scheduled Date" in modified_field_names:
            advisory_summary += "CRITICAL ALERT: Date modification impacts student calendar and attendance plans. "
        if "Venue / Room" in modified_field_names:
            advisory_summary += f"Venue relocated from '{old_notice.get('venue')}' to '{new_notice.get('venue')}'. Room capacity and conflict checks required. "
        if "Start Time" in modified_field_names or "End Time" in modified_field_names:
            advisory_summary += f"Session hours updated to {new_notice.get('start_time')} - {new_notice.get('end_time')}."

    return {
        "old_notice_id": old_notice.get("id", "Unknown"),
        "new_notice_id": new_notice.get("id", "Unknown"),
        "old_ref": old_notice.get("reference_code", "Unknown"),
        "new_ref": new_notice.get("reference_code", "Unknown"),
        "old_version": old_notice.get("version", 1),
        "new_version": new_notice.get("version", 2),
        "field_diffs": field_diffs,
        "total_changes": total_changes,
        "modified_fields": modified_field_names,
        "impact_score": total_impact_score,
        "impact_level": impact_level,
        "advisory_summary": advisory_summary
    }
