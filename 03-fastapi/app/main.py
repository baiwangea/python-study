import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from app.api.v1.api import api_router

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db
from app.schemas.item import Item, ItemCreate, ItemUpdate
from app.models.item import Item as ItemModel

app = FastAPI(
    title="FastAPI Project",
    description="A modern FastAPI project structure",
    version="0.1.0"
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to the modern FastAPI project!"}

@app.get("/items")
async def read_items(db: Session = Depends(get_db)):
    item = db.query(ItemModel).filter(ItemModel.id == 2).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
