"""
NEXUS AI Agent - Roadmap Generator Tool
Generates structured, month-by-month personalized learning roadmaps based on current skills, skill gaps, experience level, and timeframe.
"""

from typing import List, Dict, Any, Optional
from tools.skill_gap_analyzer import identify_skill_gaps
from utils.logger import logger

# Specialized curriculum templates for key tech roles
ROLE_CURRICULA: Dict[str, List[Dict[str, Any]]] = {
    "AI Engineer": [
        {
            "topic_name": "Python Programming & Core Data Structures",
            "skills": ["Python"],
            "objectives": "Master Python 3 syntax, OOP principles, data structures, type hint annotations, and virtual environments.",
            "duration": "4 Weeks",
            "practice_tasks": "Solve 20 algorithmic challenges; build a CLI text processing utility."
        },
        {
            "topic_name": "Data Manipulation with NumPy & Pandas",
            "skills": ["NumPy", "Pandas"],
            "objectives": "Perform high-performance vector calculations, tabular data cleaning, matrix transformations, and feature engineering.",
            "duration": "4 Weeks",
            "practice_tasks": "Clean an unformatted 100k-row CSV dataset and extract statistical metrics."
        },
        {
            "topic_name": "Machine Learning Foundations & Scikit-Learn",
            "skills": ["Machine Learning"],
            "objectives": "Implement supervised/unsupervised algorithms (Regression, Decision Trees, Random Forests, K-Means) and cross-validation.",
            "duration": "4 Weeks",
            "practice_tasks": "Train a predictive customer churn classification model."
        },
        {
            "topic_name": "Deep Learning Architectures with PyTorch",
            "skills": ["Deep Learning"],
            "objectives": "Build multi-layer perceptrons, CNNs for computer vision, and RNNs/Transformers for sequential data.",
            "duration": "4 Weeks",
            "practice_tasks": "Train a PyTorch image classification model on CIFAR-10."
        },
        {
            "topic_name": "Large Language Models & Generative AI",
            "skills": ["LLMs", "Generative AI"],
            "objectives": "Understand Transformer mechanisms, prompt engineering techniques, API integration, and Retrieval-Augmented Generation (RAG).",
            "duration": "4 Weeks",
            "practice_tasks": "Develop a RAG-based document QA system using vector search."
        },
        {
            "topic_name": "AI Agent Systems & Production Deployment",
            "skills": ["APIs", "Databases", "Deployment"],
            "objectives": "Design multi-tool AI agent workflows, expose REST API endpoints with FastAPI, and package with Docker for cloud deployment.",
            "duration": "4 Weeks",
            "practice_tasks": "Deploy an autonomous AI Career Assistant as a containerized REST API."
        }
    ],
    "Data Scientist": [
        {
            "topic_name": "Python & Data Analysis Ecosystem",
            "skills": ["Python", "NumPy", "Pandas"],
            "objectives": "Master Python scripting, array operations, and DataFrame data wrangling.",
            "duration": "4 Weeks",
            "practice_tasks": "Perform exploratory data analysis (EDA) on a real-world dataset."
        },
        {
            "topic_name": "Relational Databases & Advanced SQL",
            "skills": ["SQL"],
            "objectives": "Write complex SQL joins, aggregation queries, subqueries, and window functions.",
            "duration": "4 Weeks",
            "practice_tasks": "Query multi-table business schemas to solve analytical questions."
        },
        {
            "topic_name": "Applied Statistics & Data Visualization",
            "skills": ["Statistics", "Data Visualization"],
            "objectives": "Apply hypothesis testing, probability distributions, Seaborn visualization, and dashboarding.",
            "duration": "4 Weeks",
            "practice_tasks": "Build an interactive analytical dashboard."
        },
        {
            "topic_name": "Machine Learning Algorithms & Evaluation",
            "skills": ["Machine Learning"],
            "objectives": "Train predictive regression/classification models and tune hyperparameters.",
            "duration": "4 Weeks",
            "practice_tasks": "Build a sales forecasting ML model."
        },
        {
            "topic_name": "Advanced Modeling & Feature Engineering",
            "skills": ["Data Cleaning", "Git"],
            "objectives": "Advanced feature selection, pipeline building, model evaluation metrics, and Git versioning.",
            "duration": "4 Weeks",
            "practice_tasks": "Submit a Kaggle competition baseline entry."
        }
    ],
    "Full Stack Developer": [
        {
            "topic_name": "HTML5, CSS3 & Responsive Web Design",
            "skills": ["HTML", "CSS"],
            "objectives": "Master semantic markup, Flexbox, CSS Grid, and mobile-responsive layouts.",
            "duration": "4 Weeks",
            "practice_tasks": "Build a responsive multi-page portfolio website."
        },
        {
            "topic_name": "Modern JavaScript & DOM Interactivity",
            "skills": ["JavaScript"],
            "objectives": "Understand ES6+ syntax, asynchronous JS (Promises/async-await), and DOM manipulation.",
            "duration": "4 Weeks",
            "practice_tasks": "Create an interactive task management web application."
        },
        {
            "topic_name": "Frontend UI Development with React",
            "skills": ["React"],
            "objectives": "Build component-driven single-page interfaces, state hooks, and routing.",
            "duration": "4 Weeks",
            "practice_tasks": "Build an e-commerce product catalog in React."
        },
        {
            "topic_name": "Backend REST APIs with Python & FastAPI",
            "skills": ["Python", "FastAPI", "REST APIs"],
            "objectives": "Design RESTful backend routes, Pydantic data validation, and HTTP request handling.",
            "duration": "4 Weeks",
            "practice_tasks": "Build a REST API server with auth and database CRUD operations."
        },
        {
            "topic_name": "Database Persistence & Full Stack Integration",
            "skills": ["SQL", "Git"],
            "objectives": "Connect React frontend to FastAPI backend with SQL database persistence.",
            "duration": "4 Weeks",
            "practice_tasks": "Deploy a complete full-stack web application."
        }
    ]
}

def generate_roadmap(
    current_skills: List[str],
    target_role: str,
    experience_level: str = "Beginner",
    timeframe_months: int = 6,
    in_progress_skills: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Generates a personalized learning roadmap adapted to user's missing skills and timeframe.
    """
    if in_progress_skills is None:
        in_progress_skills = []

    logger.info(f"Generating roadmap for '{target_role}' ({timeframe_months} months, {experience_level})")

    gap_data = identify_skill_gaps(current_skills, target_role, in_progress_skills)
    missing_skills = gap_data["report"]["missing_skills"]
    completed_skills = gap_data["report"]["completed_skills"]

    # Select base curriculum or construct dynamic roadmap items
    curriculum = ROLE_CURRICULA.get(target_role, ROLE_CURRICULA["Full Stack Developer"])

    items = []
    month_counter = 1

    for module in curriculum:
        if month_counter > timeframe_months:
            break

        module_skills = module.get("skills", [])
        # Check if user already mastered all skills in this module
        all_completed = all(s in completed_skills for s in module_skills)

        item_status = "COMPLETED" if all_completed else ("IN_PROGRESS" if any(s in in_progress_skills for s in module_skills) else "PENDING")

        items.append({
            "month_number": month_counter,
            "topic_name": module["topic_name"],
            "objectives": module["objectives"],
            "duration": module["duration"],
            "practice_tasks": module["practice_tasks"],
            "status": item_status
        })

        month_counter += 1

    result = {
        "target_role": target_role,
        "experience_level": experience_level,
        "total_months": len(items),
        "items": items,
        "readiness_score": gap_data["report"]["readiness_score_percentage"]
    }

    result["summary"] = _format_roadmap_summary(result)
    logger.info(f"Generated {len(items)}-month roadmap for {target_role}")
    return result

def _format_roadmap_summary(roadmap_data: Dict[str, Any]) -> str:
    """Formats roadmap output into a clean user markdown string."""
    lines = [
        f"🗺️ **Personalized Learning Roadmap: {roadmap_data['target_role']}**",
        f"⏱️ **Duration**: {roadmap_data['total_months']} Months | 📈 **Target Level**: {roadmap_data['experience_level']}\n"
    ]

    for item in roadmap_data["items"]:
        status_icon = "✅" if item["status"] == "COMPLETED" else ("⏳" if item["status"] == "IN_PROGRESS" else "📌")
        lines.append(f"### {status_icon} MONTH {item['month_number']}: {item['topic_name']}")
        lines.append(f"• **Duration**: {item['duration']}")
        lines.append(f"• **Learning Objectives**: {item['objectives']}")
        lines.append(f"• **Practice Recommendation**: {item['practice_tasks']}")
        lines.append(f"• **Status**: {item['status']}\n")

    return "\n".join(lines)
