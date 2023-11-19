from dataclasses import dataclass, field
from typing import List


@dataclass
class Movie:
    # Data class representing movie details
    _id: str
    title: str
    director: str = None
    year: int = None
    last_watched: str = None
    rating: int = 0
    tag1: str = None
    tag2: str = None
    video_link: str = None


@dataclass
class User:
    # Data class representing user details
    _id: str
    email: str
    password: str
    movies: List[str] = field(default_factory=list)
