import random

import aiohttp
import discord
from discord.ext import commands
from discord.ext.commands import Context

class AuditLog(commands.Cog, name = "AuditLog"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="get_last_auditlogs",
        description="The bot shows the last 10 logs from the audit log"
    )
    async def get_last_auditlogs(self, context: Context):
        logs = []
        async for log in context.guild.audit_logs(limit=5):
            logs.append(log)
        embed = discord.Embed(
            description="Last logs from the audit log",
            color=0xD75BF4
        )
        embed.add_field(name="Log:", value="\n".join(self.parse_log(log) for log in logs))
        await context.send(embed=embed)

    def parse_log(self, log):
        if(str(log.action).__contains__("kick") or str(log.action).__contains__("ban")
                or str(log.action).__contains__("move") or str(log.action).__contains__("disconnect")):
            msg = f"<@{log.user.id}> did {log.action} to <@{log.target.id}>"
        else:
            msg = f"<@{log.user.id}> did {log.action}"
        return msg

    @commands.hybrid_command(
        name="get_last_kicks",
        description="The bot shows the last 10 kicks from the audit log"
    )
    async def get_last_kicks(self, context: Context):
        logs = []
        async for log in context.guild.audit_logs(limit=5, action=discord.AuditLogAction.kick):
            logs.append(log)
        embed = discord.Embed(
            description="Last kicks from the audit log",
            color=0xD75BF4
        )
        embed.add_field(name="Kicks:", value="\n".join(f"<@{log.user.id}> kicked <@{log.target.id}>" for log in logs))
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="get_last_bans",
        description="The bot shows the last 10 bans from the audit log"
    )
    async def get_last_bans(self, context: Context):
        logs = []
        async for log in context.guild.audit_logs(limit=5, action=discord.AuditLogAction.ban):
            logs.append(log)
        embed = discord.Embed(
            description="Last bans from the audit log",
            color=0xD75BF4
        )
        embed.add_field(name="Logs:", value="\n".join(f"<@{log.user.id}> banned <@{log.target.id}>" for log in logs))
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="get_last_disconnect",
        description="The bot shows the last 10 disconnections from the audit log"
    )
    async def get_last_disconnect(self, context: Context):
        logs = []
        async for log in context.guild.audit_logs(limit=5, action=discord.AuditLogAction.member_disconnect):
            logs.append(log)
        embed = discord.Embed(
            description="Last disconnections from the audit log",
            color=0xD75BF4
        )
        embed.add_field(name="Discconects:", value="\n".join(f"<@{log.user.id}> disconnected <@{log.target.id}>" for log in logs))
        await context.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AuditLog(bot))