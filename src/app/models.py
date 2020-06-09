from pydantic import BaseModel
from typing import List, Dict

class All(BaseModel):
    lim: int = 20

class Search(BaseModel):
    search: str
    city: str = None
    state: str = None
    lim: int = 20


class Track(BaseModel):
    track: str
    city: str = None
    state: str = None
    lim = 20

class User(BaseModel):
    user_id: int
    track: str
    skills: str
    city: str
    state: str
    lim: int = 20
