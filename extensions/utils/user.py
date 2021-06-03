from dataclasses import dataclass
from json import loads
from typing import List, Optional

from asyncpg import Record

from extensions.utils.__init__ import find_change


@dataclass
class Favorite:
    name: str
    url: str


class ScoreStat:
    def __init__(self, total: int, ranked: int):
        self.total = total
        self.ranked = ranked
        self.unranked = None
        if total is not None and ranked is not None:
            self.unranked = total - ranked


@dataclass
class User:
    snowflake: Optional[int]
    id: str
    name: str
    avatar: str
    country: str
    pp: float
    rank: int
    country_rank: int
    role: Optional[str]
    history: List[int]
    change: int

    ranked_accuracy: float
    score: ScoreStat
    play_count: ScoreStat

    song: Optional[Favorite]
    saber: Optional[Favorite]
    hmd: Optional[str]
    grip: Optional[str]

    @classmethod
    def from_psql(cls, data: Record) -> "User":
        history = data.get("history")

        song = loads(data.get("song", {}))
        saber = loads(data.get("saber", {}))

        return cls(
            snowflake=data.get("snowflake"),
            id=data.get("id"),
            name=data.get("name"),
            avatar=data.get("avatar"),
            country=data.get("country"),
            pp=data.get("pp"),
            rank=data.get("rank"),
            country_rank=data.get("country_rank"),
            role=data.get("player_role"),
            history=history,
            change=find_change(data.get("rank"), history),
            ranked_accuracy=data.get("ranked_acc"),
            score=ScoreStat(data.get("total_score"), data.get("ranked_score")),
            play_count=ScoreStat(data.get("total_played"), data.get("ranked_played")),
            song=Favorite(song.get("name"), song.get("url")),
            saber=Favorite(saber.get("name"), saber.get("url")),
            hmd=data.get("hmd"),
            grip=data.get("grip")
        )

    @classmethod
    def from_json(cls, data: dict) -> "User":
        info = data["playerInfo"]
        score = data["scoreStats"]

        history = [int(c) for c in info["history"].split(",")]

        return cls(
            snowflake=None,
            id=info["playerId"],
            name=info["playerName"],
            avatar=info["avatar"],
            country=info["country"],
            pp=info["pp"],
            rank=info["rank"],
            country_rank=info["countryRank"],
            role=info["role"],
            history=history,
            change=find_change(info["rank"], history),
            ranked_accuracy=score["averageRankedAccuracy"],
            score=ScoreStat(score["totalScore"], score["totalRankedScore"]),
            play_count=ScoreStat(score["totalPlayCount"], score["rankedPlayCount"]),
            song=None,
            saber=None,
            hmd=None,
            grip=None
        )

    def to_json(self) -> dict:
        return {
            "playerInfo": {
                "playerId": self.id,
                "playerName": self.name,
                "avatar": self.avatar,
                "rank": self.rank,
                "countryRank": self.country_rank,
                "pp": self.pp,
                "country": self.country,
                "role": self.role,
                "history": ",".join(str(c) for c in self.history),
            },
            "scoreStats": {
                "totalScore": self.score.total,
                "totalRankedScore": self.score.ranked,
                "averageRankedAccuracy": self.ranked_accuracy,
                "totalPlayCount": self.play_count.total,
                "rankedPlayCount": self.play_count.ranked,
            },
        }
