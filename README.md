# SaberBot
BeatSaber bot for the [Cube Community](https://cube.community) Discord

## Running the bot
Instructions to run the bot

> ### 1. **Cloning the Repo**

```bash
git clone https://github.com/ppotatoo/saberbot
cd saberbot
```

> ### 2. **Install Python**

For the rest of this readme, we will use `python3.9` in all of our commands. This may change depending on which version of Python you have installed. You can download Python from [here](https://www.python.org/downloads/).

> ### 3. **Install dependencies**

Simple, just run this:
```bash
python3.9 -m pip install -U -r requirements.txt
```
> ### 4. **Create database**

Install a recent version of PostgreSQL. This varies from system to system so I will leave it out of here. Once you are done this, create a user and a db like so: 
```psql
CREATE ROLE ccbot WITH LOGIN PASSWORD '<your password>';
CREATE DATABASE ccbot OWNER ccbot;
```

> ### 5. **Configure the bot**

Fill out the config.toml.example file. When you are done, make sure to remove the `.example` from the filename otherwise the bot will not recognize it.

> ### 6. **Run the bot**

Simply run the bot with this command: 
```bash
python3.9 launch.py
```
That's it. If you wish to change the prefix, add a `--prefix` flag when running as such:
```bash
python3.9 launch.py --prefix "<enter your prefix>"
```
The prefix defaults to `!`




