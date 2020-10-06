from typing import Optional, Dict, List
import os
import datetime

import toml

from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

SQLALCHEMY_DATABASE_URL = "sqlite:///data/archie.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


if os.path.exists("config.toml"):
    with open("config.toml") as f:
        config = toml.load(f)
else:
    with open("default.toml") as f:
        config = toml.load(f)


class Bookmark(Base):
    __tablename__ = "bookmarks"
    id = Column(Integer, primary_key=True, index=True)
    command = Column(String, unique=True, index=True)
    url = Column(String)


class Clip(Base):
    __tablename__ = "clips"
    id = Column(Integer, primary_key=True)
    created_time = Column(DateTime)
    content = Column(String)


def initialize_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    for command, url in config["initial_bookmarks"].items():
        bookmark = Bookmark(command=command, url=url)
        db.add(bookmark)
    db.commit()


def add_clip(db: Session, content: str):
    clip = Clip(created_time=datetime.datetime.now(), content=content)
    db.add(clip)
    db.commit()


def get_recent_clip(db: Session):
    maybe_clip = db.query(Clip).order_by(Clip.created_time.desc()).first()
    if maybe_clip is None:
        return ""
    else:
        return maybe_clip.content


def list_clips(db: Session) -> List[Clip]:
    return db.query(Clip).order_by(Clip.created_time.desc()).all()


def get_bookmark(db: Session, command: str) -> Optional[Bookmark]:
    return db.query(Bookmark).filter(Bookmark.command == command).first()


def add_bookmark(db: Session, command: str, url: str):
    maybe_bookmark = db.query(Bookmark).filter(Bookmark.command == command).first()
    if maybe_bookmark is None:
        bookmark = Bookmark(command=command, url=url)
        db.add(bookmark)
        db.commit()
        return True
    else:
        return False


def remove_bookmark(db: Session, command: str):
    maybe_bookmark = db.query(Bookmark).filter(Bookmark.command == command).first()
    if maybe_bookmark is not None:
        db.delete(maybe_bookmark)
        db.commit()


def list_bookmarks(db: Session) -> Dict[str, str]:
    bookmarks = db.query(Bookmark).all()
    return {b.command: b.url for b in bookmarks}
