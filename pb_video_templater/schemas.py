"""Pydantic's models."""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class Item(BaseModel):
    uid: int
    name: str
    date: datetime
    link: Optional[str]
    in_working: bool


class Page(BaseModel):
    items: list[Item] = []
