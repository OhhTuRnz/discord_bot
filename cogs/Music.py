from discord.ext import commands
import asyncio
import sys
import datetime as dt
import random
from enum import Enum
import typing as t
import re
import aiohttp

import discord
import wavelink

LYRICS_URL = "https://some-random-api.ml/lyrics?title="
HZ_BANDS = (20, 40, 63, 100, 150, 250, 400, 450, 630, 1000, 1600, 2500, 4000, 10000, 16000)
TIME_REGEX = r"([0-9]{1,2})[:ms](([0-9]{1,2})s?)?"
URL_REGEX = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
SOUNDCLOUD_REGEX = r".*soundcloud\.com.*"
OPTIONS = {
    "1️⃣": 0,
    "2⃣": 1,
    "3⃣": 2,
    "4⃣": 3,
    "5⃣": 4,
}

class RepeatMode(Enum):
    NONE = 0
    ONE = 1
    ALL = 2
class AlreadyConnectedToChannel(commands.CommandError):
    pass

class NoVoiceChannel(commands.CommandError):
    pass

class QueueIsEmpty(commands.CommandError):
    pass

class NoTracksFound(commands.CommandError):
    pass

class PlayerIsAlreadyPaused(commands.CommandError):
    pass

class NoMoreTracks(commands.CommandError):
    pass

class NoPreviousTracks(commands.CommandError):
    pass

class InvalidRepeatMode(commands.CommandError):
    pass

class VolumeTooLow(commands.CommandError):
    pass

class VolumeTooHigh(commands.CommandError):
    pass

class MaxVolume(commands.CommandError):
    pass

class MinVolume(commands.CommandError):
    pass

class NoLyricsFound(commands.CommandError):
    pass

class InvalidEQPreset(commands.CommandError):
    pass

class NonExistentEQBand(commands.CommandError):
    pass

class EQGainOutOfBounds(commands.CommandError):
    pass

class InvalidTimeString(commands.CommandError):
    pass

class music_utils():

    def __init__(self):
        pass
    async def get_tracks(search) -> list:
        search = search.strip("<>")
        if not re.match(URL_REGEX, search):
            search = f"ytsearch:{search}"
        if(re.match(SOUNDCLOUD_REGEX, search)):
            return await wavelink.SoundCloudTrack.search(search)
        else:
            return await wavelink.YouTubeTrack.search(search)

class Player(wavelink.Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.autoplay = True

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    async def on_player_stop(self, ctx: commands.Context, payload: wavelink.TrackEventPayload):
        await self.next_command(ctx)

    async def on_wavelink_track_start(self, payload: wavelink.TrackEventPayload):
        embed = discord.Embed(
            title="Now playing",
            description=f"[{payload.player.queue.current.title}]({payload.player.queue.current.uri}) [{payload.player.queue.current.author}]",
            colour=discord.Colour.blurple(),
            timestamp=dt.datetime.utcnow()
        )
        embed.set_author(name="Playback Information")
        embed.set_footer(text=f"Requested by {payload.player.queue.current.requester.display_name}", icon_url=payload.player.queue.current.requester.avatar_url)
        await payload.player.queue.current.channel.send(embed=embed)


    async def cog_check(self, ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.send("Music commands are not available in DMs.")
            return False

        return True

    @commands.hybrid_command(name="connect",
                             description="connects to voicechannel")
    async def connect_command(self, ctx, *, channel: t.Optional[discord.VoiceChannel]):
        vc: Player = await ctx.author.voice.channel.connect(cls=Player)
        channel = await vc.connect(ctx, channel)
        await ctx.send(f"Connected to {channel.name}.")

    @connect_command.error
    async def connect_command_error(self, ctx, exc):
        if isinstance(exc, AlreadyConnectedToChannel):
            await ctx.send("Already connected to a voice channel.")
        elif isinstance(exc, NoVoiceChannel):
            await ctx.send("No suitable voice channel was provided.")

    @commands.hybrid_command(name="disconnect",
                             description="Disconnect from channel")
    async def disconnect_command(self, ctx):
        vc: wavelink.player = ctx.voice_client
        await vc.disconnect()
        await ctx.send("Disconnected.")

    @commands.hybrid_command(name="play", description="plays music")
    async def play(self, ctx: commands.Context, *, search: str) -> None:
        """Simple play command."""
        if not ctx.author.voice.channel:
            raise NoVoiceChannel
        if not ctx.voice_client:
            vc: Player = await ctx.author.voice.channel.connect(cls=Player)
        else:
            vc: Player = ctx.voice_client

        if search is None:
            if vc.queue.is_empty:
                raise QueueIsEmpty

            await vc.resume()
            await ctx.send("Playback resumed.")

        tracks = await music_utils.get_tracks(search)
        track = tracks[0]
        if not track:
            await ctx.send(f'No tracks found with query: `{search}`')
            return
        await vc.queue.put_wait(track)
        if not vc.is_playing():
            await vc.play(vc.queue.get(), populate = True)
            await ctx.send(f"Playing: {track.title}")
        else:
            await ctx.send(f"Added {track.title} to the queue. There are {vc.queue.count} songs in the queue.")
    @play.error
    async def play_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            await ctx.send("No songs to play as the queue is empty.")
        elif isinstance(exc, NoVoiceChannel):
            await ctx.send("You are not in a voice channel!.")

    @commands.hybrid_command(name="pause")
    async def pause_command(self, ctx):
        if not ctx.author.voice.channel:
            raise NoVoiceChannel
        if not ctx.voice_client:
            vc: Player = await ctx.author.voice.channel.connect(cls=Player)
        else:
            vc: Player = ctx.voice_client

        if not vc.is_paused():
            await vc.pause()
            await ctx.send("Playback paused.")
        else:
            raise PlayerIsAlreadyPaused

    @pause_command.error
    async def pause_command_error(self, ctx, exc):
        if isinstance(exc, PlayerIsAlreadyPaused):
            await ctx.send("Already paused.")
        if isinstance(exc, NoVoiceChannel):
            await ctx.send("You are not in a voice channel!.")

    @commands.hybrid_command(name="next", aliases=["skip"])
    async def next_command(self, ctx):
        vc: wavelink.player = ctx.voice_client

        await vc.stop()
        await vc.play(vc.queue.get(), populate = True)
        await ctx.send("Playing next track in queue.")

    @next_command.error
    async def next_command_error(self, ctx, exc):
        if isinstance(exc, wavelink.QueueEmpty):
            await ctx.send("There are no tracks in the queue.")

    @commands.hybrid_command(name="previous")
    async def previous_command(self, ctx):
        if not ctx.author.voice.channel:
            raise NoVoiceChannel
        if not ctx.voice_client:
            vc: Player = await ctx.author.voice.channel.connect(cls=Player)
        else:
            vc: Player = ctx.voice_client

        if not vc.queue.history:
            raise NoPreviousTracks

        await vc.stop()
        await vc.play(vc.queue[vc.queue.find_position(vc.queue.get()) - 1], populate = True)
        await ctx.send("Playing previous track in queue.")

    @previous_command.error
    async def previous_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            await ctx.send("This could not be executed as the queue is currently empty.")
        elif isinstance(exc, NoPreviousTracks):
            await ctx.send("There are no previous tracks in the queue.")
        elif isinstance(exc, NoVoiceChannel):
            await ctx.send("You are not in a voice channel!.")

    @commands.command(name="shuffle")
    async def shuffle_command(self, ctx):
        vc: wavelink.player = ctx.voice_client
        vc.queue.shuffle()
        await ctx.send("Queue shuffled.")

    @shuffle_command.error
    async def shuffle_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            await ctx.send("The queue could not be shuffled as it is currently empty.")

    @commands.command(name="repeat")
    async def repeat_command(self, ctx, mode: str):
        if mode not in ("none", "1", "all"):
            raise InvalidRepeatMode

        player = self.get_player(ctx)
        player.queue.set_repeat_mode(mode)
        await ctx.send(f"The repeat mode has been set to {mode}.")

    @commands.command(name="queue")
    async def queue_command(self, ctx, show: t.Optional[int] = 10):
        player = self.get_player(ctx)

        if player.queue.is_empty:
            raise QueueIsEmpty

        embed = discord.Embed(
            title="Queue",
            description=f"Showing up to next {show} tracks",
            colour=ctx.author.colour,
            timestamp=dt.datetime.utcnow()
        )
        embed.set_author(name="Query Results")
        embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
        embed.add_field(
            name="Currently playing",
            value=getattr(player.queue.get(), "title", "No tracks currently playing."),
            inline=False
        )
        if upcoming := player.queue.upcoming:
            embed.add_field(
                name="Next up",
                value="\n".join(t.title for t in upcoming[:show]),
                inline=False
            )

        msg = await ctx.send(embed=embed)

    @queue_command.error
    async def queue_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            await ctx.send("The queue is currently empty.")

    # Requests -----------------------------------------------------------------

    @commands.group(name="volume", invoke_without_command=True)
    async def volume_group(self, ctx, volume: int):
        player = self.get_player(ctx)

        if volume < 0:
            raise VolumeTooLow

        if volume > 150:
            raise VolumeTooHigh

        await player.set_volume(volume)
        await ctx.send(f"Volume set to {volume:,}%")

    @volume_group.error
    async def volume_group_error(self, ctx, exc):
        if isinstance(exc, VolumeTooLow):
            await ctx.send("The volume must be 0% or above.")
        elif isinstance(exc, VolumeTooHigh):
            await ctx.send("The volume must be 150% or below.")

    @volume_group.command(name="up")
    async def volume_up_command(self, ctx):
        player = self.get_player(ctx)

        if player.volume == 150:
            raise MaxVolume

        await player.set_volume(value := min(player.volume + 10, 150))
        await ctx.send(f"Volume set to {value:,}%")

    @volume_up_command.error
    async def volume_up_command_error(self, ctx, exc):
        if isinstance(exc, MaxVolume):
            await ctx.send("The player is already at max volume.")

    @volume_group.command(name="down")
    async def volume_down_command(self, ctx):
        player = self.get_player(ctx)

        if player.volume == 0:
            raise MinVolume

        await player.set_volume(value := max(0, player.volume - 10))
        await ctx.send(f"Volume set to {value:,}%")

    @volume_down_command.error
    async def volume_down_command_error(self, ctx, exc):
        if isinstance(exc, MinVolume):
            await ctx.send("The player is already at min volume.")

    @commands.command(name="lyrics")
    async def lyrics_command(self, ctx, name: t.Optional[str]):
        player = self.get_player(ctx)
        name = name or player.queue.get().title

        async with ctx.typing():
            async with aiohttp.request("GET", LYRICS_URL + name, headers={}) as r:
                if not 200 <= r.status <= 299:
                    raise NoLyricsFound

                data = await r.json()

                if len(data["lyrics"]) > 2000:
                    return await ctx.send(f"<{data['links']['genius']}>")

                embed = discord.Embed(
                    title=data["title"],
                    description=data["lyrics"],
                    colour=ctx.author.colour,
                    timestamp=dt.datetime.utcnow(),
                )
                embed.set_thumbnail(url=data["thumbnail"]["genius"])
                embed.set_author(name=data["author"])
                await ctx.send(embed=embed)

    @lyrics_command.error
    async def lyrics_command_error(self, ctx, exc):
        if isinstance(exc, NoLyricsFound):
            await ctx.send("No lyrics could be found.")

"""
    @commands.command(name="eq")
    async def eq_command(self, ctx, preset: str):
        player = self.get_player(ctx)

        eq = getattr(wavelink.eqs.Equalizer, preset, None)
        if not eq:
            raise InvalidEQPreset

        await player.set_eq(eq())
        await ctx.send(f"Equaliser adjusted to the {preset} preset.")

    @eq_command.error
    async def eq_command_error(self, ctx, exc):
        if isinstance(exc, InvalidEQPreset):
            await ctx.send("The EQ preset must be either 'flat', 'boost', 'metal', or 'piano'.")

    @commands.command(name="adveq", aliases=["aeq"])
    async def adveq_command(self, ctx, band: int, gain: float):
        player = self.get_player(ctx)

        if not 1 <= band <= 15 and band not in HZ_BANDS:
            raise NonExistentEQBand

        if band > 15:
            band = HZ_BANDS.index(band) + 1

        if abs(gain) > 10:
            raise EQGainOutOfBounds

        player.eq_levels[band - 1] = gain / 10
        eq = wavelink.eqs.Equalizer(levels=[(i, gain) for i, gain in enumerate(player.eq_levels)])
        await player.set_eq(eq)
        await ctx.send("Equaliser adjusted.")

    @adveq_command.error
    async def adveq_command_error(self, ctx, exc):
        if isinstance(exc, NonExistentEQBand):
            await ctx.send(
                "This is a 15 band equaliser -- the band number should be between 1 and 15, or one of the following "
                "frequencies: " + ", ".join(str(b) for b in HZ_BANDS)
            )
        elif isinstance(exc, EQGainOutOfBounds):
            await ctx.send("The EQ gain for any band should be between 10 dB and -10 dB.")

    @commands.command(name="playing", aliases=["np"])
    async def playing_command(self, ctx):
        player = self.get_player(ctx)

        if not player.is_playing:
            raise PlayerIsAlreadyPaused

        embed = discord.Embed(
            title="Now playing",
            colour=ctx.author.colour,
            timestamp=dt.datetime.utcnow(),
        )
        embed.set_author(name="Playback Information")
        embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
        embed.add_field(name="Track title", value=player.queue.get().title, inline=False)
        embed.add_field(name="Artist", value=player.queue.get().author, inline=False)

        position = divmod(player.position, 60000)
        length = divmod(player.queue.get().length, 60000)
        embed.add_field(
            name="Position",
            value=f"{int(position[0])}:{round(position[1] / 1000):02}/{int(length[0])}:{round(length[1] / 1000):02}",
            inline=False
        )

        await ctx.send(embed=embed)

    @playing_command.error
    async def playing_command_error(self, ctx, exc):
        if isinstance(exc, PlayerIsAlreadyPaused):
            await ctx.send("There is no track currently playing.")

    @commands.command(name="skipto", aliases=["playindex"])
    async def skipto_command(self, ctx, index: int):
        player = self.get_player(ctx)

        if player.queue.is_empty:
            raise QueueIsEmpty

        if not 0 <= index <= player.queue.length:
            raise NoMoreTracks

        player.queue.position = index - 2
        await player.stop()
        await ctx.send(f"Playing track in position {index}.")

    @skipto_command.error
    async def skipto_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            await ctx.send("There are no tracks in the queue.")
        elif isinstance(exc, NoMoreTracks):
            await ctx.send("That index is out of the bounds of the queue.")

    @commands.command(name="restart")
    async def restart_command(self, ctx):
        player = self.get_player(ctx)

        if player.queue.is_empty:
            raise QueueIsEmpty

        await player.seek(0)
        await ctx.send("Track restarted.")

    @restart_command.error
    async def restart_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            await ctx.send("There are no tracks in the queue.")

    @commands.command(name="seek")
    async def seek_command(self, ctx, position: str):
        player = self.get_player(ctx)

        if player.queue.is_empty:
            raise QueueIsEmpty

        if not (match := re.match(TIME_REGEX, position)):
            raise InvalidTimeString

        if match.group(3):
            secs = (int(match.group(1)) * 60) + (int(match.group(3)))
        else:
            secs = int(match.group(1))

        await player.seek(secs * 1000)
        await ctx.send("Seeked.")
"""

async def setup(bot):
    await bot.add_cog(Music(bot))