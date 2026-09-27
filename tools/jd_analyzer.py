"""
NEXUS AI 2.0 - Job Description Analyzer Tool
Parses target job postings, extracts skill requirements, matches against user profile,
computes gap score, and recommends targeted study topics.
"""

import json
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from utils.helpers import normalize_skill
from utils.logger import logger
from tools.resume_analyzer import KNOWN_SKILLS_TAXONOMY

def analyze_job_description(
    job_title: str,
    jd_text: str,
    user_skills: List[str],
    db: Optional[Session] = None,
    user_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Parses job description text and computes gap match score against user's current skills.
    """
    logger.info(f"Analyzing Job Description '{job_title}' against {len(user_skills)} user skills.")

    jd_lower = jd_text.lower()
    norm_user_skills = {normalize_skill(s): s for s in user_skills}

    # Extract required skills from JD
    extracted_reqs = []
    for skill in KNOWN_SKILLS_TAXONOMY:
        if normalize_skill(skill) in jd_lower or skill.lower() in jd_lower:
            extracted_reqs.append(skill)

    # Calculate matches vs user skills
    matched = []
    missing = []

    for req in extracted_reqs:
        req_norm = normalize_skill(req)
        if req_norm in norm_user_skills:
            matched.append(norm_user_skills[req_norm])
        else:
            missing.append(req)

    total_extracted = len(extracted_reqs)
    if total_extracted > 0:
        match_percentage = round((len(matched) / total_extracted) * 100.0, 1)
    else:
        match_percentage = 65.0

    gap_report = []
    for miss in missing:
        gap_report.append(f"Add practice project or module for {miss}")

    result = {
        "job_title": job_title,
        "match_percentage": min(match_percentage, 100.0),
        "extracted_requirements": extracted_reqs,
        "matched_user_skills": matched,
        "missing_skills": missing,
        "actionable_gaps": gap_report,
        "fit_tier": "High Fit" if match_percentage >= 75 else ("Moderate Fit" if match_percentage >= 45 else "Bridge Needed")
    }

    # Persist to database if provided
    if db and user_id:
        try:
            from database.models import JobDescription
            new_jd = JobDescription(
                user_id=user_id,
                title=job_title,
                raw_text=jd_text,
                extracted_reqs_json=json.dumps(extracted_reqs),
                match_percentage=result["match_percentage"],
                gap_analysis_json=json.dumps(result)
            )
            db.add(new_jd)
            db.commit()
            logger.info(f"Persisted Job Description analysis to DB for user_id={user_id}")
        except Exception as e:
            logger.error(f"Error persisting JD analysis: {e}")

    return result
