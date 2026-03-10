from fastapi import FastAPI
from app.database import engine, Base
from app.models import models
from app.routes import course_routes

# Create the database tables
Base.metadata.create_all(bind=engine)   

app = FastAPI(
    title="RayHub AI LMS",
    description="AI Powered CPA Learning Management System",
    version="1.0.0"
)

@app.get("/")
def home():
    return {"message": "Welcome to RayHub AI LMS!"}

app.include_router(course_routes.router)

from app.routes import auth_routes
app.include_router(auth_routes.router)
