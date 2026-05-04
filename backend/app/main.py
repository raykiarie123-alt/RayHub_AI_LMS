from fastapi import FastAPI
from app.core.database import create_tables
from app.core.vector_store_instance import init_vector_store

app = FastAPI(title="RayHub AI LMS")


@app.on_event("startup")
def startup():
    create_tables()
    init_vector_store()


@app.get("/")
def root():
    return {"message": "RayHub AI LMS is running 🚀"}