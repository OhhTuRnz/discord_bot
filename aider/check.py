import db_parser
import json

from typing import Callable, TypeVar

from discord.ext import commands

from exceptions import UserBlacklisted
T = TypeVar("T")

def not_blacklisted() -> Callable[[T], T]:
    """
    This is a custom check to see if the user executing the command is blacklisted.
    """
    async def predicate(context: commands.Context) -> bool:
        if await db_parser.is_blacklisted(context.author.id, context.guild.id):
            raise UserBlacklisted
        return True

    return commands.check(predicate)
