import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from database import db, create_document, get_documents
from schemas import Subscriber, Message, Poem, Track, Event, Fanpost

app = FastAPI(title="Artist Portfolio API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Artist Portfolio API running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response


# ------- Artist-specific endpoints -------

@app.post("/api/subscribe")
def subscribe(sub: Subscriber):
    # prevent duplicate emails
    existing = db["subscriber"].find_one({"email": sub.email}) if db else None
    if existing:
        raise HTTPException(status_code=409, detail="Already subscribed")
    sub_id = create_document("subscriber", sub)
    return {"status": "ok", "id": sub_id}


@app.post("/api/message")
def send_message(msg: Message):
    msg_id = create_document("message", msg)
    return {"status": "ok", "id": msg_id}


@app.get("/api/poems", response_model=List[Poem])
def get_poems():
    docs = get_documents("poem", {}, limit=50)
    # Convert _id to string and map fields
    items = []
    for d in docs:
        d.pop("_id", None)
        items.append(Poem(**d))
    return items


@app.get("/api/tracks", response_model=List[Track])
def get_tracks():
    docs = get_documents("track", {}, limit=50)
    items = []
    for d in docs:
        d.pop("_id", None)
        items.append(Track(**d))
    return items


@app.get("/api/events", response_model=List[Event])
def get_events():
    docs = get_documents("event", {}, limit=50)
    items = []
    for d in docs:
        d.pop("_id", None)
        items.append(Event(**d))
    return items


# ------- Fan Wall with simple moderation -------

BAD_WORDS = {
    "spam",
    "scam",
    "fake",
    "hate",
    "abuse",
}


def is_clean(text: str) -> bool:
    t = (text or "").lower()
    for w in BAD_WORDS:
        if w in t:
            return False
    return True


@app.post("/api/fanwall")
def create_fanpost(post: Fanpost):
    # auto-flag if contains disallowed content
    approved = is_clean(post.message)
    data = post.model_dump()
    data["approved"] = approved
    post_id = create_document("fanpost", data)
    return {"status": "ok", "id": post_id, "approved": approved}


@app.get("/api/fanwall", response_model=List[Fanpost])
def list_fanposts():
    # only return approved posts to the public feed
    docs = get_documents("fanpost", {"approved": True}, limit=100)
    items: List[Fanpost] = []
    for d in docs:
        d.pop("_id", None)
        # Ensure approved True for response model
        d["approved"] = True
        items.append(Fanpost(**d))
    return items


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
