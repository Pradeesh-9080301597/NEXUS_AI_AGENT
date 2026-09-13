"""
NEXUS AI Agent - Helper Functions & Career Skill Catalog
Provides text normalization, skill comparison logic, and comprehensive reference career skill requirements.
"""

from typing import List, Dict, Any

# Standard reference catalog of required & optional skills across tech career paths
CAREER_SKILL_CATALOG: Dict[str, Dict[str, Any]] = {
    "AI Engineer": {
        "description": "Designs, builds, and deploys intelligent systems using machine learning, deep learning, and large language models.",
        "required_skills": [
            "Python", "NumPy", "Pandas", "Machine Learning", 
            "Deep Learning", "LLMs", "Generative AI", "APIs", "Databases", "Deployment"
        ],
        "optional_skills": ["Docker", "MLOps", "LangChain", "Vector Databases", "PyTorch"],
        "skill_importance": {
            "Python": "Primary programming language for AI/ML development, scripting, and model integration.",
            "NumPy": "Essential for numerical computation, array operations, and vector processing.",
            "Pandas": "Core data manipulation and tabular analysis library.",
            "Machine Learning": "Fundamental algorithms (regression, classification, clustering) for predictive modeling.",
            "Deep Learning": "Neural network architectures (CNNs, RNNs, Transformers) for complex pattern recognition.",
            "LLMs": "Building applications with large language models, prompt engineering, and RAG.",
            "Generative AI": "Creating generative applications with diffusion models, fine-tuning, and multi-modal AI.",
            "APIs": "Exposing models as scalable REST endpoints using FastAPI/Flask.",
            "Databases": "Storing structured profile data, logs, and embeddings in relational or vector DBs.",
            "Deployment": "Packaging and hosting models on cloud infrastructure or containers."
        }
    },
    "Data Scientist": {
        "description": "Extracts actionable insights from complex datasets using statistics, machine learning, and visualization.",
        "required_skills": [
            "Python", "SQL", "Statistics", "Data Cleaning", 
            "NumPy", "Pandas", "Machine Learning", "Data Visualization", "Git"
        ],
        "optional_skills": ["Big Data", "Spark", "Tableau", "Deep Learning", "A/B Testing"],
        "skill_importance": {
            "Python": "Primary programming environment for data analysis and modeling.",
            "SQL": "Querying and manipulating structured relational databases.",
            "Statistics": "Formulating hypotheses, statistical significance, and probability models.",
            "Data Cleaning": "Handling missing data, outliers, normalization, and feature extraction.",
            "NumPy": "Fast numerical array operations.",
            "Pandas": "DataFrame manipulation and exploratory data analysis.",
            "Machine Learning": "Building predictive algorithms for classification and regression.",
            "Data Visualization": "Communicating insights visually with Matplotlib/Seaborn.",
            "Git": "Version control for reproducible data science code."
        }
    },
    "Full Stack Developer": {
        "description": "Builds end-to-end web applications, encompassing client frontend interfaces and backend server architecture.",
        "required_skills": [
            "HTML", "CSS", "JavaScript", "React", "Node.js", 
            "Python", "FastAPI", "SQL", "Git", "REST APIs"
        ],
        "optional_skills": ["Docker", "TypeScript", "Next.js", "Tailwind CSS", "CI/CD"],
        "skill_importance": {
            "HTML": "Structure and semantically meaningful markup for web applications.",
            "CSS": "Styling, layouts, responsive design, and visual components.",
            "JavaScript": "Core programming language of web interfaces.",
            "React": "Component-driven frontend UI library for single-page applications.",
            "Node.js": "JavaScript runtime for building scalable server-side applications.",
            "Python": "Backend programming for APIs and business logic.",
            "FastAPI": "High-performance Python web framework for building REST APIs.",
            "SQL": "Managing relational database schema and data persistence.",
            "Git": "Collaborative version control and source code management.",
            "REST APIs": "Designing clean HTTP contracts between client frontend and server backend."
        }
    },
    "Backend Developer": {
        "description": "Specializes in server-side application logic, database architecture, integration, and performance scalability.",
        "required_skills": [
            "Python", "Java", "SQL", "FastAPI", "PostgreSQL", 
            "REST APIs", "Git", "System Design", "Authentication"
        ],
        "optional_skills": ["Docker", "Kubernetes", "Redis", "Microservices", "Kafka"],
        "skill_importance": {
            "Python": "Writing high-level server code and backend services.",
            "Java": "Building enterprise-grade robust backend applications.",
            "SQL": "Database schema modeling and complex relational queries.",
            "FastAPI": "Rapid REST API service development with automatic OpenAPI generation.",
            "PostgreSQL": "Production relational database management system.",
            "REST APIs": "Defining HTTP endpoints and data serialization.",
            "Git": "Source code management and version tracking.",
            "System Design": "Architecting scalable, fault-tolerant backend systems.",
            "Authentication": "Securing applications using JWT, OAuth2, and session tokens."
        }
    },
    "Frontend Developer": {
        "description": "Creates intuitive, responsive, and visually appealing web interfaces for optimal user experiences.",
        "required_skills": [
            "HTML", "CSS", "JavaScript", "TypeScript", "React", 
            "Tailwind CSS", "Git", "REST APIs", "Responsive Design"
        ],
        "optional_skills": ["Next.js", "Redux", "Web Performance", "Testing", "Figma"],
        "skill_importance": {
            "HTML": "Semantic document structuring for web browsers.",
            "CSS": "Visual styling, animations, and flexbox/grid layout systems.",
            "JavaScript": "Dynamic web interactivity and DOM manipulation.",
            "TypeScript": "Typed JavaScript for scalable error-resistant frontend applications.",
            "React": "Declarative component-based UI framework.",
            "Tailwind CSS": "Utility-first CSS framework for rapid styling.",
            "Git": "Version control for UI codebase management.",
            "REST APIs": "Fetching and consuming dynamic data from backends.",
            "Responsive Design": "Ensuring UI adapts perfectly across mobile, tablet, and desktop screens."
        }
    },
    "Cloud & DevOps Engineer": {
        "description": "Automates deployment pipelines, manages cloud infrastructure, and optimizes application delivery reliability.",
        "required_skills": [
            "Linux", "Bash", "Python", "Docker", "Kubernetes", 
            "CI/CD", "AWS", "Terraform", "Git", "Networking"
        ],
        "optional_skills": ["Ansible", "Prometheus", "Grafana", "Azure", "GCP"],
        "skill_importance": {
            "Linux": "Core operating system for server administration and cloud instances.",
            "Bash": "Shell scripting for automation tasks.",
            "Python": "Scripting infrastructure pipelines and cloud APIs.",
            "Docker": "Containerizing applications for consistent execution across environments.",
            "Kubernetes": "Orchestrating container deployment, scaling, and networking.",
            "CI/CD": "Building automated build, test, and release pipelines.",
            "AWS": "Cloud infrastructure services (EC2, S3, IAM, VPC).",
            "Terraform": "Infrastructure as Code (IaC) provisioning.",
            "Git": "Version control for software and configuration files.",
            "Networking": "DNS, subnets, firewalls, HTTP/S, and load balancing fundamentals."
        }
    }
}

def normalize_skill(skill_name: str) -> str:
    """Normalizes skill strings for case-insensitive matching."""
    return skill_name.strip().lower()

def format_skill_list(skills: List[str]) -> List[str]:
    """Cleans and deduplicates a list of skill strings while preserving display case."""
    seen = set()
    cleaned = []
    for s in skills:
        item = s.strip()
        norm = item.lower()
        if norm and norm not in seen:
            seen.add(norm)
            cleaned.append(item)
    return cleaned

def get_career_details(target_role: str) -> Dict[str, Any]:
    """Returns catalog details for a target role or a default custom fallback."""
    for role, details in CAREER_SKILL_CATALOG.items():
        if role.lower() == target_role.lower():
            return details
    
    # Generic fallback catalog entry for custom or unknown roles
    return {
        "description": f"Custom technology path for {target_role}.",
        "required_skills": ["Python", "Git", "SQL", "APIs", "Problem Solving"],
        "optional_skills": ["Docker", "Cloud", "Testing"],
        "skill_importance": {
            "Python": "Core programming language for automation and logic.",
            "Git": "Version control standard.",
            "SQL": "Data query language.",
            "APIs": "Interface communication standard.",
            "Problem Solving": "Essential algorithmic thinking."
        }
    }
