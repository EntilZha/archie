from typing import Optional, Dict
import datetime

from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

SQLALCHEMY_DATABASE_URL = "sqlite:///./archie.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


INITIAL_BOOKMARKS = {
    "acl": "https://www.aclweb.org/anthology/search/?q=%s",
    "am": "https://www.amazon.com/s?k=%s",
    "apr": "https://www.archlinux.org/packages/?sort=&q=%s&maintainer=&flagged=",
    "aur": "https://aur.archlinux.org/packages/?O=0&SeB=nd&K=%s&outdated=&SB=n&SO=a&PP=50&do_Search=Go",
    "aws": "https://console.aws.amazon.com/",
    "benepar": "https://github.com/nikitakit/self-attentive-parser",
    "def": "https://www.lexico.com/en/definition/%s",
    "g": "https://www.google.com/search?q=%s&btnK",
    "gh": "https://github.com/search?q=%s&ref=opensearch",
    "gim": "https://www.google.com/search?q=%s&um=1&ie=UTF-8&hl=en&tbm=isch",
    "gm": "http://maps.google.com/maps?q=%s",
    "hub": "https://github.com",
    "iclr": "https://openreview.net/search?term=test&content=all&group=all&source=all",
    "imdb": "http://www.imdb.com/find?q=%s",
    "majora": "https://materiacollective.store/collections/times-end-majoras-mask-remixed",
    "p9": "https://plotnine.readthedocs.io/en/stable/search.html?q=%s&check_keywords=yes&area=default",
    "py": "https://docs.python.org/3/search.html?q=%s",
    "r": "https://www.reddit.com/r/%s",
    "rmtg": "https://www.reddit.com/r/magicTCG/",
    "rterra": "https://www.reddit.com/r/LegendsOfRuneterra/",
    "sc": "https://www.semanticscholar.org/search?q=%s&sort=relevance",
    "scry": "https://scryfall.com/search?q=%s",
    "wiki": "http://en.wikipedia.org/?search=%s",
    "ynews": "https://news.ycombinator.com/",
    "yt": "http://www.youtube.com/results?search_type=search_videos&search_sort=relevance&search_query=%s&search=Search",
}


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
    for command, url in INITIAL_BOOKMARKS.items():
        bookmark = Bookmark(command=command, url=url)
        db.add(bookmark)
    db.commit()


def add_clip(db: Session, content: str):
    clip = Clip(created_time=datetime.datetime.now(), content=content)
    db.add(clip)
    db.commit()


def get_recent_clip(db: Session):
    maybe_clip = db.query(Clip).order_by(Clip.created_time.desc).first()
    if maybe_clip is None:
        return ""
    else:
        return maybe_clip.content


def list_clips(db: Session) -> List[Clip]:
    return db.query(Clip).all()


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
