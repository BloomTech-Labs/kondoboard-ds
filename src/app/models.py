from pydantic import BaseModel
from typing import List, Dict


class Search(BaseModel):
    search: str
    city: str = None
    state: str = None


class User(BaseModel):
    user_id: int = None
    track: str = None
    skills: str = None
    city: str = None
    state: str = None
