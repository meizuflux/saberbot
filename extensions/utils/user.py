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
        return cls(
            name=json['name'],
            url=json['url']
        )


class ScoreStat:
    def __init__(self, total: int, ranked: int):
        self.total = total
        self.ranked = ranked
        self.unranked = total - ranked

    @classmethod
    def from_json(cls, json):
        json = loads(json)
        return cls(
            total=json['total'],
            ranked=json['ranked']
        )


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
            id=data['user_id'],
            scoresaber_id=data['scoresaber_id'],
            pp=data['user_id'],
            change=data['change'],
            favorite_song=Favorite.from_json(data['favorite_song']),
            favorite_saber=Favorite.from_json(data['favorite_saber']),
            play_count=ScoreStat.from_json(data['play_count']),
            score=ScoreStat.from_json(data['score']),
            average_accuracy=data['average_accuracy'],
            headset=data['headset'],
            grip=data['grip']
        )
