from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 
from fastapi.staticfiles import StaticFiles
import os

from app.core.config import settings
from app.core.database import create_tables
from app.core.vector_store_instance import init_vector_store

# Import all models to ensure they are registered with SQLAlchemy
import app.models  # noqa

# Import routers
from app.api.routes.auth import router as auth_router
from app.api.routes.users import router as users_router
from app.api.routes.courses import router as courses_router, levels_router
from app.api.routes.units import router as units_router
from app.api.routes.topics import router as topics_router
from app.api.routes.documents import router as documents_router
from app.api.routes.youtube import router as youtube_router
from app.api.routes.resources import router as web_router
from app.api.routes.rag import router as rag_router
from app.api.routes.quizzes import router as quizzes_router
from app.api.routes.flashcards import router as flashcards_router
from app.api.routes.study_plans import router as study_plans_router
from app.api.routes.progress import router as progress_router
from app.api.routes.gamification import router as gamification_router
from app.api.routes.community import router as community_router
from app.api.routes.admin import router as admin_router
from app.api.routes.resources import router as resources_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered CPA Learning Management System with RAG, personalized study plans, and intelligent assessments.",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list + ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for uploads
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Register all routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(levels_router)
app.include_router(courses_router)
app.include_router(units_router)
app.include_router(topics_router)
app.include_router(resources_router)
app.include_router(documents_router)
app.include_router(youtube_router)
app.include_router(web_router)
app.include_router(rag_router)
app.include_router(quizzes_router)
app.include_router(flashcards_router)
app.include_router(study_plans_router)
app.include_router(progress_router)
app.include_router(gamification_router)
app.include_router(community_router)
app.include_router(admin_router)


@app.on_event("startup")
async def startup_event():
    """Initialize database tables and vector store on startup."""
    create_tables()
    init_vector_store()
    _seed_initial_data()
    print(f"✅ {settings.APP_NAME} v{settings.APP_VERSION} started successfully")


def _seed_initial_data():
    """Seed initial CPA levels, courses, and badges if not present."""
    from app.core.database import SessionLocal
    from app.models.course import Level, Course, Unit, Topic
    from app.models.gamification import Badge
    from app.utils.constants import DEFAULT_UNITS, BADGES

    db = SessionLocal()
    try:
        # Seed levels
        if db.query(Level).count() == 0:
            levels_data = [
                {"name": "Foundation", "description": "Entry-level CPA subjects", "order": 1},
                {"name": "Intermediate", "description": "Intermediate CPA subjects", "order": 2},
                {"name": "Advanced", "description": "Advanced CPA subjects", "order": 3},
                {"name": "Post-Qualification", "description": "Specialized subjects for qualified CPAs", "order": 4}
            ]
            levels = {}
            for ld in levels_data:
                level = Level(**ld)
                db.add(level)
                db.flush()
                levels[ld["name"]] = level

            # Seed courses and units
            for level_name, unit_titles in DEFAULT_UNITS.items():
                level = levels.get(level_name)
                if not level:
                    continue
                course = Course(
                    title=f"CPA {level_name}",
                    description=f"Complete CPA {level_name} program",
                    level_id=level.id
                )
                db.add(course)
                db.flush()

                for i, unit_title in enumerate(unit_titles):
                    unit = Unit(
                        title=unit_title,
                        description=f"{unit_title} - CPA {level_name}",
                        course_id=course.id,
                        order=i + 1
                    )
                    db.add(unit)
                    db.flush()

                    # Add sample topics for each unit
                    sample_topics = _get_sample_topics(unit_title)
                    for j, topic_title in enumerate(sample_topics):
                        topic = Topic(
                            title=topic_title,
                            description=f"{topic_title} in {unit_title}",
                            unit_id=unit.id,
                            order=j + 1,
                            estimated_hours=2
                        )
                        db.add(topic)

            db.commit()

        # Seed badges
        if db.query(Badge).count() == 0:
            for key, badge_def in BADGES.items():
                badge = Badge(
                    key=key,
                    name=badge_def["name"],
                    description=badge_def["description"],
                    icon=badge_def["icon"],
                    xp_reward=50
                )
                db.add(badge)
            db.commit()

    finally:
        db.close()


def _get_sample_topics(unit_title: str) -> list:
    """Return sample topics for a given unit."""
    topics_map = {
        "Financial Accounting": ["Introduction to Accounting", "Double Entry Bookkeeping", "Trial Balance", "Financial Statements", "Adjusting Entries"],
        "Audit and Assurance": ["Audit Risk", "Internal Controls", "Audit Evidence", "Audit Planning", "Audit Reports"],
        "Taxation": ["Income Tax Basics", "VAT Principles", "Corporate Tax", "Tax Planning", "Tax Returns"],
        "Management Accounting": ["Cost Classification", "Budgeting", "Variance Analysis", "Break-even Analysis", "Decision Making"],
        "Company Law": ["Company Formation", "Directors Duties", "Shareholders Rights", "Corporate Governance", "Winding Up"],
        "Financial Reporting": ["IFRS Standards", "Revenue Recognition", "Leases", "Financial Instruments", "Consolidation"],
        "Advanced Financial Reporting": ["Group Accounts", "Foreign Currency", "Share-based Payments", "Impairment", "Disclosure"],
        "Advanced Audit": ["Risk Assessment", "Fraud Detection", "IT Audit", "Group Audit", "Quality Control"],
        "Advanced Taxation": ["International Tax", "Transfer Pricing", "Tax Investigations", "Estate Planning", "Tax Treaties"],
        "Public Finance": ["Government Budgeting", "Public Expenditure", "Fiscal Policy", "Public Debt", "Accountability"],
    }
    return topics_map.get(unit_title, ["Introduction", "Core Concepts", "Advanced Topics", "Practice Questions", "Exam Preparation"])


@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy", "app": settings.APP_NAME}