🧠 RayHub AI LMS

RayHub is an AI-powered Learning Management System (LMS) designed to transform how Kasneb students—starting with CPA candidates—learn, revise, and master complex concepts.

Unlike traditional LMS platforms, RayHub integrates Retrieval-Augmented Generation (RAG), enabling both structured learning and student-driven knowledge ingestion.

🎯 Core Objectives

RayHub is built around the following key objectives:

AI-Driven Personalization
Generate adaptive study plans based on learner goals, performance trends, available time, and learning preferences.
Intelligent Assessment Systems
Provide adaptive quizzes, flashcards, and AI-generated questions to improve retention and track mastery.
Centralized Resource Management
Consolidate notes, past papers, summaries, and external materials into one unified platform.
Gamified Learning Experience
Increase engagement through streaks, points, badges, and progress tracking.
Community-Driven Learning (Phase 3)
Enable collaboration through shared resources, peer discussions, and group challenges.
🧩 Key Features
📚 LMS Core
Course and unit tracking (CPA-focused)
Quiz system and past paper practice
Student progress monitoring
Secure authentication using JWT
🤖 AI Learning Engine (RAG)
Upload PDFs and external resource links
Ask AI questions based on your materials
AI-generated:
Summaries
Quiz questions
Concept explanations
Combine official LMS content + personal uploads
🧠 Smart Study Scheduler
Generates study plans based on:
Weak topics
Exam timelines
Available study hours
Uploaded learning materials
📊 Analytics & Insights (Upcoming)
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
Authentication Module → JWT-based login and security
Student Module → Tracks student progress and activity
Course Module → Manages CPA learning content
Quiz & Past Paper Module → Supports assessment and exam prep
Document Module → Handles uploads and external resources
RAG Module → Powers AI tutor using retrieval-based learning
Scheduler Module → Generates intelligent study plans
Gamification Module → Boosts engagement through rewards
Analytics Module → Tracks performance and usage
Notification Module → Sends alerts and reminders
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
Backend
FastAPI
SQLAlchemy
PostgreSQL / SQLite
JWT Authentication
AI Stack
OpenAI / Sentence Transformers (Embeddings)
FAISS / Chroma (Vector DB)
PyPDF / BeautifulSoup (Parsing)
Frontend
Angular (Planned)
🚧 Development Roadmap
Phase 1 — MVP
PDF upload & processing
RAG-based Q&A
Basic LMS (courses, quizzes)
Phase 2 — AI Features
Summary generation
Quiz generation
Smart scheduler
Phase 3 — Advanced System
Analytics dashboard
Real-time engagement tracking
Gamification
Community learning
🌍 Vision

RayHub aims to become a fully intelligent learning ecosystem that:

Bridges education and AI
Empowers students with personalized learning
Supports both structured and self-driven study
Transforms passive studying into interactive learning
⚡ Status

🚧 Actively under development
🔥 RAG system in progress

🤝 Contribution

This project is currently under active development. Contributions and feedback are welcome in future phases.

📌 Author

Built with a vision to bridge Finance, Education, and AI.