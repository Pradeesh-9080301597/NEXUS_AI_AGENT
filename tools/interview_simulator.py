"""
NEXUS AI 2.0 - AI Interviewer & Assessment Simulator Tool
Generates role-specific technical interview questions, evaluates user answers using LLM / heuristic rubric,
computes score percentage, and persists results to database.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from utils.logger import logger

DEFAULT_INTERVIEW_QUESTIONS = {
    "AI Engineer": [
        {
            "id": 1,
            "category": "Architecture",
            "question": "Explain the difference between Fine-Tuning a Large Language Model and using Retrieval-Augmented Generation (RAG). When would you choose one over the other?",
            "key_concepts": ["latency", "knowledge cutoff", "domain specificity", "hallucinations", "compute cost"]
        },
        {
            "id": 2,
            "category": "System Design",
            "question": "How would you design a scalable Vector Database retrieval pipeline handling 1 million query requests per minute with <100ms latency?",
            "key_concepts": ["indexing (HNSW / IVF)", "sharding", "caching (Redis)", "batching", "embedding models"]
        },
        {
            "id": 3,
            "category": "MLOps",
            "question": "What techniques do you use to detect prompt injection vulnerabilities and data drift in production LLM applications?",
            "key_concepts": ["input sanitization", "guardrails", "eval metrics (ROUGE/BLEU/Cosine)", "logging"]
        }
    ],
    "Data Scientist": [
        {
            "id": 1,
            "category": "Statistics",
            "question": "How do you handle severe class imbalance in a fraud detection dataset with 99.9% negative cases?",
            "key_concepts": ["SMOTE", "PR-AUC vs ROC-AUC", "cost-sensitive learning", "focal loss"]
        },
        {
            "id": 2,
            "category": "Machine Learning",
            "question": "Explain gradient boosting vs random forest. Why does XGBoost perform so well on tabular data?",
            "key_concepts": ["sequential boosting", "regularization", "tree splitting", "variance reduction"]
        }
    ]
}

def get_interview_questions(target_role: str = "AI Engineer") -> List[Dict[str, Any]]:
    """Returns curated interview questions for target role."""
    return DEFAULT_INTERVIEW_QUESTIONS.get(target_role, DEFAULT_INTERVIEW_QUESTIONS["AI Engineer"])

def evaluate_interview_answer(
    question: str,
    user_answer: str,
    target_role: str = "AI Engineer",
    db: Optional[Session] = None,
    user_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Evaluates user's answer against key technical concepts.
    Returns feedback and score percentage.
    """
    logger.info(f"Evaluating answer for role '{target_role}' (Answer length: {len(user_answer)} chars)")
    
    words = user_answer.strip().split()
    word_count = len(words)
    answer_lower = user_answer.lower()

    # Find matching key concepts for default question bank
    matched_concepts = []
    missing_concepts = []
    
    relevant_q = None
    for q in DEFAULT_INTERVIEW_QUESTIONS.get(target_role, DEFAULT_INTERVIEW_QUESTIONS["AI Engineer"]):
        if q["question"].lower() in question.lower() or question.lower() in q["question"].lower():
            relevant_q = q
            break

    key_concepts = relevant_q["key_concepts"] if relevant_q else ["accuracy", "tradeoffs", "scalability", "architecture"]

    for concept in key_concepts:
        if any(w in answer_lower for w in concept.lower().split()):
            matched_concepts.append(concept)
        else:
            missing_concepts.append(concept)

    # Calculate rubric score
    if word_count < 15:
        score = 30.0
        feedback_msg = "Answer is too brief. Elaborate on trade-offs, architecture decisions, and real-world examples."
    else:
        concept_coverage = (len(matched_concepts) / len(key_concepts)) * 100.0 if key_concepts else 70.0
        length_bonus = min(word_count / 100.0 * 20.0, 20.0)
        score = round(min(concept_coverage * 0.8 + length_bonus, 95.0), 1)
        feedback_msg = f"Solid technical answer! Covered {len(matched_concepts)}/{len(key_concepts)} key concepts."

    result = {
        "question": question,
        "score_percentage": score,
        "matched_concepts": matched_concepts,
        "missing_concepts": missing_concepts,
        "feedback": feedback_msg,
        "model_tip": f"To improve score to 100%, discuss: {', '.join(missing_concepts)}" if missing_concepts else "Great comprehensive answer!"
    }

    # Persist to database if provided
    if db and user_id:
        try:
            from database.models import AssessmentResult
            result_record = AssessmentResult(
                user_id=user_id,
                assessment_type="AI Interview Simulator",
                skill_name=target_role,
                score_percentage=score,
                feedback=feedback_msg
            )
            db.add(result_record)
            db.commit()
            logger.info(f"Persisted assessment result to DB for user_id={user_id}")
        except Exception as e:
            logger.error(f"Error persisting assessment result: {e}")

    return result
