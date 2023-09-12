import os
import requests
import json
import aiohttp
import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context
import random

from aider import db_parser

class Miscelaneous(commands.Cog, name = "Misc"):
    @commands.hybrid_command(
        name="myrandomquote",
        description="The bot prints a random quote from his"
    )
    async def get_my_quotes(self, context: Context):
        data = random.choice(json.load(open('resources/Spanish_Quotes.json', 'r', encoding='UTF-8')))
        unk = "unknown"
        quote = f"{data['quote']} - {unk if data['from'] == '' else data['from']}"
        await context.send(quote)

    @commands.hybrid_command(
        name="internetquote",
        description="The bot prints a random quote from the internet"
    )
    async def get_internet_quotes(self, context: Context):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://zenquotes.io/api/random", ssl=False) as request:
                if request.status == 200:
                    data = await request.json()
                    quote = f"{data[0]['q']} -{data[0]['a']}"
                    print(quote)
                else:
                    quote = "Dunno what2say"
                await session.close()
                await context.send(quote)
    @commands.hybrid_command(name="ping", description="Returns the bot's latency")
    async def ping(self, context: Context):
        await context.send(f"Pong!")

    @commands.hybrid_command(name="update_users", description="Clears the chat")
    async def update_users(self, context: Context):
        members = context.guild.members
        await db_parser.parse_users_from_guild(list(members), context.guild.id, context.guild.owner_id)
        await context.send("Updated users")


async def setup(bot):
    await bot.add_cog(Miscelaneous(bot))