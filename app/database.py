from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./rayhub.db"

#create_engine() function is used to create a new SQLAlchemy engine instance.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}      
)


#sessionmaker() function is used to create a new SQLAlchemy session factory.
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False,
    bind=engine
    )

#declarative_base() function is used to create a new base class for declarative class definitions.
Base = declarative_base()   

#get_db() function is a dependency that provides a database session to the API endpoints. It creates a new session, yields it to the endpoint, and ensures that the session is closed after the request is completed.
from sqlalchemy.orm import Session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        