import discord
from discord.ext import commands

class Reddit(commands.Cog):
    pass

async def setup(bot):
    await bot.add_cog(Reddit(bot))