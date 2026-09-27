NEXUS URL : https://nexusaiagent-hd2tpkysbx2yjn8xohckks.streamlit.app/#welcome-back-pradeesh

# NEXUS – AI Career Intelligence Agent

NEXUS is an autonomous, tool-augmented **AI Career Intelligence Agent** designed for students, fresh graduates, and career switchers. It analyzes user skills, identifies career skill gaps, generates month-by-month learning roadmaps, recommends difficulty-categorized portfolio projects, tracks completed learning progress, and persists profile context using a SQLite database and an intelligent AI Orchestrator Agent.

---

## 🏗️ System Architecture

```
                                  +-----------------------+
                                  |   Streamlit UI        |
                                  |   (7 Dedicated Pages) |
                                  +-----------+-----------+
                                              |
                                              v
                                  +-----------------------+
                                  |   FastAPI REST Backend|
                                  +-----------+-----------+
                                              |
                                              v
                                  +-----------------------+
                                  |   Orchestrator Agent  |
                                  +-----+-----------+-----+
                                        |           |
               +------------------------+           +-----------------------+
               |                                                            |
               v                                                            v
+-------------------------------+                            +-------------------------------+
|  Cognitive Engine             |                            |  Tool System                  |
|  - Intent Analyzer            |                            |  - skill_analyzer             |
|  - Planner & Evaluator        |                            |  - skill_gap_analyzer         |
|  - Memory Manager             |                            |  - roadmap_generator          |
|  - LLM Service (Gemini/OpenAI)|                            |  - project_recommender        |
+---------------+---------------+                            |  - progress_tracker           |
                |                                            +---------------+---------------+
                +-----------------------+------------------------------------+
                                        |
                                        v
                               +-----------------+
                               | SQLite Database |
                               | (SQLAlchemy 2)  |
                               +-----------------+
```

---

## 🔄 Agent Reasoning Workflow

NEXUS follows a 9-step autonomous reasoning cycle:

1. **OBSERVE**: Inspect user query and conversation context.
2. **UNDERSTAND INTENT**: Classify request into target intent (`ANALYZE_SKILLS`, `IDENTIFY_GAPS`, `GENERATE_ROADMAP`, `RECOMMEND_PROJECTS`, `UPDATE_PROGRESS`, `GET_PROFILE`).
3. **CHECK PROFILE**: Retrieve stored skills, target role, and progress history from persistent memory.
4. **DECIDE ACTION**: Formulate execution strategy.
5. **SELECT TOOL**: Select corresponding tool function.
6. **EXECUTE TOOL**: Run deterministic tool with validated arguments.
7. **VALIDATE RESULT**: Verify tool output quality.
8. **GENERATE RESPONSE**: Synthesize structured markdown response using LLM or structured templates.
9. **UPDATE MEMORY**: Persist progress updates and readiness score to database.

---

## 🛠️ Key Features

- **User Profile Management**: Persistent storage for name, education, experience level, target career role, and current skills inventory.
- **Skill Analyzer**: Classifies skills into `COMPLETED`, `IN_PROGRESS`, `MISSING`, and `OPTIONAL`, and computes a readiness score percentage.
- **Skill Gap Report**: Detailed rationales explaining why missing skills are critical for target roles.
- **Dynamic Roadmap Generator**: Month-by-month curriculum adapted to skill gaps, timeframe, and experience level.
- **Portfolio Project Recommender**: Difficulty-categorized project recommendations (`BEGINNER`, `INTERMEDIATE`, `ADVANCED`).
- **Progress Tracker**: Milestone updates ("I completed Python Basics"), readiness score recalculation, and next-topic selection.
- **Interactive AI Coach**: Conversational multi-turn assistance powered by the Orchestrator Agent.

---

## 🚀 Quick Start & Installation

### 1. Prerequisites & Installation
```bash
# Navigate to project directory
cd NEXUS_AI_AGENT

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env`:
```ini
DATABASE_URL=sqlite:///./nexus.db
LOG_LEVEL=INFO
GEMINI_API_KEY=your_gemini_api_key_here
LLM_MODEL_NAME=gemini-2.5-flash
APP_ENV=development
```
*(Note: If `GEMINI_API_KEY` is not configured, NEXUS runs seamlessly in offline rule-based mode.)*

---

## 💻 Running the Application

### Option A: Launch Streamlit Web UI (Recommended)
```bash
streamlit run streamlit_app.py
```
Open `http://localhost:8501` in your web browser.

### Option B: Launch FastAPI REST Backend
```bash
uvicorn app:app --reload --port 8000
```
Access interactive API documentation:
- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

---

## 📡 REST API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/profile` | Create user profile with target career goal & skills |
| `GET` | `/profile` | Fetch complete user profile data |
| `POST` | `/skills` | Add/update individual skill |
| `GET` | `/skills` | Retrieve user skills list |
| `GET` | `/analysis` | Generate skill gap report |
| `POST` | `/roadmap` | Generate & store 6-month learning roadmap |
| `GET` | `/roadmap` | Retrieve active roadmap |
| `POST` | `/progress` | Record completed learning topic |
| `GET` | `/projects` | Get portfolio project recommendations |
| `POST` | `/chat` | Conversational interface with NEXUS Agent |

---

## 🧪 Running Unit & Integration Tests

Execute the complete pytest test suite:
```bash
pytest tests/ -v
```

---

## 📂 Project Directory Structure

```
NEXUS_AI_AGENT/
├── app.py                      # ASGI application alias
├── main.py                     # FastAPI REST server & endpoint routing
├── streamlit_app.py            # Streamlit multi-page frontend UI
├── config.py                   # Environment & Pydantic settings
├── requirements.txt            # Project dependencies
├── README.md                   # Project documentation
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
│
├── agent/                      # Cognitive Agent Engine
│   ├── __init__.py
│   ├── orchestrator.py         # Main Orchestrator Agent
│   ├── intent_analyzer.py      # Intent classifier
│   ├── planner.py              # Tool sequence planner
│   └── evaluator.py            # Result evaluator & response builder
│
├── tools/                      # Deterministic Agent Tools
│   ├── __init__.py
│   ├── skill_analyzer.py       # Skill classification & readiness scoring
│   ├── skill_gap_analyzer.py   # Skill gap report generator
│   ├── roadmap_generator.py    # Month-by-month curriculum generator
│   ├── project_recommender.py  # Portfolio project recommender
│   └── progress_tracker.py     # Progress milestone tracker
│
├── memory/                     # Memory Management Layer
│   ├── __init__.py
│   └── memory_manager.py       # Persistent DB memory lookup
│
├── database/                   # Database Layer
│   ├── __init__.py
│   ├── database.py             # SQLAlchemy engine & session factory
│   └── models.py               # ORM Models (Users, Skills, Goals, Roadmaps, Progress)
│
├── schemas/                    # Pydantic Validation Schemas
│   ├── __init__.py
│   ├── user.py                 # User & skill schemas
│   ├── roadmap.py              # Roadmap & analysis schemas
│   └── response.py             # API & agent response wrappers
│
├── prompts/                    # System Prompts & Templates
│   ├── __init__.py
│   └── system_prompt.py        # System prompt & reasoning rules
│
├── services/                   # LLM API Services
│   ├── __init__.py
│   └── llm_service.py          # Google GenAI SDK wrapper & fallback
│
├── utils/                      # Helper Functions & Logging
│   ├── __init__.py
│   ├── logger.py               # Centralized logger
│   └── helpers.py              # Career skill catalog & helpers
│
├── tests/                      # Pytest Test Suites
│   ├── test_database.py        # Database & ORM tests
│   ├── test_tools.py           # Skill analyzer tests
│   ├── test_phase3_tools.py    # Roadmap & progress tool tests
│   ├── test_agent.py           # Orchestrator & agent tests
│   └── test_api.py             # FastAPI REST endpoint tests
│
└── logs/                       # Application Logs
    └── nexus.log
```
