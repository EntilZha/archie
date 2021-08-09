import os
import subprocess

import arrow
import requests
from fastapi import Depends, FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session

from archie.database import (
    SessionLocal,
    add_bookmark,
    add_clip,
    get_bookmark,
    get_recent_clip,
    list_bookmarks,
    list_clips,
    remove_bookmark,
)

app = FastAPI()

GOOGLE_SEARCH = "https://www.google.com/search?q=%s&btnK"
GOOGLE_SUGGEST_FF = "https://www.google.com/complete/search?client=firefox&q=%s"
GOOGLE_SUGGEST_OPERA = "https://www.google.com/complete/search?client=opera&q=%s"


class Clip(BaseModel):
    content: str


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


def tz_convert(datetime_str, src_tz, dst_tz):
    parsed_dt = arrow.get(datetime_str, tzinfo=src_tz)
    dt = parsed_dt.to(dst_tz)
    return {
        "input_datetime": datetime_str,
        "parsed_datetime": str(parsed_dt),
        "parsed_tz": str(parsed_dt.tzinfo),
        "converted_datetime": str(dt),
        "converted_tz": str(dt.tzinfo),
    }


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
    elif command == "tz":
        return tz_convert(tokens[1], tokens[2], tokens[3])
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


@app.get("/clip/paste")
async def paste(db: Session = Depends(get_db)):
    return get_recent_clip(db)


@app.post("/clip/copy")
async def copy(content: Clip, db: Session = Depends(get_db)):
    add_clip(db, content.content)


@app.get("/clip/list")
async def list_clip(db: Session = Depends(get_db)):
    return [c.content for c in list_clips(db)]


@app.get("/suggest/firefox")
async def ff_suggest(q: str):
    return requests.get(GOOGLE_SUGGEST_FF % q).json()


@app.get("/suggest/opera")
async def opera_suggest(q: str):
    return requests.get(GOOGLE_SUGGEST_OPERA % q).json()


@app.get("/yt-dl/list")
async def ytdl_list():
    return os.listdir("/fs/media/music")


@app.get("/yt-dl/download")
async def ytdl_download(url: str, folder: str):
    os.makedirs(f"/fs/media/music/{folder}/", exist_ok=True)
    subprocess.run(
        f"youtube-dl -x --audio-quality 0 --audio-format flac -w -o '/fs/media/music/{folder}/%(title)s-%(id)s.%(ext)s' '{url}'",
        shell=True,
    )
    return True


app.mount("/", StaticFiles(directory="static"), name="static")
