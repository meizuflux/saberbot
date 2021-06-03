import re
from json import dumps
from math import ceil
from typing import Optional, Union

import discord
from discord.ext import commands

from bot import Bot
from extensions.utils.user import User

BEATSAVER_SONG_REGEX = re.compile(r"https?://beatsaver\.com/beatmap/(?P<key>[0-9a-zA_Z]+)")
MODELSABER_VALIDATION_REGEX = re.compile(
    r"https?://modelsaber\.com/sabers/\?id=(?P<id>[0-9a-zA_Z]+)"
)


class MiscButton(discord.ui.Button):
    view: "ProfileView"

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(embed=await self.view.misc_embed)


class MainButton(discord.ui.Button):
    view: "ProfileView"

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(embed=self.view.profile_embed)


class StopButton(discord.ui.Button):
    def __init__(
        self,
        *,
        style: discord.ButtonStyle = discord.ButtonStyle.red,
        label: Optional[str] = "Stop",
        disabled: bool = False,
        custom_id: Optional[str] = None,
        emoji: Optional[Union[str, discord.PartialEmoji]] = None,
        row: Optional[int] = None,
    ):
        super().__init__(
            style=style, label=label, disabled=disabled, custom_id=custom_id, emoji=emoji, row=row
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.message.delete()


class ProfileView(discord.ui.View):
    def __init__(self, user: User, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.ctx.author.id

    @property
    def profile_embed(self):
        if not hasattr(self, "_profile_embed"):
            user = self.user
            embed = discord.Embed(
                title=f"{user.name}'s Profile",
                color=self.ctx.bot.scoresaber_color,
                url="https://new.scoresaber.com/u/" + user.id,
            )
            embed.set_thumbnail(url="https://new.scoresaber.com" + user.avatar)

            country_url = f"[#{user.country_rank:,d}](https://scoresaber.com/global/{ceil(user.country_rank / 50)}&country={user.country})"
            info_msg = (
                f"**PP:** {user.pp}\n"
                f"**Rank:** [#{user.rank:,d}](https://new.scoresaber.com/rankings/{ceil(user.rank / 50)})\n"
                f"**Country Rank:** :flag_{user.country.lower()}: {country_url}\n"
                f"**7 Day Change:** {user.change}"
            )
            if role := user.role:
                info_msg += f"\n**Role:** {role}"
            embed.add_field(name="Player Info:", value=info_msg)

            score_msg = (
                f"**Average Ranked Accuracy:** {user.ranked_accuracy:.2f}\n"
                f"**Unranked Score:** {user.score.unranked:,d}\n"
                f"**Ranked Score:** {user.score.ranked:,d}\n"
                f"**Unranked Play Count:** {user.play_count.unranked:,d}\n"
                f"**Ranked Play Count:** {user.play_count.ranked:,d}"
            )
            embed.add_field(name="Score Stats:", value=score_msg, inline=False)
            self._profile_embed = embed
        return self._profile_embed

    @property
    async def misc_embed(self):
        if not hasattr(self, "_misc_embed"):
            bot: Bot = self.ctx.bot
            embed = discord.Embed(title="Misc")
            query = """
                SELECT
                    song, saber, hmd, grip
                FROM 
                    users 
                WHERE 
                    id = $1
                """
            items = await bot.pool.fetchrow(query, self.user.id)
            user = User.from_psql(items)
            song = (
                f"[{user.song.name}]({user.song.url})"
                if user.song.name is not None
                else "This user has not set a favorite song."
            )
            saber = (
                f"[{user.saber.name}]({user.saber.url})"
                if user.saber.name is not None
                else "This user has not set a favorite saber."
            )
            hmd = user.hmd or "This user has not set which headset they use."
            grip = user.grip or "This user has not specified which grip they use."
            embed.description = (
                f"**Favorite Song:** {song}\n"
                f"**Favorite Saber:** {saber}\n"
                f"**Headset:** {hmd}\n"
                f"**Grip:** {grip}"
            )
            self._misc_embed: discord.Embed = embed

        self._misc_embed.color = self.ctx.bot.cc_color
        return self._misc_embed

    async def start(self, ctx: commands.Context):
        self.ctx = ctx
        await self.ctx.send(embed=self.profile_embed, view=self)


class SettingButton(discord.ui.Button["SettingView"]):
    def __init__(self, setting, *, label):
        super().__init__(style=discord.ButtonStyle.blurple, label=label)
        self.setting = setting

    async def callback(self, interaction: discord.Interaction):
        func = getattr(self.view, "set_" + self.setting, None)
        if func is not None:
            await func(interaction)
        await interaction.message.delete()


class SettingView(discord.ui.View):
    editable = ("favorite_song", "favorite_saber", "headset", "grip")

    def __init__(self, ctx: commands.Context):
        super().__init__()
        self.ctx = ctx
        for i in self.editable:
            self.add_item(SettingButton(i, label=i.replace("_", " ").title()))
        self.add_item(StopButton())

    @staticmethod
    async def send_confirmed(interaction: discord.Interaction, message: str) -> None:
        webhook = interaction.followup
        await webhook.send(message, ephemeral=True)

    async def update(self, item, value):
        pool = self.ctx.bot.pool
        query = f"""
            UPDATE
                users
            SET
                {item} = $1
            WHERE
                snowflake = $2
            """
        await pool.execute(query, value, self.ctx.author.id)

    async def set_favorite_song(self, interaction: discord.Interaction):
        ctx = self.ctx
        await interaction.response.send_message(
            "Please send the BeatSaver url of your favorite song.", ephemeral=True
        )
        try:
            response = await ctx.bot.wait_for(
                "message",
                check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
                timeout=60,
            )
        except TimeoutError:
            await interaction.response.send_message("You did not respond in time.", empheral=True)
        else:
            content = response.content.lower().strip("<>")
            if not (key_match := BEATSAVER_SONG_REGEX.fullmatch(content)):
                await interaction.followup.send("Please send a BeatSaver url.", ephemeral=True)
            else:
                key = key_match["key"]
                url = "https://beatsaver.com/api/maps/detail/" + key
                async with ctx.bot.session.get(url) as resp:
                    if not resp.ok:
                        return await interaction.followup.send(
                            f"Something went wrong: HTTP Error code {resp.status}", ephemeral=True
                        )
                    song_name = (await resp.json())["name"]
                    song_url = "https://beatsaver.com/beatmap/" + key
                json = dumps({"name": song_name, "url": song_url})
                await self.update("song", json)
                await self.send_confirmed(
                    interaction, f"I have set your favorite song to [`{song_name}`]({song_url})"
                )

    async def set_favorite_saber(self, interaction: discord.Interaction):
        ctx = self.ctx
        await interaction.response.send_message(
            "Please send the ModelSaber url of your favorite saber.", ephemeral=True
        )
        try:
            response = await ctx.bot.wait_for(
                "message",
                check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
                timeout=60,
            )
        except TimeoutError:
            await interaction.response.send_message("You did not respond in time.", empheral=True)
        else:
            content = response.content.lower().strip("<>").rstrip("&pc")
            if not (id_match := MODELSABER_VALIDATION_REGEX.fullmatch(content)):
                await interaction.followup.send(
                    "Please send a valid ModelSaber url.", ephemeral=True
                )
            else:
                _id = id_match["id"]
                url = "https://modelsaber.com/api/v2/get.php?type=saber&filter=id:" + _id
                async with ctx.bot.session.get(url) as resp:
                    if not resp.ok:
                        return await interaction.followup.send(
                            f"Something went wrong: HTTP Error code {resp.status}", ephemeral=True
                        )
                    data = await resp.json()
                    if not data:
                        return await interaction.followup.send(
                            f"Invalid URL provided.", ephemeral=True
                        )
                    for i in data.values():
                        saber_name = i["name"]
                        break
                    saber_url = "https://modelsaber.com/Sabers/?id=" + _id
                json = dumps({"name": saber_name, "url": saber_url})
                await self.update("saber", json)
                await self.send_confirmed(
                    interaction, f"I have set your favorite saber to [`{saber_name}`]({saber_url})"
                )

    async def set_headset(self, interaction: discord.Interaction):
        embed = discord.Embed(
            description="Please click the button that resembles which headset you prefer to use.",
            color=self.ctx.bot.cc_color,
        )
        await interaction.response.send_message(
            embed=embed, ephemeral=True, view=HeadsetView(parent=self)
        )

    async def set_grip(self, interaction: discord.Interaction):
        ctx = self.ctx
        bot = ctx.bot
        await interaction.response.send_message(
            "Please send the grip you prefer to use.", ephemeral=True
        )
        try:
            response = await bot.wait_for(
                "message",
                check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
                timeout=30,
            )
        except TimeoutError:
            await interaction.response.send_message("You did not respond in time.", empheral=True)
        else:
            grip = response.content

            await self.update("grip", grip)
            message = f"I have set your grip to `{grip}`"
            await self.send_confirmed(interaction, message)


class HeadsetButton(discord.ui.Button["HeadsetView"]):
    def __init__(
        self,
        *,
        style: discord.ButtonStyle = discord.ButtonStyle.blurple,
        label: Optional[str] = None,
        disabled: bool = False,
        custom_id: Optional[str] = None,
        emoji: Optional[Union[str, discord.PartialEmoji]] = None,
        row: Optional[int] = None,
    ):
        if label == "Other":
            style = discord.ButtonStyle.secondary
        super().__init__(
            style=style, label=label, disabled=disabled, custom_id=custom_id, emoji=emoji, row=row
        )

    async def callback(self, interaction: discord.Interaction):
        await self.view.parent.update("hmd", self.label)
        await interaction.response.send_message(
            f"I set your preferred headset to `{self.label}`", ephemeral=True
        )


class HeadsetView(discord.ui.View):
    headsets = (
        "Oculus Rift CV1",
        "Oculus Rift S",
        "Oculus Quest",
        "Oculus Quest 2",
        "Valve Index",
        "HTC Vive",
        "HTC Vive (Pro)",
        "Other",
    )

    def __init__(self, parent: SettingView):
        super().__init__()
        for i in self.headsets:
            self.add_item(HeadsetButton(label=i))
        self.parent = parent
