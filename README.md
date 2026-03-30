🧠 RayHub AI LMS

RayHub is an AI-powered Learning Management System (LMS) designed to transform how Kasneb students—starting with CPA candidates—learn, revise, and master complex concepts.

Unlike traditional LMS platforms, RayHub integrates Retrieval-Augmented Generation (RAG), enabling both structured learning and student-driven knowledge ingestion.

🎯 Core Objectives

RayHub is built around the following key objectives:

1. AI-Driven Personalization

 Generate adaptive study plans based on learner goals, performance trends, available time, and learning preferences.

2. Intelligent Assessment Systems

Provide adaptive quizzes, flashcards, and AI-generated questions to improve retention and track mastery.

3. Centralized Resource Management
Consolidate notes, past papers, summaries, and external materials into one unified platform.

4. Gamified Learning Experience
Increase engagement through streaks, points, badges, and progress tracking.

5. Community-Driven Learning (Phase 3)
Enable collaboration through shared resources, peer discussions, and group challenges.

🧩 Key Features
1. 📚 LMS Core
Course and unit tracking (CPA-focused)
Quiz system and past paper practice
Student progress monitoring
Secure authentication using JWT

2. 🤖 AI Learning Engine (RAG)
Upload PDFs and external resource links
Ask AI questions based on your materials
AI-generated:
Summaries
Quiz questions
Concept explanations
Combine official LMS content + personal uploads

3. 🧠 Smart Study Scheduler
Generates study plans based on:
Weak topics
Exam timelines
Available study hours
Uploaded learning materials

4. 📊 Analytics & Insights (Upcoming)
Engagement tracking
Weak topic detection
Performance trends
AI usage insights


🏗️ System Architecture
Frontend (Angular)
        ↓
FastAPI Backend
        ↓
-----------------------------------
| LMS Core System                |
| - Users                       |
| - Courses                     |
| - Progress                    |
-----------------------------------
        ↓
-----------------------------------
| AI Layer (RAG System)         |
| - Document Upload             |
| - Text Extraction             |
| - Chunking                    |
| - Embeddings                  |
| - Vector Database             |
-----------------------------------
        ↓
LLM (AI Model)
        ↓
AI Outputs (chat, quiz, summary)
📂 Project Structure
app/
├── api/routes/         # API endpoints
├── core/               # Config & security
├── db/                 # Database setup
├── models/             # SQLAlchemy models
├── schemas/            # Pydantic schemas
├── services/           # Business logic
│   ├── rag/            # RAG pipeline (AI core)
│   ├── documents/      # Upload & parsing
│   └── scheduler/      # Study plan logic
├── utils/              # Helper functions
├── templates/          # AI prompt templates

🧠 System Modules
1. Authentication Module → JWT-based login and security

2. Student Module → Tracks student progress and activity

3. Course Module → Manages CPA learning content

4. Quiz & Past Paper Module → Supports assessment and exam prep

5. Document Module → Handles uploads and external resources

6. RAG Module → Powers AI tutor using retrieval-based learning

7. Scheduler Module → Generates intelligent study plans

8. Gamification Module → Boosts engagement through rewards

9. Analytics Module → Tracks performance and usage

10. Notification Module → Sends alerts and reminders


📊 Use Case Diagram
usecaseDiagram
actor Student
actor Admin
actor "AI Engine" as AI

rectangle RayHub_AI_LMS {
    Student --> (Register/Login)
    Student --> (View Courses)
    Student --> (Track Learning Progress)
    Student --> (Attempt Quiz)
    Student --> (Practice Past Papers)
    Student --> (Upload PDF or Resource Link)
    Student --> (Ask AI Questions)
    Student --> (Generate Summary)
    Student --> (Generate Quiz from Document)
    Student --> (Receive Study Recommendations)
    Student --> (View Smart Study Schedule)

    Admin --> (Manage Courses)
    Admin --> (Upload Official Materials)
    Admin --> (Manage Quizzes)
    Admin --> (View Analytics)

    AI --> (Ask AI Questions)
    AI --> (Generate Summary)
    AI --> (Generate Quiz from Document)
}
🖼️ Wireframes
📊 Student Dashboard
+--------------------------------------------------------------+
|                        RAYHUB DASHBOARD                      |
+--------------------------------------------------------------+
| Welcome, Student                                             |
| Progress: 68%   Streak: 6 days   Exam: CPA Section 2         |
+--------------------------------------------------------------+
| Courses | Quizzes | AI Tutor | Upload | Study Plan           |
+--------------------------------------------------------------+
| Weak Topics: Cost Accounting, Auditing                       |
+--------------------------------------------------------------+
| Recommended Actions                                          |
| - Revise Cost Accounting                                     |
| - Attempt Quiz 5                                             |
+--------------------------------------------------------------+
🤖 AI Tutor Interface
+--------------------------------------------------------------+
|                         AI TUTOR                             |
+--------------------------------------------------------------+
| Source: [ LMS ] [ My PDFs ] [ Both ]                         |
+--------------------------------------------------------------+
| Ask: Explain marginal costing                                |
+--------------------------------------------------------------+
| AI Response:                                                 |
| Marginal costing is...                                       |
+--------------------------------------------------------------+
| [ Generate Quiz ] [ Summarize ]                              |
+--------------------------------------------------------------+
📅 Smart Study Scheduler
+--------------------------------------------------------------+
|                    SMART STUDY SCHEDULER                     |
+--------------------------------------------------------------+
| Exam Date: 2026-05-30                                        |
| Study Hours: 3/day                                           |
+--------------------------------------------------------------+
| Generated Plan                                               |
| Mon: Cost Accounting + Quiz                                  |
| Tue: Taxation Review                                         |
+--------------------------------------------------------------+


🛠️ Tech Stack
1. Backend

FastAPI
SQLAlchemy
PostgreSQL / SQLite
JWT Authentication

2. AI Stack
OpenAI / Sentence Transformers (Embeddings)
FAISS / Chroma (Vector DB)
PyPDF / BeautifulSoup (Parsing)

3. Frontend
Angular (Planned)

🚧 Development Roadmap

1. Phase 1 — MVP
PDF upload & processing
RAG-based Q&A
Basic LMS (courses, quizzes)

2. Phase 2 — AI Features
Summary generation
Quiz generation
Smart scheduler

3. Phase 3 — Advanced System
Analytics dashboard
Real-time engagement tracking
Gamification
Community learning

🌍 Vision

RayHub aims to become a fully intelligent learning ecosystem that:

1. Bridges education and AI

2. Empowers students with personalized learning

3. Supports both structured and self-driven study

4. Transforms passive studying into interactive learning

⚡ Status

🚧 Actively under development
🔥 RAG system in progress

🤝 Contribution

This project is currently under active development. Contributions and feedback are welcome in future phases.

📌 Author

Built with a vision to bridge Finance, Education, and AI.