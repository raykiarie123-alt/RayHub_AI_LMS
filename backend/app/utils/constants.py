# CPA Levels
CPA_LEVELS = ["Foundation", "Intermediate", "Advanced"]

# User Roles
ROLE_STUDENT = "student"
ROLE_TUTOR = "tutor"
ROLE_ADMIN = "admin"
USER_ROLES = [ROLE_STUDENT, ROLE_TUTOR, ROLE_ADMIN]

# XP Rules
XP_COMPLETE_TOPIC = 10
XP_COMPLETE_QUIZ = 20
XP_SCORE_ABOVE_80 = 30
XP_MAINTAIN_STREAK = 15
XP_UPLOAD_RESOURCE = 10
XP_COMPLETE_FLASHCARD_REVIEW = 5

# Badge Definitions
BADGES = {
    "first_quiz": {"name": "Quiz Starter", "description": "Completed your first quiz", "icon": "🎯"},
    "streak_3": {"name": "3-Day Streak", "description": "Studied 3 days in a row", "icon": "🔥"},
    "streak_7": {"name": "Week Warrior", "description": "Studied 7 days in a row", "icon": "⚡"},
    "streak_30": {"name": "Monthly Master", "description": "Studied 30 days in a row", "icon": "🏆"},
    "top_scorer": {"name": "Top Scorer", "description": "Scored 100% on a quiz", "icon": "⭐"},
    "resource_uploader": {"name": "Knowledge Sharer", "description": "Uploaded 5 resources", "icon": "📚"},
    "topic_master": {"name": "Topic Master", "description": "Completed 10 topics", "icon": "🎓"},
    "study_plan_creator": {"name": "Planner", "description": "Created your first study plan", "icon": "📅"},
}

# Difficulty Levels
DIFFICULTY_EASY = "easy"
DIFFICULTY_INTERMEDIATE = "intermediate"
DIFFICULTY_HARD = "hard"
DIFFICULTY_LEVELS = [DIFFICULTY_EASY, DIFFICULTY_INTERMEDIATE, DIFFICULTY_HARD]

# Question Types
QUESTION_MCQ = "mcq"
QUESTION_SHORT = "short_answer"
QUESTION_CASE = "case_study"
QUESTION_TYPES = [QUESTION_MCQ, QUESTION_SHORT, QUESTION_CASE]

# Resource Types
RESOURCE_PDF = "pdf"
RESOURCE_TEXT = "text"
RESOURCE_YOUTUBE = "youtube"
RESOURCE_WEBSITE = "website"
RESOURCE_PAST_PAPER = "past_paper"
RESOURCE_TYPES = [RESOURCE_PDF, RESOURCE_TEXT, RESOURCE_YOUTUBE, RESOURCE_WEBSITE, RESOURCE_PAST_PAPER]

# Chunk settings
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
MAX_CHUNKS_PER_RETRIEVAL = 5

# CPA Units
DEFAULT_UNITS = {
    "Foundation": [
        "Financial Accounting",
        "Quantitative Analysis",
        "Communication SKills",
        "Economics",
        "Business Law"
        "Information Technology"
    ],
    "Intermediate": [
        "Financial Reporting",
        "Management Accounting",
        "Audit and Assurance",
        "Taxation",
        "Company Law"
        "Financial Management"
    ],
    "Advanced": [
        "Advanced Financial Reporting",
        "Advanced Financial Management",
        "Advanced Management Accounting",
        "Advanced Audit",
        "Advanced Taxation",
        "Public Finance and Governance"
        "Leadership and Strategic Management"
    ],
    "Post-Qualification": [
        "Ethics and Professionalism",
        "Global Business Environment",
        "Data Analytics for Accountants",
        "Sustainability and ESG Reporting",
        "Forensic Accounting and Fraud Examination",
        "Technology and Innovation in Accounting"
    ]
}