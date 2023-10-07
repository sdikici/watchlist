from dataclasses import dataclass, field
from typing import List


@dataclass
class Movie:
    _id: str
    title: str
    director: str = None
    year: int = None
    last_watched: str = None
    rating: int = 0
    tags: List[str] = field(default_factory=list)
    video_link: str = None


@dataclass
class User:
    _id: str
    email: str
    password: str
    movies: List[str] = field(default_factory=list)
