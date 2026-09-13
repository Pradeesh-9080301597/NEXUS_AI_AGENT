"""
NEXUS AI Agent - Skill Analyzer Tool
Analyzes current user skills against target career role specifications.
Classifies skills as COMPLETED, IN_PROGRESS, MISSING, or OPTIONAL.
"""

from typing import List, Dict, Any
from utils.helpers import get_career_details, normalize_skill, format_skill_list
from utils.logger import logger

def analyze_skills(
    current_skills: List[str], 
    target_role: str,
    in_progress_skills: List[str] = None
) -> Dict[str, Any]:
    """
    Compares user's current skills against required/optional skills for a target career role.
    
    Returns a dictionary containing:
    - target_role
    - completed_skills
    - in_progress_skills
    - missing_skills
    - optional_skills
    - readiness_score_percentage
    """
    if in_progress_skills is None:
        in_progress_skills = []

    logger.info(f"Analyzing skills for target role: '{target_role}' with current skills: {current_skills}")

    career_info = get_career_details(target_role)
    required_skills = career_info.get("required_skills", [])
    optional_skills = career_info.get("optional_skills", [])

    norm_current = {normalize_skill(s): s for s in current_skills}
    norm_in_progress = {normalize_skill(s): s for s in in_progress_skills}

    completed = []
    missing = []
    in_prog = []
    opt = []

    # Classify required skills
    for req in required_skills:
        req_norm = normalize_skill(req)
        if req_norm in norm_current:
            completed.append(norm_current[req_norm])
        elif req_norm in norm_in_progress:
            in_prog.append(norm_in_progress[req_norm])
        else:
            missing.append(req)

    # Classify optional skills
    for opt_skill in optional_skills:
        opt_norm = normalize_skill(opt_skill)
        if opt_norm in norm_current or opt_norm in norm_in_progress:
            opt.append(f"{opt_skill} (Acquired)")
        else:
            opt.append(f"{opt_skill} (Recommended)")

    total_required = len(required_skills)
    completed_count = len(completed) + (0.5 * len(in_prog))
    readiness_score = round((completed_count / total_required * 100), 1) if total_required > 0 else 0.0

    result = {
        "target_role": target_role,
        "description": career_info.get("description", ""),
        "total_required_skills": total_required,
        "completed_skills": format_skill_list(completed),
        "in_progress_skills": format_skill_list(in_prog),
        "missing_skills": format_skill_list(missing),
        "optional_skills": format_skill_list(opt),
        "readiness_score_percentage": min(readiness_score, 100.0)
    }

    logger.info(f"Skill analysis complete for {target_role}. Readiness: {readiness_score}%")
    return result
