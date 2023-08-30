import os
import requests
import json
import aiohttp
import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context
import random

class Miscelaneous(commands.Cog, name = "Misc"):
    @commands.hybrid_command(
        name="myrandomquote",
        description="The bot prints a random quote from his"
    )
    async def get_my_quotes(self, context: Context):
        data = random.choice(json.load(open('../resources/Spanish_Quotes.json', 'r', encoding='UTF-8')))
        unk = "unknown"
        quote = f"{data['quote']} - {unk if data['from'] == '' else data['from']}"
        await context.send(quote)

    @commands.hybrid_command(
        name="internetquote",
        description="The bot prints a random quote from the internet"
    )
    async def get_internet_quotes(self, context: Context):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://zenquotes.io/api/random") as request:
                if request.status == 200:
                    data = await request.json()
                    quote = f"{data[0]['q']} -{data[0]['a']}"
                    print(quote)
                else:
                    quote = "Dunno what2say"
                await context.send(quote)


async def setup(bot):
    await bot.add_cog(Miscelaneous(bot))