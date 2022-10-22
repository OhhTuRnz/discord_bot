import random
import pygame

import aiohttp
import discord
from discord.ext import commands
from discord.ext.commands import Context

class Games(commands.Cog):
    pass

async def setup(bot):
    await bot.add_cog(Games(bot))