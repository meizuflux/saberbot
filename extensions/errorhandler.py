import traceback
from contextlib import suppress

import discord
from discord.ext import commands

from bot import Bot


class Handler(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @staticmethod
    async def handle_command_error(ctx: commands.Context, error: commands.CommandError):
        owner_reinvoke = (
            commands.MissingAnyRole,
            commands.MissingPermissions,
            commands.MissingRole,
            commands.CommandOnCooldown,
            commands.DisabledCommand,
        )
        if isinstance(error, owner_reinvoke):
            await ctx.reinvoke()
            return

        command = None

        if ctx.command:
            if ctx.command.has_error_handler():
                return

            cog: commands.Cog = ctx.cog
            if cog and cog.has_error_handler():
                return

            command = ctx.command.qualified_name

        error = getattr(error, "original", error)

        if isinstance(error, commands.CheckFailure):
            return await ctx.send(str(error))

        if isinstance(error, commands.NoPrivateMessage):
            with suppress(discord.HTTPException):
                await ctx.author.send(f"{command} can only be used within a server.")

        if isinstance(error, commands.MissingRequiredArgument):
            errors = str(error).split(" ", maxsplit=1)
            msg = (
                f"`{errors[0]}` {errors[1]}\n"
                f"You can view the help for this command with `{ctx.prefix}help` `{command}`"
            )
            return await ctx.send(msg)

        if isinstance(error, commands.DisabledCommand):
            return await ctx.send(f"`{command}` has been disabled.")

        if isinstance(error, commands.BadArgument):
            return await ctx.send(str(error))

    async def handle_library_error(self, ctx: commands.Context, error: discord.DiscordException):
        if isinstance(error, commands.CommandError):
            await self.handle_command_error(ctx, error)
        else:
            formatted = traceback.format_exception(type(error), error, error.__traceback__)
            print("".join(formatted))

            await ctx.send(
                f"Oops, an error occurred. Sorry about that." f"```py\n{''.join(formatted)}\n```"
            )

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: Exception):
        error = getattr(error, "original", error)
        if isinstance(error, discord.DiscordException):
            await self.handle_library_error(ctx, error)
        else:
            if ctx.command:
                if ctx.command.has_error_handler():
                    return

                cog: commands.Cog = ctx.cog
                if cog and cog.has_error_handler():
                    return

            formatted = traceback.format_exception(type(error), error, error.__traceback__)
            print("".join(formatted))

            await ctx.send(
                f"Oops, an error occurred. Sorry about that." f"```py\n{''.join(formatted)}\n```"
            )


def setup(bot):
    bot.add_cog(Handler(bot))
