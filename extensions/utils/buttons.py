import re
from json import dumps
from math import ceil
from typing import Optional, Union

import discord
from discord.ext import commands

from bot import Bot
from extensions.utils.user import User

BEATSAVER_SONG_REGEX = re.compile(r"https?://beatsaver\.com/beatmap/(?P<key>[0-9a-zA_Z]+)")


class MiscButton(discord.ui.Button):
    view: 'ProfileView'

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(embed=await self.view.misc_embed)


class MainButton(discord.ui.Button):
    view: 'ProfileView'

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(embed=self.view.profile_embed)


class StopButton(discord.ui.Button):
    def __init__(
            self,
            *,
            style: discord.ButtonStyle = discord.ButtonStyle.red,
            label: Optional[str] = 'Stop',
            disabled: bool = False,
            custom_id: Optional[str] = None,
            emoji: Optional[Union[str, discord.PartialEmoji]] = None,
            row: Optional[int] = None,
    ):
        super().__init__(
            style=style,
            label=label,
            disabled=disabled,
            custom_id=custom_id,
            emoji=emoji,
            row=row
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.message.delete()


class ProfileView(discord.ui.View):
    def __init__(self, data: dict, *args, **kwargs):
        self.profile_data = data
        self.scoresaber_id = data['playerInfo']['playerId']
        super().__init__(*args, **kwargs)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.ctx.author.id

    @property
    def profile_embed(self):
        if not hasattr(self, '_profile_embed'):
            player_info = self.profile_data['playerInfo']
            score_stats = self.profile_data['scoreStats']
            embed = discord.Embed(
                title=f"{player_info['playerName']}'s Profile",
                color=self.ctx.bot.scoresaber_color,
                url="https://new.scoresaber.com/u/" + player_info['playerId']
            )
            embed.set_thumbnail(url="https://new.scoresaber.com" + player_info['avatar'])

            country_url = f"[#{player_info['countryRank']:,d}](https://scoresaber.com/global/{ceil(player_info['countryRank'] / 50)}&country={player_info['country']})"
            info_msg = (
                f"**PP:** {player_info['pp']}\n"
                f"**Rank:** [#{player_info['rank']:,d}](https://new.scoresaber.com/rankings/{ceil(player_info['rank'] / 50)})\n"
                f"**Country Rank:** :flag_{player_info['country'].lower()}: {country_url}"
            )
            if role := player_info['role']:
                info_msg += f"\n**Role:** {role}"
            embed.add_field(name="Player Info:", value=info_msg)

            score_msg = (
                f"**Average Ranked Accuracy:** {score_stats['averageRankedAccuracy']:.2f}\n"
                f"**Total Score:** {score_stats['totalScore']:,d}\n"
                f"**Total Ranked Score:** {score_stats['totalRankedScore']:,d}\n"
                f"**Total Play Count:** {score_stats['totalPlayCount']:,d}\n"
                f"**Ranked Play Count:** {score_stats['rankedPlayCount']:,d}"
            )
            embed.add_field(name="Score Stats:", value=score_msg, inline=False)
            self._profile_embed = embed
        return self._profile_embed

    @property
    async def misc_embed(self):
        if not hasattr(self, '_misc_embed'):
            bot: Bot = self.ctx.bot
            embed = discord.Embed(title="Misc")
            query = (
                """
                SELECT
                    favorite_song, favorite_saber, headset, grip
                FROM 
                    users 
                WHERE 
                    scoresaber_id = $1
                """
            )
            items = await bot.pool.fetchrow(query, self.scoresaber_id)
            user = User.from_json(items)
            song = f"[{user.favorite_song.name}]({user.favorite_song.url})" if user.favorite_song.url is not None else "This user has not set a favorite song."
            saber = f"[{user.favorite_saber.name}]({user.favorite_saber.url})" if user.favorite_saber.url is not None else "This user has not set a favorite saber."
            headset = user.headset or "This user has not set which headset they use."
            grip = user.grip or "This user has not specified which grip they use."
            embed.description = (
                f"**Favorite Song:** {song}\n"
                f"**Favorite Saber:** {saber}\n"
                f"**Headset:** {headset}\n"
                f"**Grip:** {grip}"
            )
            self._misc_embed: discord.Embed = embed

        self._misc_embed.color = self.ctx.bot.cc_color
        return self._misc_embed

    async def start(self, ctx: commands.Context):
        self.ctx = ctx
        await self.ctx.send(embed=self.profile_embed, view=self)


class SettingButton(discord.ui.Button['SettingView']):
    def __init__(self, setting, *, label):
        super().__init__(style=discord.ButtonStyle.blurple, label=label)
        self.setting = setting

    async def callback(self, interaction: discord.Interaction):
        func = getattr(self.view, 'set_' + self.setting, None)
        if func is not None:
            await func(interaction)
        await interaction.message.delete()


class SettingView(discord.ui.View):
    editable = ("favorite_song", "favorite_saber", "headset", "grip")

    def __init__(self, ctx: commands.Context):
        super().__init__()
        self.ctx = ctx
        for i in self.editable:
            self.add_item(SettingButton(i, label=i.replace('_', ' ').title()))
        self.add_item(StopButton())

    @staticmethod
    async def send_confirmed(interaction: discord.Interaction, message: str) -> None:
        webhook = interaction.followup
        await webhook.send(message, ephemeral=True)

    async def update(self, item, value):
        pool = self.ctx.bot.pool
        query = (
            f"""
            UPDATE
                users
            SET
                {item} = $1
            WHERE
                user_id = $2
            """
        )
        await pool.execute(query, value, self.ctx.author.id)



    async def set_favorite_song(self, interaction: discord.Interaction):
        ctx = self.ctx
        await interaction.response.send_message("Please send the BeatSaver url of your favorite song.", ephemeral=True)
        try:
            response = await ctx.bot.wait_for('message',
                                              check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
                                              timeout=60)
        except TimeoutError:
            await interaction.response.send_message("You did not respond in time.", empheral=True)
        else:
            content = response.content.lower().strip("<>")
            if not (key_match := BEATSAVER_SONG_REGEX.fullmatch(content)):
                await interaction.followup.send("Please send a BeatSaver url.", ephemeral=True)
            else:
                key = key_match['key']
                url = "https://beatsaver.com/api/maps/detail/" + key
                async with ctx.bot.session.get(url) as resp:
                    if not resp.ok:
                        return await interaction.followup.send("Something went wrong: HTTP Error code {resp.status}")
                    song_name = (await resp.json())['name']
                    song_url = "https://beatsaver.com/beatmap/" + key
                json = dumps({"name": song_name, "url": song_url})
                await self.update('favorite_song', json)
                await self.send_confirmed(interaction, f"I have set your favorite song to [`{song_name}`]({song_url})")

    async def set_headset(self, interaction: discord.Interaction):
        embed = discord.Embed(description="Please click the button that resembles which headset you prefer to use.",
                              color=self.ctx.bot.cc_color)
        await interaction.response.send_message(embed=embed, ephemeral=True, view=HeadsetView(parent=self))

    async def set_grip(self, interaction: discord.Interaction):
        ctx = self.ctx
        bot = ctx.bot
        await interaction.response.send_message("Please send the grip you prefer to use.", ephemeral=True)
        try:
            response = await bot.wait_for('message',
                                          check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
                                          timeout=30)
        except TimeoutError:
            await interaction.response.send_message("You did not respond in time.", empheral=True)
        else:
            grip = response.content

            await self.update('grip', grip)
            message = f"I have set your grip to `{grip}`"
            await self.send_confirmed(interaction, message)


class HeadsetButton(discord.ui.Button['HeadsetView']):
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
            style=style,
            label=label,
            disabled=disabled,
            custom_id=custom_id,
            emoji=emoji,
            row=row
        )

    async def callback(self, interaction: discord.Interaction):
        await self.view.parent.update('headset', self.label)
        await interaction.response.send_message(f"I set your preferred headset to `{self.label}`", ephemeral=True)


class HeadsetView(discord.ui.View):
    headsets = ('Oculus Rift CV1', 'Oculus Rift S', 'Oculus Quest', 'Oculus Quest 2', 'Valve Index', 'HTC Vive',
                'HTC Vive (Pro)', 'Other')

    def __init__(self, parent: SettingView):
        super().__init__()
        for i in self.headsets:
            self.add_item(HeadsetButton(label=i))
        self.parent = parent
