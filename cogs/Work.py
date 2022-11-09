import random

import aiohttp
import discord
from discord.ext import commands
from discord.ext.commands import Context

class Status(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(label="Work", style=discord.ButtonStyle.blurple)
    async def work(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = "Working"
        self.stop()

    @discord.ui.button(label="NoWork", style=discord.ButtonStyle.blurple)
    async def nowork(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = "Out of work"
        self.stop()

class Work(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="work_status",
        description="Update your work status"
    )
    async def workStatus(self, context: Context) -> None:
        buttons = Status()
        embed = discord.Embed(
            description= "What are you gonna do?",
            color= 0x751C72
        )
        message = await context.send(embed=embed, view=buttons)
        await buttons.wait()
        validRole = None
        for role in message.channel.guild.roles:
            if role.name.lower().__contains__("work"):
                validRole = role
                break
        if validRole != None:
            if buttons.value == "Working":
                try:
                    await context.author.add_roles(validRole, reason="Dis bot is badass")
                    embed = discord.Embed(
                        description= "Welcome to the gulag, my brudda",
                        color= 0x751C72
                    )
                    embed.set_image(url="https://panampost.com/wp-content/uploads/gulag.jpeg")
                except:
                    embed = discord.Embed(
                        description="Sorry, something went wrong",
                        color=0xFF0000
                    )
            else:
                try:
                    await context.author.remove_roles(validRole, reason= "Dis bot is badass")
                    embed = discord.Embed(
                        description= "Comrade down, we'll be watching you",
                        color= 0x751C72
                    )
                    embed.set_image(url="https://study.com/cimages/videopreview/videopreview-full/edixjf9183.jpg")
                except:
                    embed = discord.Embed(
                        description="Sorry, something went wrong",
                        color=0xFF0000
                    )
            await message.edit(embed=embed, view= None, content= None)
        else:
            await message.edit("Please, add a role that has the word 'work' in it")


async def setup(bot):
    await bot.add_cog(Work(bot))