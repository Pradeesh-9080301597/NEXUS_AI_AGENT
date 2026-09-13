"""
NEXUS AI Agent - Skill Gap Analyzer Tool
Generates structured skill gap reports explaining why missing skills are critical for target roles.
"""

from typing import List, Dict, Any
from tools.skill_analyzer import analyze_skills
from utils.helpers import get_career_details
from schemas.roadmap import SkillGapReport, SkillItemStatus
from utils.logger import logger

def identify_skill_gaps(
    current_skills: List[str],
    target_role: str,
    in_progress_skills: List[str] = None
) -> Dict[str, Any]:
    """
    Identifies skill gaps and constructs a detailed SkillGapReport.
    
    Provides explicit justifications for why each missing or in-progress skill is vital.
    """
    if in_progress_skills is None:
        in_progress_skills = []

    logger.info(f"Generating skill gap report for role '{target_role}'")

    raw_analysis = analyze_skills(current_skills, target_role, in_progress_skills)
    career_info = get_career_details(target_role)
    importance_map = career_info.get("skill_importance", {})

    skill_details: List[SkillItemStatus] = []

    # Completed Skills
    for skill in raw_analysis["completed_skills"]:
        reason = importance_map.get(skill, "Existing skill aligned with role requirements.")
        skill_details.append(SkillItemStatus(
            skill_name=skill,
            status="COMPLETED",
            importance_reason=f"Existing skill: {reason}"
        ))

    # In Progress Skills
    for skill in raw_analysis["in_progress_skills"]:
        reason = importance_map.get(skill, "Actively being acquired.")
        skill_details.append(SkillItemStatus(
            skill_name=skill,
            status="IN_PROGRESS",
            importance_reason=f"Currently learning: {reason}"
        ))

    # Missing Skills
    for skill in raw_analysis["missing_skills"]:
        reason = importance_map.get(skill, "Critical core requirement for career proficiency.")
        skill_details.append(SkillItemStatus(
            skill_name=skill,
            status="MISSING",
            importance_reason=f"Missing core skill: {reason}"
        ))

    report = SkillGapReport(
        target_role=target_role,
        total_required_skills=raw_analysis["total_required_skills"],
        completed_skills=raw_analysis["completed_skills"],
        in_progress_skills=raw_analysis["in_progress_skills"],
        missing_skills=raw_analysis["missing_skills"],
        optional_skills=raw_analysis["optional_skills"],
        readiness_score_percentage=raw_analysis["readiness_score_percentage"],
        skill_details=skill_details
    )

    logger.info(f"Skill gap analysis generated successfully for '{target_role}'")

    return {
        "report": report.model_dump(),
        "summary": _format_gap_summary(report)
    }

def _format_gap_summary(report: SkillGapReport) -> str:
    """Formats the skill gap report into a clear, readable text summary."""
    lines = [
        f"🎯 **Skill Gap Analysis for {report.target_role}**",
        f"📊 **Career Readiness Score**: {report.readiness_score_percentage}%\n",
        f"✅ **Completed Skills ({len(report.completed_skills)})**: {', '.join(report.completed_skills) if report.completed_skills else 'None'}",
        f"⏳ **In-Progress Skills ({len(report.in_progress_skills)})**: {', '.join(report.in_progress_skills) if report.in_progress_skills else 'None'}",
        f"❌ **Missing Core Skills ({len(report.missing_skills)})**: {', '.join(report.missing_skills) if report.missing_skills else 'None'}\n",
        "💡 **Key Missing Skill Insights & Importance**:"
    ]

    missing_items = [item for item in report.skill_details if item.status == "MISSING"]
    if missing_items:
        for item in missing_items:
            lines.append(f"  • **{item.skill_name}**: {item.importance_reason}")
    else:
        lines.append("  🎉 You possess all primary core skills required for this career path!")

    return "\n".join(lines)
