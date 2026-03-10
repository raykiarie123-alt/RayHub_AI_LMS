#schemas define how data is sent and received in the API. They are used for validation and serialization of data.   
from pydantic import BaseModel

class UserRegister(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class CourseCreate(BaseModel):
    name: str
    description: str

class LevelCreate(BaseModel):
    name: str
    description: str
    price: int
    course_id: int

class UnitCreate(BaseModel):
    name: str
    content: str
    level_id: int

class TopicCreate(BaseModel):
    title: str
    content: str
    video_url: str
    unit_id: int