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
        embed = discord.Embed(
            description=quote,
            color=0xD75BF4
        )
        await context.send(embed)

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
                else:
                    quote = "Dunno what2say"
                embed = discord.Embed(
                    description=quote,
                    color=0xD75BF4
                )
                await session.close()
                await context.send(embed)
    @commands.hybrid_command(name="ping", description="Returns the bot's latency")
    async def ping(self, context: Context):
        await context.send(f"Pong!")

    @commands.hybrid_command(name="update_users", description="Clears the chat")
    async def update_users(self, context: Context):
        members = context.guild.members
        await db_parser.parse_users_from_guild(list(members), context.guild.id, context.guild.owner_id)
        await context.send("Updated users")

    async def randomfact(self, context: Context) -> None:
        """
        Get a random fact.

        :param context: The hybrid command context.
        """
        async with aiohttp.ClientSession() as session:
            async with session.get("https://uselessfacts.jsph.pl/random.json?language=en", ssl=False) as request:
                if request.status == 200:
                    data = await request.json()
                    embed = discord.Embed(
                        description=data["text"],
                        color=0xD75BF4
                    )
                else:
                    embed = discord.Embed(
                        title="Error!",
                        description="There is something wrong with the API, please try again later",
                        color=0xE02B2B
                    )
                await context.send(embed=embed)
                await session.close()


async def setup(bot):
    await bot.add_cog(Miscelaneous(bot))