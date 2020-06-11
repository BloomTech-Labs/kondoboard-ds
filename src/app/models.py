from pydantic import BaseModel


class Search(BaseModel):
    search: str
    city: str = None
    state: str = None


class User(BaseModel):
    user_id: str = None
    track: str = None
    skills: str = None
    city: str = None
    state: str = None
