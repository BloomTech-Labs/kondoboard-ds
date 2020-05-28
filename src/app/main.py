import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from .queries import get_all_jobs
from .models import Search, Track

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """
    Verifies the API is deployed, and links to the docs
    """
    return HTMLResponse(
    """
    <h1>Kondoboard API</h1>
    <p>Go to <a href="/docs">/docs</a> for documentation.</p>
    """)

@app.get("/all")
async def search_all():
    """ 
    Get endpoint to return all jobs
    """
    all = get_all_jobs()
    return all

@app.post("/search/")
async def search_custom(search: Search):
    """
    Endpoint to return custom search when user specifies
    the location and enters in keywords  

    NOTE: will currently return the same jobs as endpoint /all  
    We will be updating this later
    """

    all = get_all_jobs()
    return all

@app.post("/track/")
async def search_by_track(track: Track):
    """ 
    Simple endpoint to return jobs recommended for
    a specific track

    NOTE: will currently return the same jobs as endpoint /all  
    We will be updating this later
    """
    all = get_all_jobs()
    return all