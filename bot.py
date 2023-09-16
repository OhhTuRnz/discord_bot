import asyncio
import json
import os
import platform
import random
import sqlite3
import sys
from contextlib import closing
import discord

from discord.ext.commands import Bot, Context

import aiosqlite

import exceptions
import keep_alive

import wavelink

from aider import db_parser as db

if not os.path.isfile("config.json"):
    sys.exit("Can't find the config.json, aborting...")
else:
    with open("config.json") as file:
        config = json.load(file)
class MyBot(Bot):
    def __init__(self):
        intents = discord.Intents.all()
        intents.message_content = True
        intents.members = True
        application_id = config['application_id']
        super().__init__(command_prefix = config['prefix'], intents = intents, application_id = application_id)
    async def setup_hook(self):
        await self.tree.sync()
        node: wavelink.Node = wavelink.Node(uri='http://127.0.0.1:2333', password='youshallnotpass')
        await wavelink.NodePool.connect(client=self, nodes=[node])
bot = MyBot()

#bot.config = config

# Just in case you want to load an schema into the database
#async def init_db():
#    async with aiosqlite.connect("database/database.db") as db:
#        with open("database/schema.sql") as file:
#            await db.executescript(file.read())
#        await db.commit()
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    print(f"discord API version: {discord.__version__}")
    print("Enjoy your bot!")

@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user or message.author.bot:
        return
    await bot.process_commands(message)

@bot.event
async def on_member_join(member):
    await db.parse_users_from_guild({member : member.role}, member.guild.id, member.guild.owner_id)
    await member.guild.system_channel.send(f"Tonto tontisimo que eres vete a la mierda <@{str(member.id)}>")

async def on_member_leave(member):
    await db.delete_user(member.id, member.guild.id)

async def on_guild_join(guild):
    # This function will be called when the bot joins a new guild
    embed = discord.Embed(
        description=f""""
    🐒 Hello buddies a pleasure to be in {guild.name}! 🐒

           __  __ ___  ____  ____  _  _ 
          (  \/  ) __)(  _ \(  _ \/ )( \
           )    ( \__ \ ) __/ ) __/) __ (
          (_/\/\_)(___/(__)  (__)  (__)__)
          
    You can find me on:
    GitHub: {config['github']}
    LinkedIn: {config['linkedin']}
    
    Feel free to reach out if you have any questions or need assistance!
    """,
        color=0x751C72
    )
    embed.set_image(url="https://assets.stickpng.com/images/5845cd430b2a3b54fdbaecf8.png")
    await guild.system_channel.send(embed=embed)
    await db.parse_users_from_guild(guild.members, guild.id, guild.owner_id)

async def load_cogs():
  for file in os.listdir(f"./cogs"):
    if file.endswith(".py") and not file.startswith("_"):
      extension = file[:-3]
      try:
        await bot.load_extension(f"cogs.{extension}")
        print(f"Loaded extension '{extension}'")
      except Exception as e:
        exception = f"{type(e).__name__}: {e}"
        print(f"Failed to load extension {extension}\n{exception}")
try:
    asyncio.run(load_cogs())
    bot.run(config['token'])
except Exception as e:
    print(f"//!\\\\ Error loading the bot. Is your token valid? {type(e).__name__} : {e}")

"""
async def on_wavelink_node_ready(node:wavelink.Node):
    print(f"Wavelink node '{node.identifier}' ready.")
"""

