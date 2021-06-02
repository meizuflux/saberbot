from collections import defaultdict

import discord
from discord.ext import menus


class LeaderboardSource(menus.ListPageSource):
    async def format_page(self, menu, page):
        embed = discord.Embed(title="Scoresaber Top 50", color=menu.ctx.bot.scoresaber_color)
        for user in page:
            name = user["playerName"]
            player_id = user["playerId"]
            change = user["difference"]
            if not str(change).startswith("-"):
                change = "+" + str(change)
            desc = (
                f'[{player_id}](https://new.scoresaber.com/u/{player_id} "{name}\'s profile")',
                f"PP: {user['pp']}",
                f"Change: {change}",
            )
            embed.add_field(name=f"**{user['rank']}.** {name}", value="\n".join(desc), inline=False)
        if self.is_paginating():
            fmt = f"Page {menu.current_page + 1}/{self.get_max_pages()}"
            embed.set_footer(text=fmt)

        return embed


class LeaderboardPages(menus.Menu):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache = defaultdict(list)
        self.total_scoresaber_pages = None
        self.current_page = 0
        self.current_ss_page = 0

    def is_cached(self, page):
        return page in self.cache

    async def cache_page(self, page_num: int):
        print("Caching Page: ", page_num)
        bot = self.ctx.bot
        url = "https://new.scoresaber.com/api/players/" + str(page_num)
        self.current_ss_page = page_num
        async with bot.session.get(url) as resp:
            data = await resp.json()
        players = data["players"]
        index = 0
        page = page_num * 10 - 9
        for i in players:
            self.cache[page].append(i)
            index += 1
            if index == 5:
                index = 0
                page += 1

    async def get_max_pages(self):
        if not self.total_scoresaber_pages:
            async with self.ctx.bot.session.get(
                "https://new.scoresaber.com/api/players/pages"
            ) as pages:
                self.total_scoresaber_pages = (await pages.json())["pages"]
        return self.total_scoresaber_pages

    async def format_page(self, players):
        embed = discord.Embed(title="Scoresaber Top 50", color=self.ctx.bot.scoresaber_color)
        for user in players:
            name = user["playerName"]
            player_id = user["playerId"]
            change = user["difference"]
            if not str(change).startswith("-"):
                change = "+" + str(change)
            desc = (
                f'[{player_id}](https://new.scoresaber.com/u/{player_id} "{name}\'s profile")',
                f"PP: {user['pp']}",
                f"Change: {change}",
            )
            embed.add_field(name=f"**{user['rank']}.** {name}", value="\n".join(desc), inline=False)

        return embed

    async def send_initial_message(self, ctx, channel):
        return await self.show_page(1)

    async def show_page(self, page_num, down=False):
        if page_num == 0:
            return
        if not self.is_cached(page_num):
            if down is True:
                await self.cache_page(self.current_ss_page - 1)
            else:
                await self.cache_page(self.current_ss_page + 1)
        self.current_page = page_num
        embed = await self.format_page(self.cache[page_num])
        if self.message is None:
            return await self.ctx.send(embed=embed)
        else:
            return await self.message.edit(content=None, embed=embed)

    @menus.button(
        "\N{BLACK LEFT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}\ufe0f", position=menus.First()
    )
    async def go_to_first_page(self, payload):
        """go to the first page"""
        await self.show_page(1)

    @menus.button("\N{BLACK LEFT-POINTING TRIANGLE}\ufe0f", position=menus.First(1))
    async def go_to_previous_page(self, payload):
        """go to the previous page"""
        await self.show_page(self.current_page - 1, down=True)

    @menus.button("\N{BLACK RIGHT-POINTING TRIANGLE}\ufe0f", position=menus.Last())
    async def go_to_next_page(self, payload):
        """go to the next page"""
        await self.show_page(self.current_page + 1)

    @menus.button("\N{BLACK SQUARE FOR STOP}\ufe0f", position=menus.Last(2))
    async def stop_pages(self, payload):
        """stops the pagination session."""
        self.stop()

    @menus.button(
        "\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}\ufe0f", position=menus.Last(1)
    )
    async def go_to_last_page(self, payload):
        """go to the last page"""
        max_pages = await self.get_max_pages() - 1
        await self.cache_page(max_pages)
        self.current_ss_page = max_pages

        to_show = self.current_ss_page * 10
        await self.show_page(to_show)


class SongLeaderboardSource(menus.ListPageSource):
    def __init__(self, embed: discord.Embed, entries, *, per_page):
        super().__init__(entries, per_page=per_page)
        self.embed = embed
        self.headsets = {
            "1": "Oculus CV1",
            "2": "HTC Vive",
            "16": "Oculus Rift S",
            "32": "Oculus Quest",
            "64": "Valve Index",
        }

    async def format_page(self, menu: menus.Menu, page):
        self.embed.clear_fields()
        if menu.current_page != 0:
            self.embed.description = ""
        if self.is_paginating():
            fmt = f"Page {menu.current_page + 1}/{self.get_max_pages()}"
            self.embed.set_footer(text=fmt)
        for score in page:
            title = f"**{score['rank']}.** {score['name']}"
            msg = (
                f"**ID:** [{score['playerId']}](https://new.scoresaber.com/u/{score['playerId']})\n"
            )
            if score["pp"] != "0":
                msg += "**PP:** " + score["pp"] + "\n"
            msg += (
                f"**Score:** {int(score['score']):,d}\n"
                f"**HMD:** {self.headsets.get(score['hmd'], 'Unknown')}"
            )
            if (misses := int(score["badCuts"]) + int(score["missedNotes"])) != 0:
                msg += f"\n**Misses:** {misses}\n"
            self.embed.add_field(name=title, value=msg, inline=False)

        return self.embed
