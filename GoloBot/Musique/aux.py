from GoloBot.Auxilliaire import GBEmbed
from GoloBot.Auxilliaire.settings import *
from GoloBot.Musique.songs import *
import re
import asyncio
from enum import Enum
import aiohttp

"""
Adapté de https://github.com/Raptor123471/DingoLingo
"""

url_regex = re.compile("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
session = aiohttp.ClientSession(
    headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'})


class Sites(Enum):
    YouTube = "YouTube"
    Twitter = "Twitter"
    SoundCloud = "SoundCloud"
    Bandcamp = "Bandcamp"
    Custom = "Custom"
    Unknown = "Unknown"


class PlaylistTypes(Enum):
    YouTube_Playlist = "YouTube Playlist"
    BandCamp_Playlist = "BandCamp Playlist"
    Unknown = "Unknown"


class Origins(Enum):
    Default = "Default"
    Playlist = "Playlist"


async def is_connected(ctx):
    try:
        voice_channel = ctx.guild.voice_client.channel
        return voice_channel
    except:
        return None


def clean_sclink(track):
    if track.startswith("https://m."):
        track = track.replace("https://m.", "https://")
    if track.startswith("http://m."):
        track = track.replace("http://m.", "https://")
    return track


def get_url(content):
    regex = re.compile("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
    if re.search(regex, content):
        result = regex.search(content)
        url = result.group(0)
        return url
    else:
        return None


def identify_url(url):
    if url is None:
        return Sites.Unknown
    if "https://www.youtu" in url or "https://youtu.be" in url:
        return Sites.YouTube
    if "bandcamp.com/track/" in url:
        return Sites.Bandcamp
    if "https://twitter.com/" in url:
        return Sites.Twitter
    if url.lower().endswith(('.webm', '.mp4', '.mp3', '.avi', '.wav', '.m4v', '.ogg', '.mov')):
        return Sites.Custom
    if "soundcloud.com/" in url:
        return Sites.SoundCloud
    # If no match
    return Sites.Unknown


def identify_playlist(url):
    if url is None:
        return Sites.Unknown
    if "playlist?list=" in url:
        return PlaylistTypes.YouTube_Playlist
    if "bandcamp.com/album/" in url:
        return PlaylistTypes.BandCamp_Playlist
    return PlaylistTypes.Unknown


async def play_check(ctx):
    sett = guild_to_settings[ctx.guild]
    author_voice = ctx.author.voice
    if ctx.guild.voice_client is None:
        await ctx.respond("Tu dois être dans le même vocal que le bot pour utiliser cette commande.", ephemeral=True)
        return False
    bot_vc = ctx.guild.voice_client.channel
    if author_voice is None:
        await ctx.respond("Tu dois être dans le même vocal que le bot pour utiliser cette commande.", ephemeral=True)
        return False
    elif ctx.author.voice.channel != bot_vc:
        await ctx.respond("Tu dois être dans le même vocal que le bot pour utiliser cette commande.", ephemeral=True)
        return False
    return True
