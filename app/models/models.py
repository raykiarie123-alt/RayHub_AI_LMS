from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime   
from app.database import Base


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


#create course model to represent courses in the system.
class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)  

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
    

    