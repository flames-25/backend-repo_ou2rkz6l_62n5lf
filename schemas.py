"""
Database Schemas for the Artist Portfolio

Each Pydantic model corresponds to a MongoDB collection. The collection name
is the lowercase of the class name (e.g., Subscriber -> "subscriber").
"""
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr

class Subscriber(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Fan name")
    email: EmailStr = Field(..., description="Email for updates/newsletter")
    source: Optional[str] = Field(None, description="Where the signup came from")

class Message(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    message: str = Field(..., min_length=1, max_length=1000)
    social: Optional[str] = Field(None, description="Optional social handle or link")

class Poem(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    body: str = Field(..., min_length=1)
    tags: List[str] = Field(default_factory=list)

class Track(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    platform_url: Optional[str] = Field(None, description="Link to listen")

class Event(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    date_iso: str = Field(..., description="ISO datetime string of event start")
    location: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
