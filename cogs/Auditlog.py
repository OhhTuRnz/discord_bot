import random

import aiohttp
import discord
from discord.ext import commands
from discord.ext.commands import Context

class AuditLog(commands.Cog, name = "AuditLog"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="check_last_audit_logs",
        description="The bot shows the last 10 logs from the audit log"
    )
    async def get_my_quotes(self, context: Context):
        data = random.choice(json.load(open('resources/Spanish_Quotes.json', 'r', encoding='UTF-8')))
        unk = "unknown"
        quote = f"{data['quote']} - {unk if data['from'] == '' else data['from']}"
        await context.send(quote)

async def setup(bot):
    await bot.add_cog(AuditLog(bot))