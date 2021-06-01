import yaml
import discord

try:
    with open("config.yml", "r") as f:
        config = yaml.safe_load(f)
except FileNotFoundError:
    raise RuntimeError("You have no config.yml file setup! Please make one using the config.yml.example file!")

bot_token = config.get("token")
if not bot_token:
    raise RuntimeError("No token is provided! Please get a token and add it to the config.yml file!")

postgres_dsn = config.get("postgres_dsn")
if not postgres_dsn:
    raise RuntimeError("No Postgres DSN has been provided!")

prefix = config.get("prefix", "!")

activity = None
_activity = config.get("activity")
if _activity:
    _valid_types = {
        "playing": 0,
        "streaming": 1,
        "listening": 2,
        "watching": 3,
        "competing": 5
    }
    _activity_type = _activity.get("type")
    if _activity_type not in _valid_types:
        raise RuntimeError(f"Activity Type must be one of {', '.join(_valid_types)}")
    _type = _valid_types.get(_activity_type)
    _url = _activity.get("url")
    if _url == "":
        _url = None
    if _url is None and _type == 1:
        raise RuntimeError("You must provide a url if your activity type is 'streaming'")
    activity = discord.Activity(type=_type, name=_activity.get("name"), url=_url)

status = config.get("status", "online")
_valid_status = ("online", "offline", "idle", "dnd")
if status not in _valid_status:
    raise RuntimeError(f"Status must be one of {', '.join(_valid_status)}")



