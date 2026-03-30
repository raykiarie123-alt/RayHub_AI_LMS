#  RayHub AI LMS

RayHub is an AI-powered Learning Management System (LMS) designed to transform how Kasneb students—starting with CPA candidates—learn, revise, and master complex concepts.

It goes beyond traditional LMS platforms by integrating "Retrieval-Augmented Generation (RAG)", enabling both "structured learning" and "student-driven knowledge exploration".

## 🎯 Core Objectives

RayHub is built around five key objectives:

1. AI-Driven Personalization
Generate adaptive study plans based on learner goals, performance trends, available time, and learning preferences.

2. Intelligent Assessment Systems
Provide adaptive quizzes, flashcards, and AI-generated questions to improve retention and track mastery.

3. Centralized Resource Management
Eliminate fragmented learning by consolidating notes, summaries, past papers, and guides in one platform.

4. Gamified Learning Experience
Increase engagement through streaks, points, progress tracking, and achievement systems.

5. Community-Driven Learning** *(Phase 3)*
Enable collaborative study through shared resources, discussions, and group challenges.


##  Key Features

###  LMS Core

1. Course and unit tracking (CPA-focused)
2. Past paper practice and quiz system
3. Progress monitoring and performance insights
4. Secure authentication (JWT-based)

# AI Learning Engine (RAG)

1. Upload PDFs or add web resources
2. Ask questions directly from your materials
3. AI-generated:

a. Summaries
b. Quiz questions
c. Key concept explanations
d. Combine "official LMS content + personal resources"

# Smart Study Scheduler

# AI-generated study plans based on:

  1. Weak areas
  2. Exam timelines
  3. Available study hours
  4. Uploaded learning materials

# Analytics & Insights *(Upcoming)*

1. Student engagement tracking
2. Weak-topic detection
3. Performance trends
4. Resource usage analytics


### System Architecture

```text
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
```

---

## 🛠️ Tech Stack

### Backend

* FastAPI
* SQLAlchemy ORM
* PostgreSQL / SQLite
* JWT Authentication

### AI Stack

* Embeddings (OpenAI / Sentence Transformers)
* Vector Database (FAISS / Chroma)
* Document Processing (PyPDF, BeautifulSoup)

### Frontend

* Angular (planned integration)

---

## 📂 Project Structure (High-Level)

```text
app/
├── api/            # Routes (auth, courses, RAG, scheduler)
├── core/           # Config & security
├── models/         # Database models
├── services/       # Business logic (AI, scheduler, etc.)
├── db/             # Database setup
```

---

## 🚧 Development Roadmap

### Phase 1 — MVP

* PDF upload & processing
* RAG-based Q&A
* Basic LMS (courses, quizzes, tracking)

### Phase 2 — AI Enhancement

* Quiz generation from documents
* Summary generation
* Smart study scheduler

### Phase 3 — Advanced Features

* Admin analytics dashboard
* Real-time engagement tracking
* Gamification system
* Community-driven resource sharing

---

## 🌍 Vision

RayHub aims to become a **fully intelligent learning ecosystem**, bridging education and AI by:

* Empowering students to learn from **both structured and self-sourced materials**
* Providing **real-time adaptive learning support**
* Transforming passive studying into an **interactive, personalized experience**

---
Status

🚧 Actively under development
🔥 Core AI features (RAG) in progress


🤝 Contribution

This project is currently under active development. Contributions, feedback, and collaboration ideas are welcome in future phases.

---

## 📌 Author

Built with a vision to bridge **Finance, Education, and AI**.
