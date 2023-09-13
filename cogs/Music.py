from discord.ext import commands

import sys
sys.path.append("..")

import wavelink

class Music(commands.Cog, name="Music"):

    def __init__(self, bot):
        self.bot = bot
    @commands.hybrid_command(
        name="play",
        description="Play a song from youtube"
    )
    async def play(self, context: commands.Context, *, search: str) -> None:
        """Simple play command."""

        if not context.voice_client:
            vc: wavelink.Player = await context.author.voice.channel.connect(cls=wavelink.Player)
        else:
            vc: wavelink.Player = context.voice_client

        tracks = await wavelink.YouTubeTrack.search(search)
        if not tracks:
            await context.send(f'No tracks found with query: `{search}`')
            return

        track = tracks[0]
        await vc.play(track)

    @commands.hybrid_command(
        name="quit",
        description="Disconnects bot"
    )
    async def disconnect(self, context: commands.Context) -> None:
        """Simple disconnect command.

        This command assumes there is a currently connected Player.
        """
        vc: wavelink.Player = context.voice_client
        await vc.disconnect()

async def setup(bot):
    await bot.add_cog(Music(bot))