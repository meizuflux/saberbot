import discord
from discord.ext import menus


class LeaderboardSource(menus.ListPageSource):
    async def format_page(self, menu, page):
        embed = discord.Embed(title="Scoresaber Top 50", color=discord.Color.blurple())
        for user in page:
            name = user['playerName']
            player_id = user['playerId']
            change = user['difference']
            if not str(change).startswith("-"):
                change = "+" + str(change)
            desc = (
                f"[{player_id}](https://new.scoresaber.com/u/{player_id} \"{name}'s profile\")",
                f"PP: {user['pp']}",
                f"Change: {change}"
            )
            embed.add_field(name=f"**{user['rank']}.** {name}", value="\n".join(desc), inline=False)
        if self.is_paginating():
            fmt = f"Page {menu.current_page + 1}/{self.get_max_pages()}"
            embed.set_footer(text=fmt)

        return embed
