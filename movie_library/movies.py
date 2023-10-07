from dataclasses import dataclass, field


@dataclass
class Movie:
    _id: str
    title: str
    director: str = None
    year: int = None
    cast: list[str] = field(default_factory=list)
    series: list[str] = field(default_factory=list)
    last_watched: str = None
    rating: int = 0
    tags: list[str] = field(default_factory=list)
    description: str = None
    video_link: str = None


@dataclass
class User:
    _id: str
    email: str
    password: str
    movies: list[str] = field(default_factory=list)
