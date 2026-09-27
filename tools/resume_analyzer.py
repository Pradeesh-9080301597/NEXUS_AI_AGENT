"""
NEXUS AI 2.0 - Resume Analyzer Tool
Parses resume text/uploads, extracts skills, analyzes ATS keyword alignment against target role,
computes match score percentage, and provides optimization recommendations.
"""

import json
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from utils.helpers import get_career_details, normalize_skill
from utils.logger import logger

KNOWN_SKILLS_TAXONOMY = [
    "Python", "Java", "C++", "JavaScript", "TypeScript", "SQL", "Go", "Rust",
    "PyTorch", "TensorFlow", "Scikit-Learn", "Keras", "Pandas", "NumPy",
    "LangChain", "LlamaIndex", "Transformers", "OpenAI API", "Gemini API",
    "Docker", "Kubernetes", "AWS", "GCP", "Azure", "FastAPI", "Flask", "Django",
    "Streamlit", "Git", "CI/CD", "Linux", "REST APIs", "GraphQL", "PostgreSQL",
    "MongoDB", "Redis", "Pinecone", "ChromaDB", "FAISS", "Qdrant", "RAG",
    "Prompt Engineering", "Fine-Tuning", "BERT", "GPT", "MLOps", "Spark",
    "System Design", "Unit Testing", "PyTest", "HTML", "CSS", "React", "Node.js",
    "Machine Learning", "Deep Learning", "Generative AI", "LLMs", "APIs", "Databases", "Deployment"
]

SKILL_SYNONYMS = {
    "llms": ["llm", "llms", "large language model", "large language models", "gpt", "bert", "llama", "transformers"],
    "generative ai": ["generative ai", "genai", "gen ai", "llm", "prompt engineering", "fine-tuning", "rag"],
    "machine learning": ["machine learning", "ml", "scikit-learn", "sklearn"],
    "deep learning": ["deep learning", "dl", "pytorch", "tensorflow", "keras", "neural networks"],
    "apis": ["api", "apis", "fastapi", "flask", "rest api", "rest apis", "graphql"],
    "databases": ["database", "databases", "sql", "postgresql", "mongodb", "redis", "chromadb", "vector db", "pinecone"],
    "deployment": ["deployment", "deploy", "docker", "kubernetes", "aws", "gcp", "azure", "streamlit"]
}

def analyze_resume(
    resume_text: str,
    target_role: str = "AI Engineer",
    db: Optional[Session] = None,
    user_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Analyzes resume text for ATS keyword alignment against a target role.
    """
    logger.info(f"Analyzing resume for target role: '{target_role}' (Length: {len(resume_text)} chars)")
    
    # 1. Normalize resume text
    text_lower = resume_text.lower()

    # 2. Extract present skills
    extracted_skills = []
    for skill in KNOWN_SKILLS_TAXONOMY:
        sk_norm = normalize_skill(skill)
        synonyms = SKILL_SYNONYMS.get(sk_norm, [sk_norm, skill.lower()])
        if any(syn in text_lower for syn in synonyms):
            extracted_skills.append(skill)

    # Deduplicate
    extracted_skills = list(dict.fromkeys(extracted_skills))

    # 3. Match against Target Role Requirements
    career_info = get_career_details(target_role)
    required_skills = career_info.get("required_skills", [])

    matched_required = []
    missing_required = []

    for req in required_skills:
        req_norm = normalize_skill(req)
        synonyms = SKILL_SYNONYMS.get(req_norm, [req_norm, req.lower()])
        if any(syn in text_lower for syn in synonyms) or any(normalize_skill(s) == req_norm for s in extracted_skills):
            matched_required.append(req)
        else:
            missing_required.append(req)

    total_req = len(required_skills)
    if total_req > 0:
        match_score = round((len(matched_required) / total_req) * 100.0, 1)
    else:
        match_score = 70.0

    # 4. Generate Feedback & Optimization Tips
    feedback = []
    if missing_required:
        feedback.append(f"Missing high-impact role keywords: {', '.join(missing_required[:4])}")
    if len(resume_text.split()) < 150:
        feedback.append("Resume appears concise. Consider expanding on project metrics, impact, and quantitative achievements.")
    if "docker" not in text_lower and "aws" not in text_lower:
        feedback.append("Consider highlighting cloud or containerization experience (e.g. Docker, AWS, Streamlit Cloud).")
    if not feedback:
        feedback.append("Excellent keyword coverage and ATS formatting structure!")

    result = {
        "target_role": target_role,
        "score_percentage": min(match_score, 100.0),
        "extracted_skills": extracted_skills,
        "matched_required_skills": matched_required,
        "missing_required_skills": missing_required,
        "total_skills_found": len(extracted_skills),
        "feedback": feedback,
        "tier": "Strong Match" if match_score >= 80 else ("Moderate Match" if match_score >= 50 else "Needs Optimization")
    }

    # 5. Persist to Database if session and user_id provided
    if db and user_id:
        try:
            from database.models import Resume
            new_resume = Resume(
                user_id=user_id,
                file_name=f"resume_{target_role.lower().replace(' ', '_')}.txt",
                raw_text=resume_text,
                extracted_skills_json=json.dumps(extracted_skills),
                score_percentage=result["score_percentage"],
                feedback_json=json.dumps(feedback)
            )
            db.add(new_resume)
            db.commit()
            logger.info(f"Persisted resume analysis to DB for user_id={user_id}")
        except Exception as e:
            logger.error(f"Error persisting resume analysis: {e}")

    return result
