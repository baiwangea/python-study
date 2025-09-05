import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from app.api.v1.api import api_router

app = FastAPI(
    title="FastAPI Project",
    description="A modern FastAPI project structure",
    version="0.1.0"
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to the modern FastAPI project!"}