from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, Float, Date
from sqlalchemy import Time
from sqlalchemy.orm import relationship
from datetime import datetime   
from app.database import Base
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.rag_query_log import RAGQueryLog


#create a User model to represent users in the system.
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String(200), nullable=False)
    role = Column(String(50), default="student")
    created_at = Column(DateTime, default=datetime.utcnow)
    full_name = Column(String)

    notifications = relationship("Notification", back_populates="student")
    streak = relationship("UserStreak", back_populates="student", uselist=False)
    documents = relationship("Document", back_populates="user")

#create course model to represent courses in the system.
class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow) 
    levels = relationship("Level", back_populates="course") 

#level model to represent different levels of courses.
class Level(Base):
    __tablename__ = "levels"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    price = Column(Integer)

    course_id = Column(Integer, ForeignKey("courses.id"))
    created_at = Column(DateTime, default=datetime.utcnow)  

    course = relationship("Course", back_populates="levels")
    units = relationship("Unit", back_populates="level")

    #unit model to represent different units within a level.
class Unit(Base):
    __tablename__ = "units"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    content = Column(Text)

    level_id = Column(Integer, ForeignKey("levels.id"))
    created_at = Column(DateTime, default=datetime.utcnow)  

    level = relationship("Level", back_populates="units")
    topics = relationship("Topic", back_populates="unit")

#topic model to represent different topics within a unit.
class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    video_url = Column(String(300))

    unit_id = Column(Integer, ForeignKey("units.id"))
    created_at = Column(DateTime, default=datetime.utcnow)  

    unit = relationship("Unit", back_populates="topics")

#quiz model to represent quizzes for each topic.
class Quiz(Base):
    __tablename__ = "quizzes"

    #primary key
    id = Column(Integer, primary_key=True, index=True)
    #each quiz belongs to a topic
    topic_id = Column(Integer, ForeignKey("topics.id"))
    #quiz question
    title = Column(String, index=True)
    
    #when quiz was created
    created_at = Column(DateTime, default=datetime.utcnow)

#question model to represent questions for each quiz.
class Question(Base):
    __tablename__ = "questions"

    # Primary key
    id = Column(Integer, primary_key=True)

    # Question belongs to a quiz
    quiz_id = Column(Integer, ForeignKey("quizzes.id"))

    # Question text
    question_text = Column(Text)

    # Multiple choice options
    option_a = Column(String)
    option_b = Column(String)
    option_c = Column(String)
    option_d = Column(String)

    # Correct option (A,B,C,D)
    correct_answer = Column(String)

#quiz attempt model to represent user attempts at quizzes.
class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"
    #primary key
    id = Column(Integer, primary_key=True)
    #foreign key to user who attempted the quiz
    user_id = Column(Integer, ForeignKey("users.id"))
    #foreign key to the quiz that was attempted
    quiz_id = Column(Integer, ForeignKey("quizzes.id"))
    #final score of the quiz attempt
    score = Column(Integer)
    #when the quiz was attempted
    attempted_at = Column(DateTime, default=datetime.utcnow)

#student answer table
class StudentAnswer(Base):
    __tablename__ = "student_answers"
    #primary key
    id = Column(Integer, primary_key=True)
    #foreign key to quiz attempt
    quiz_attempt_id = Column(Integer, ForeignKey("quiz_attempts.id"))
    #foreign key to question being answered
    question_id = Column(Integer, ForeignKey("questions.id"))
    #the answer provided by the student (A,B,C,D)
    selected_option = Column(String)
    #whether the answer was correct or not    is_correct = Column(Boolean)
    is_correct = Column(Boolean)

#past Paper model to represent past CPA exam papers.
class PastPaper(Base):
    __tablename__ = "past_papers"
    #primary key
    id = Column(Integer, primary_key=True)
    #unit the past paper belongs to    unit_id = Column(Integer, ForeignKey("units.id"))
    unit_id = Column(Integer, ForeignKey("units.id"))
    #title of the past paper
    title = Column(String, index=True)
    #description of the past paper
    description = Column(Text)
    #url to download the past paper
    file_url = Column(String(300))
    #when the past paper was added to the system
    created_at = Column(DateTime, default=datetime.utcnow)


class PastPaperSubmission(Base):
    __tablename__ = "past_paper_submissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    past_paper_id = Column(Integer, ForeignKey("past_papers.id"))
    answer_text = Column(Text)
    score = Column(Integer)


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    study_hours_per_day = Column(Float, default=0.0)
    preferred_learning_style = Column(String(50)) 
    target_exam_date = Column(Date) 
    
    daily_reminder_time = Column(Time) 
    created_at = Column(DateTime, default=datetime.utcnow) 
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

 #topic mastery model to track student performance on different topics.   
class TopicMastery(Base):
    __tablename__ = "topic_mastery"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    topic_id = Column(Integer, ForeignKey("topics.id"))
    average_score = Column(Float, default=0.0)
    attempts = Column(Integer, default=0)
    mastery_level = Column(String(50))  # e.g., "beginner", "intermediate", "advanced"
    updated_at = Column(DateTime, default=datetime.utcnow)

class StudyPlan(Base):
    __tablename__ = "study_plans"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    topic_id = Column(Integer, ForeignKey("topics.id"))
    study_date = Column(Date)
    status = Column(String(50))  # e.g., "pending", "completed", "missed"
    created_at = Column(DateTime, default=datetime.utcnow)

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    recommendation_type = Column(Text)
    message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    reminder_time = Column(DateTime)
    message = Column(Text)
    status = Column(String(50), default="pending")  # e.g., "pending", "sent", "missed"
    created_at = Column(DateTime, default=datetime.utcnow)

    #add gamification elements like points, badges, and leaderboards to motivate students.
class Gamification(Base):
    __tablename__ = "user_points"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    points = Column(Integer, default=0)


class UserStreak(Base):
    __tablename__ = "user_streak"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    streak_count = Column(Integer, default=0)
    last_active_date = Column(Date)

    student = relationship("User", back_populates="streak")

class Badge(Base):
    __tablename__ = "badges"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    criteria = Column(Text)

class UserBadge(Base):
    __tablename__ = "user_badges"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    badge_id = Column(Integer, ForeignKey("badges.id"))
    awarded_at = Column(DateTime, default=datetime.utcnow)

#Notifications Table to store notifications for users.
class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    message = Column(Text)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("User", back_populates="notifications")