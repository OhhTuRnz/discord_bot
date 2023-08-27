import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context

class Moderation(commands.Cog, name = "Moderation"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name = "kick",
                             description = "Make this dood kick da shit outa em")
    @commands.has_permissions(kick_members = True)
    @app_commands.describe(user= "Who you want to kick", reason= "Why the user should be kicked")
    async def kick(self, context: Context, user : discord.User, *, reason: str = "Non determined") -> None:
        member = await context.guild.fetch_member(user.id)
        if context.message.author.guild_permissions.kick_members:
            try:
                if member.guild_permissions.administrator:
                    embed = discord.Embed(
                        description= "You played with the wrong guy",
                        color= 0xFCFC07
                    )
                else:
                    embed = discord.Embed(
                        title="Toot toot mothafucka",
                        description= f"<@{context.author.id}> has kicked <@{member.id}>",
                        color= 0xFCFC07
                    )
                    embed.add_field(
                        name= "reason:",
                        value= reason
                    )
                    await member.kick(reason= reason)
                    await member.send(f"Bro did u know this boi {context.author} has kicked u? Just sayin' that he told me it was cuz this reason: {reason}")
            except Exception:
                await context.send("There was an unexpected error")
        else:
            embed = discord.Embed(
                description="Bro u a random",
                color=0xFCFC07
            )
        await context.send(embed= embed)

    @commands.hybrid_command(name="rename",
                             description="Set servers nickname for a user")
    @commands.has_permissions(manage_nicknames=True)
    @app_commands.describe(user="Who do you want to rename", nick="New nick")
    async def nickname(self, context: Context, user: discord.User, *, nick : str):
        member = await context.guild.fetch_member(user.id)
        if context.message.author.guild_permissions.manage_nicknames:
            try:
                await member.edit(nick = nick)
                embed = discord.Embed(
                    title="Succesfully changed user's nickname",
                    description=f"Say hi <@{member.id}>",
                    color=0xFCFC07
                )
            except Exception:
                await context.send("There was an unexpected error")
        else:
            embed = discord.Embed(
                description="Bro u a random",
                color=0xFCFC07
            )
        await context.send(embed=embed)

    @commands.hybrid_command(name="blacklist",
                             description="Blacklists a user from this bot")
    @commands.has_permissions(administrator = True)
    @app_commands.describe(user="Who do you want to blacklist", reason= "The reason for it")
    async def blacklist(self, context: Context, user: discord.User, *, reason: str):
        pass
async def setup(bot):
    await bot.add_cog(Moderation(bot))