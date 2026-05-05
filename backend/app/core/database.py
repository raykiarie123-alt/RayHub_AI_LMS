#connect your app to the database, Creates tables,Manages database sessions

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

#create the database engine using the DATABASE_URL from settings, with special handling for SQLite to allow multiple threads
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)
#create a session factory that will be used to create database sessions, with autocommit and autoflush disabled
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#create a base class for our database models to inherit from, which will include the metadata for creating tables
Base = declarative_base()

# Dependency function to get a database session, which will be used in our API endpoints to interact with the database. It ensures that the session is properly closed after use.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to create all database tables based on the models defined in our application. This should be called at the start of the application to ensure that the database schema is set up correctly.
def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)