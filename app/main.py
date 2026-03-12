from fastapi import FastAPI
from app.database import engine, Base
from app.models import models
from app.routes import course_routes
from app.routes import student_routes
from app.routes import quiz_routes
from app.routes import auth_routes
from app.routes import pastpaper_routes 

# Create the database tables
models.Base.metadata.create_all(bind=engine)   

app = FastAPI(
    title="RayHub",
    description="AI Powered CPA Learning Management System",
    version="1.0.0"
)

@app.get("/")
def home():
    return {"message": "Welcome to RayHub AI LMS!"}

app.include_router(course_routes.router)

app.include_router(auth_routes.router)

app.include_router(quiz_routes.router)

app.include_router(student_routes.router)

app.include_router(pastpaper_routes.router)