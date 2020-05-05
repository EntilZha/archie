import requests

from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from archie.database import (
    SessionLocal,
    get_bookmark,
    list_bookmarks,
    add_bookmark,
    remove_bookmark,
)


app = FastAPI()

GOOGLE_SEARCH = "https://www.google.com/search?q=%s&btnK"
GOOGLE_SUGGEST = (
    "http://suggestqueries.google.com/complete/search?output=firefox&hl=en&q=%s"
)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def handle_command(bookmark, terms):
    url = bookmark.url
    if len(terms) == 0:
        return RedirectResponse(url)
    else:
        args = " ".join(terms)
        return RedirectResponse(url % args)


@app.get("/list")
async def list_api(db: Session = Depends(get_db)):
    return list_bookmarks(db)


@app.get("/search")
async def search(q: str, db: Session = Depends(get_db)):
    tokens = q.split()
    command = tokens[0]
    print(command)
    if command == "add":
        new_command = tokens[1]
        new_target = " ".join(tokens[2:])
        success = add_bookmark(db, new_command, new_target)
        if success:
            return {
                "status": "Success: added",
                "command": new_command,
                "url": new_target,
            }
        else:
            return "Added: failed"
    elif command == "remove":
        new_command = tokens[1]
        remove_bookmark(db, new_command)
        return f"Removed: {new_command}"
    elif command == "list":
        return list_bookmarks(db)
    elif command == "help":
        return "TODO"
    else:
        bookmark = get_bookmark(db, command)
        if bookmark is None:
            return RedirectResponse(GOOGLE_SEARCH % q)
        else:
            return handle_command(bookmark, tokens[1:])


@app.get("/suggest")
async def suggest(q: str):
    return requests.get(GOOGLE_SUGGEST % q).json()


app.mount("/", StaticFiles(directory="static"), name="static")
