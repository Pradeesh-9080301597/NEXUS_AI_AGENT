"""
NEXUS AI Agent - Project Recommender Tool
Recommends hands-on portfolio projects aligned with the user's target career role and skill level.
"""

from typing import List, Dict, Any, Optional
from utils.logger import logger

PROJECT_CATALOG: Dict[str, List[Dict[str, Any]]] = {
    "AI Engineer": [
        {
            "title": "Smart CLI Resume & Skill Extractor",
            "description": "Build a Python command-line utility that extracts skills from text files and categorizes them against target job descriptions.",
            "required_skills": "Python, File I/O, Regex",
            "level": "BEGINNER",
            "outcome": "Master Python string parsing, file handling, and basic text classification."
        },
        {
            "title": "Predictive Customer Churn Classifier",
            "description": "Develop a machine learning pipeline using Scikit-Learn to predict customer churn based on behavioral data.",
            "required_skills": "Python, NumPy, Pandas, Machine Learning",
            "level": "INTERMEDIATE",
            "outcome": "Gain practical experience in data preprocessing, feature scaling, model training, and metric evaluation."
        },
        {
            "title": "RAG-Powered AI Documentation Assistant",
            "description": "Construct an end-to-end Retrieval-Augmented Generation application using FastAPI, vector embeddings, and LLM APIs.",
            "required_skills": "Python, LLMs, Generative AI, APIs, Vector DBs",
            "level": "ADVANCED",
            "outcome": "Learn production AI agent architecture, vector similarity search, API orchestration, and container deployment."
        }
    ],
    "Data Scientist": [
        {
            "title": "Exploratory Data Analysis on E-Commerce Sales",
            "description": "Perform comprehensive statistical analysis and data visualization on customer purchasing patterns.",
            "required_skills": "Python, Pandas, Data Visualization, Statistics",
            "level": "BEGINNER",
            "outcome": "Master data cleaning, trend visualization, and statistical correlation analysis."
        },
        {
            "title": "SQL & Python Sales Analytics Pipeline",
            "description": "Build a pipeline connecting SQL database relational schema with Python modeling for automated business reports.",
            "required_skills": "Python, SQL, Pandas, Matplotlib",
            "level": "INTERMEDIATE",
            "outcome": "Bridge database querying with analytical programming and automated reporting."
        },
        {
            "title": "Customer Segmentation & Lifetime Value Predictor",
            "description": "Implement K-Means clustering and predictive regression models for high-value customer targeting.",
            "required_skills": "Python, Machine Learning, Statistics, Scikit-Learn",
            "level": "ADVANCED",
            "outcome": "Deploy production data science models to solve complex business domain challenges."
        }
    ],
    "Full Stack Developer": [
        {
            "title": "Personal Developer Portfolio & Blog",
            "description": "Build a responsive static website showcasing developer projects, skills, and contact form.",
            "required_skills": "HTML, CSS, JavaScript",
            "level": "BEGINNER",
            "outcome": "Master semantic HTML5 structures, CSS layouts, and client-side interactivity."
        },
        {
            "title": "Interactive Task & Kanban Management App",
            "description": "Develop a component-driven React frontend application with dynamic task boards and local storage persistence.",
            "required_skills": "JavaScript, React, CSS",
            "level": "INTERMEDIATE",
            "outcome": "Master React state management, hooks, component architecture, and responsive styling."
        },
        {
            "title": "Full-Stack Career Portal with FastAPI & React",
            "description": "Architect a complete web application with React UI, FastAPI REST backend, SQLite persistence, and JWT authentication.",
            "required_skills": "React, Python, FastAPI, SQL, REST APIs",
            "level": "ADVANCED",
            "outcome": "Gain full-stack integration expertise covering authentication, database ORM, and REST endpoints."
        }
    ]
}

def recommend_projects(
    target_role: str,
    experience_level: str = "Beginner",
    current_skills: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Recommends projects matched to user's target career role and skill level.
    """
    if current_skills is None:
        current_skills = []

    logger.info(f"Recommending projects for '{target_role}' at level '{experience_level}'")

    role_projects = PROJECT_CATALOG.get(target_role, PROJECT_CATALOG["Full Stack Developer"])

    level_norm = experience_level.upper()
    recommended = []

    # Prioritize projects matching experience level
    for project in role_projects:
        if project["level"] == level_norm:
            recommended.append(project)

    # If no exact match, return all available projects for role
    if not recommended:
        recommended = role_projects

    result = {
        "target_role": target_role,
        "experience_level": experience_level,
        "recommended_projects": recommended
    }

    result["summary"] = _format_project_summary(result)
    logger.info(f"Recommended {len(recommended)} projects for {target_role}")
    return result

def _format_project_summary(project_data: Dict[str, Any]) -> str:
    """Formats project recommendations into markdown text."""
    lines = [
        f"💡 **Recommended Portfolio Projects for {project_data['target_role']}** ({project_data['experience_level']} Level)\n"
    ]

    for idx, proj in enumerate(project_data["recommended_projects"], 1):
        lines.append(f"### Project {idx}: {proj['title']}")
        lines.append(f"• **Difficulty**: `{proj['level']}`")
        lines.append(f"• **Description**: {proj['description']}")
        lines.append(f"• **Required Skills**: {proj['required_skills']}")
        lines.append(f"• **Expected Outcome**: {proj['outcome']}\n")

    return "\n".join(lines)
