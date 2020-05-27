from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import pandas as pd
from pydantic import BaseModel

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
    return HTMLResponse("""
    <h1>Kondoboard API</h1>
    <p>Go to <a href="/docs">/docs</a> for documentation.</p>
    """)

class Story(BaseModel):
    title: str
    text: str

@app.post('/predict')
async def predict(story: Story):
    """
    THIS IS NOT TO BE USED. It is an example from Ryan Herr 
    lecture that will be removed..

    Predicts nothing really. Leftover endpoint from testing 

    Naive baseline: Always predicts 'fake'
    """
    # Doesn't do anything with the request body yet,
    # just verifies we can read it.
    print(story)
    X = pd.DataFrame([dict(story)])
    print(X.to_markdown())
    return {
        'prediction': 'fake', 
        'probability': 0.50
    }

