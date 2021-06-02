from dataclasses import dataclass
from json import loads

from discord.ext import commands


class InvalidHeadsetError(commands.BadArgument):
    """Error raised when a user inputs an invalid headset"""


@dataclass
class Favorite:
    name: str
    url: str

    @classmethod
    def from_json(cls, json):
        json = loads(json)
        return cls(name=json.get("name"), url=json.get("url"))


class ScoreStat:
    def __init__(self, total: int, ranked: int):
        self.total = total
        self.ranked = ranked
        self.unranked = None
        if total is not None and ranked is not None:
            self.unranked = total - ranked

    @classmethod
    def from_json(cls, json):
        json = loads(json)
        return cls(total=json.get("total"), ranked=json.get("ranked"))


@dataclass
class User:
    id: int
    scoresaber_id: str
    pp: float
    change: int
    play_count: ScoreStat
    score: ScoreStat
    average_accuracy: float
    favorite_song: Favorite
    favorite_saber: Favorite
    headset: str
    grip: str

    @classmethod
    def from_json(cls, data):
        return cls(
            id=data.get("user_id"),
            scoresaber_id=data.get("scoresaber_id"),
            pp=data.get("pp"),
            change=data.get("change"),
            favorite_song=Favorite.from_json(data.get("favorite_song", "{}")),
            favorite_saber=Favorite.from_json(data.get("favorite_saber", "{}")),
            play_count=ScoreStat.from_json(data.get("play_count", "{}")),
            score=ScoreStat.from_json(data.get("score", "{}")),
            average_accuracy=data.get("average_accuracy"),
            headset=data.get("headset"),
            grip=data.get("grip"),
        )
