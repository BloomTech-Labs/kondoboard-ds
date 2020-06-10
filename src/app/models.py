from pydantic import BaseModel
from typing import List, Dict


class Search(BaseModel):
    search: str
    city: str = None
    state: str = None


class Track(BaseModel):
    track: str
    city: str = None
    state: str = None

class User(BaseModel):
    user_id: int
    track: str
    skills: str
    city: str
    state: str
