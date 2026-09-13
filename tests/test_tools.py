"""
NEXUS AI Agent - Phase 2 Tool Tests
Verifies skill_analyzer and skill_gap_analyzer tool logic, skill status classifications, and report generation.
"""

import pytest
from tools.skill_analyzer import analyze_skills
from tools.skill_gap_analyzer import identify_skill_gaps

def test_skill_analyzer_ai_engineer():
    """Test skill analyzer logic for AI Engineer target role."""
    current_skills = ["Java", "HTML", "CSS", "JavaScript", "Machine Learning"]
    target_role = "AI Engineer"

    result = analyze_skills(current_skills, target_role)

    assert result["target_role"] == "AI Engineer"
    assert "Machine Learning" in result["completed_skills"]
    assert "Python" in result["missing_skills"]
    assert "Deep Learning" in result["missing_skills"]
    assert "LLMs" in result["missing_skills"]
    assert result["readiness_score_percentage"] > 0.0

def test_skill_gap_analyzer_report_generation():
    """Test skill gap report generation and textual summary format."""
    current_skills = ["Java", "Machine Learning"]
    target_role = "AI Engineer"

    gap_output = identify_skill_gaps(current_skills, target_role)

    assert "report" in gap_output
    assert "summary" in gap_output

    report = gap_output["report"]
    assert report["target_role"] == "AI Engineer"
    assert len(report["missing_skills"]) > 0
    assert "Python" in report["missing_skills"]

    summary = gap_output["summary"]
    assert "Skill Gap Analysis for AI Engineer" in summary
    assert "Missing Core Skills" in summary
    assert "Python" in summary

def test_skill_analyzer_unknown_role_fallback():
    """Test fallback handling for custom or uncataloged target roles."""
    current_skills = ["Python"]
    target_role = "Quantum Software Engineer"

    result = analyze_skills(current_skills, target_role)

    assert result["target_role"] == "Quantum Software Engineer"
    assert "Python" in result["completed_skills"]
    assert len(result["missing_skills"]) > 0
