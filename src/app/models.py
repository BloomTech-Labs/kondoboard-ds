from pydantic import BaseModel

class Search(BaseModel):
    search: str
    location: str = None

class Track(BaseModel):
    track: str