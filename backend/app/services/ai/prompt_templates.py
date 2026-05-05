"""
Centralized prompt templates for all AI services in RayHub AI LMS.
"""

# ─── Quiz Generation ──────────────────────────────────────────────────────────

QUIZ_SYSTEM_PROMPT = """You are an expert CPA examiner and educator creating high-quality exam questions.
Generate questions that test deep understanding of CPA concepts.
Always return valid JSON in the exact format specified."""

QUIZ_MCQ_PROMPT = """Generate {num_questions} multiple-choice questions for CPA students on the topic: "{topic}".
Difficulty level: {difficulty}
{context}

Return a JSON object with this exact structure:
{{
  "title": "Quiz on {topic}",
  "questions": [
    {{
      "question_text": "Question text here",
      "question_type": "mcq",
      "options": ["A. Option 1", "B. Option 2", "C. Option 3", "D. Option 4"],
      "correct_answer": "A. Option 1",
      "explanation": "Detailed explanation of why this is correct"
    }}
  ]
}}"""

QUIZ_SHORT_ANSWER_PROMPT = """Generate {num_questions} short-answer questions for CPA students on: "{topic}".
Difficulty level: {difficulty}
{context}

Return a JSON object:
{{
  "title": "Short Answer Quiz on {topic}",
  "questions": [
    {{
      "question_text": "Question text here",
      "question_type": "short_answer",
      "options": null,
      "correct_answer": "Model answer here",
      "explanation": "Detailed explanation"
    }}
  ]
}}"""

QUIZ_CASE_PROMPT = """Generate {num_questions} CPA-style case study questions on: "{topic}".
Difficulty level: {difficulty}
{context}

Return a JSON object:
{{
  "title": "Case Study Questions on {topic}",
  "questions": [
    {{
      "question_text": "Case scenario and question here",
      "question_type": "case_study",
      "options": null,
      "correct_answer": "Comprehensive model answer",
      "explanation": "Step-by-step explanation"
    }}
  ]
}}"""

# ─── Study Plan Generation ────────────────────────────────────────────────────

STUDY_PLAN_SYSTEM_PROMPT = """You are an expert CPA study coach creating personalized study plans.
Create realistic, achievable study schedules that help students pass their CPA exams.
Always return valid JSON in the exact format specified."""

STUDY_PLAN_PROMPT = """Create a personalized CPA study plan for a student with these details:
- Exam date: {exam_date}
- Available study hours per day: {hours_per_day}
- Selected units to study: {selected_units}
- Weak topics needing extra attention: {weak_topics}
- Learning style preference: {learning_style}
- CPA level: {cpa_level}

Create a week-by-week study plan. Return a JSON object:
{{
  "title": "CPA Study Plan",
  "description": "Brief description of the plan",
  "total_weeks": <number>,
  "weekly_plan": [
    {{
      "week": 1,
      "focus": "Main focus for this week",
      "tasks": [
        {{
          "day": 1,
          "title": "Task title",
          "description": "What to study/do",
          "task_type": "topic|quiz|flashcard|revision|past_paper",
          "estimated_hours": 2.0
        }}
      ]
    }}
  ]
}}"""

# ─── Flashcard Generation ─────────────────────────────────────────────────────

FLASHCARD_SYSTEM_PROMPT = """You are an expert CPA tutor creating effective study flashcards.
Create concise, clear flashcards that help students memorize key concepts.
Always return valid JSON."""

FLASHCARD_PROMPT = """Generate {num_cards} flashcards for CPA students on: "{topic}".
{context}

Return a JSON object:
{{
  "flashcards": [
    {{
      "front": "Question or concept on the front",
      "back": "Answer or explanation on the back"
    }}
  ]
}}"""

# ─── Recommendation Engine ────────────────────────────────────────────────────

RECOMMENDATION_PROMPT = """Based on this CPA student's performance data, recommend what they should study next:

Student Profile:
- CPA Level: {cpa_level}
- Weak areas: {weak_areas}
- Recently completed: {completed_topics}
- Quiz performance: {quiz_performance}
- Study streak: {streak} days

Return a JSON object:
{{
  "recommendations": [
    {{
      "type": "topic|quiz|resource|flashcard",
      "title": "What to study",
      "reason": "Why this is recommended",
      "priority": "high|medium|low"
    }}
  ]
}}"""

# ─── Summarization ────────────────────────────────────────────────────────────

SUMMARIZE_SYSTEM_PROMPT = """You are an expert CPA tutor creating clear, structured summaries for students.
Focus on exam-relevant content and key concepts."""

SUMMARIZE_PROMPT = """Summarize this CPA study material for students:

Topic: {topic}
Content:
{content}

Create a structured summary with:
1. Key concepts and definitions
2. Important rules and principles  
3. Common exam questions/areas
4. Quick revision points"""