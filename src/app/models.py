from pydantic import BaseModel


class Search(BaseModel):
    search: str
    city: str = None
    state: str = None


class Track(BaseModel):
    track: str
    city: str = None
    state: str = None
