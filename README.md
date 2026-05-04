# 🚀 RayHub AI LMS

An AI-powered Learning Management System designed for CPA students to learn smarter through personalization, intelligent assessments, and Retrieval-Augmented Generation (RAG).

---

## 📌 Overview

RayHub AI LMS is built to transform how CPA students study by combining:

- AI-driven study planning
- Intelligent quizzes and flashcards
- Document-based learning (RAG)
- Progress tracking and gamification
- Centralized learning resources

> Built with FastAPI, React, and AI technologies.

---

## 🧠 Core Features

### 1. AI-Personalized Study Plans
- Generates study schedules based on:
  - CPA level (Foundation, Intermediate, Advanced)
  - Available study time
  - Weak areas
  - Exam timelines

---

### 2. Intelligent Assessments
- Topic quizzes
- AI-generated questions
- Flashcards
- Performance analytics

---

### 3. RAG-Based Learning (🔥 Key Feature)
- Upload PDFs, YouTube links, or notes
- System:
  - Extracts content
  - Chunks it
  - Embeds it
  - Stores in FAISS vector store
- Ask questions and get AI answers from your own material

---

### 4. Progress Tracking & Gamification
- XP points
- Streaks
- Badges
- Leaderboards
- Course progress tracking

---

## 🏗️ System Architecture

```text
Frontend (React)
   ↓
FastAPI Backend
   ↓
Database + FAISS Vector Store
   ↓
AI (LLM + RAG + Embeddings)