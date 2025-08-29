from GoloBot.Musique.aux import *
from GoloBot.Auxilliaire.settings import *
from GoloBot.Musique.songs import *
import concurrent.futures
import yt_dlp
from youtube_search import YoutubeSearch
import asyncio
import discord

guild_to_audiocontroller = dict()


class YTDLPSilentLogger:
    def debug(self, msg):
        pass

    def info(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        pass

    def youtube(self, message):
        pass


yt_dlp_options = {
    'logger': YTDLPSilentLogger(),
    'extract_flat': True,
    "cookiefile": "cookies.txt",
    'quiet': True,
    'noprogress': True,
    'nowarnings': True,
    'simulate': True
}


class Timer:
    def __init__(self, callback):
        self._callback = callback
        self._task = asyncio.create_task(self._job())

    async def _job(self):
        await asyncio.sleep(600)
        await self._callback()

    def cancel(self):
        self._task.cancel()


class AudioController:
    """ Controls the playback of audio and the sequential playing of the songs.

            Attributes:
                bot: The instance of the bot that will be playing the music.
                playlist: A Playlist object that stores the history and queue of songs.
                current_song: A Song object that stores details of the current song.
                guild: The guild in which the Audiocontroller operates.
        """

    def __init__(self, bot, guild):
        self.bot = bot
        self.playlist = Playlist()
        self.current_song = None
        self.guild = guild
        sett = guild_to_settings[guild.id]
        self._volume = sett['default volume'].value
        self.timer = Timer(self.timeout_handler)
        self.loop = False

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value):
        self._volume = value
        try:
            self.guild.voice_client.source.volume = float(value) / 100.0
        except Exception:
            pass

    @staticmethod
    async def register_voice_channel(channel):
        await channel.connect(reconnect=True, timeout=None)

    def track_history(self):
        history_string = "Musiques jouées :"
        return history_string + "\n".join([f"- {track}" for track in self.playlist.trackname_history])

    def next_song(self, error):
        """Invoked after a song is finished. Plays the next song if there is one."""
        next_song = self.playlist.next(self.current_song)
        self.current_song = None
        if next_song is None:
            return
        coro = self.play_song(next_song)
        self.bot.loop.create_task(coro)

    async def play_song(self, song):
        """Plays a song object"""
        self.timer.cancel()
        self.timer = Timer(self.timeout_handler)

        if song.info.title is None:
            try:
                downloader = yt_dlp.YoutubeDL(
                    {'format': 'bestaudio', 'title': True, "cookiefile": "cookies.txt"})
                r = downloader.extract_info(
                    song.info.webpage_url, download=False)
            except:
                asyncio.wait(1)
                downloader = yt_dlp.YoutubeDL(
                    {'title': True, "cookiefile": "cookies.txt"})
                r = downloader.extract_info(
                    track, download=False)

            song.base_url = r.get('url')
            song.info.uploader = r.get('uploader')
            song.info.title = r.get('title')
            song.info.duration = r.get('duration')
            song.info.webpage_url = r.get('webpage_url')
            song.info.thumbnail = r.get('thumbnails')[0]['url']

        self.playlist.add_name(song.info.title)
        self.current_song = song
        self.playlist.playhistory.append(self.current_song)
        self.guild.voice_client.play(discord.FFmpegPCMAudio(
            song.base_url,
            before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'),
            after=lambda e: self.next_song(e))
        self.guild.voice_client.source = discord.PCMVolumeTransformer(self.guild.voice_client.source)
        self.guild.voice_client.source.volume = float(self.volume) / 100.0
        self.playlist.playque.popleft()
        for song in list(self.playlist.playque)[:5]:
            asyncio.ensure_future(self.preload(song))

    async def process_song(self, track):
        """Adds the track to the playlist instance and plays it, if it is the first song"""
        search = YoutubeSearch(track, max_results=1).to_dict()
        if search:
            track = f"https://www.youtube.com{search[0]['url_suffix']}"
        host = identify_url(track)
        is_playlist = identify_playlist(track)

        if is_playlist != PlaylistTypes.Unknown:
            await self.process_playlist(is_playlist, track)
            if self.current_song is None:
                await self.play_song(self.playlist.playque[0])
            song = Song(Origins.Playlist, Sites.Unknown)
            return song

        if host == Sites.Unknown:
            if get_url(track) is not None:
                return None
            track = self.search_youtube(track)

        if host == Sites.YouTube:
            track = track.split("&list=")[0]

        r = None
        try:
            downloader = yt_dlp.YoutubeDL({'format': 'bestaudio', 'title': True, "cookiefile": "cookies.txt"})
            try:
                r = downloader.extract_info(track, download=False)
            except Exception as e:
                if "ERROR: Sign in to confirm your age" in str(e):
                    return None
        except:
            downloader = yt_dlp.YoutubeDL({'title': True, "cookiefile": "cookies.txt"})
            r = downloader.extract_info(track, download=False)

        if r is None:
            return

        if r.get('thumbnails') is not None:
            thumbnail = r.get('thumbnails')[len(r.get('thumbnails')) - 1]['url']
        else:
            thumbnail = None

        song = Song(Origins.Default, host, base_url=r.get('url'), uploader=r.get('uploader'), title=r.get(
            'title'), duration=r.get('duration'), webpage_url=r.get('webpage_url'), thumbnail=thumbnail)
        self.playlist.add(song)
        if self.current_song is None:
            await self.play_song(song)
        return song

    async def process_playlist(self, playlist_type, url):
        if playlist_type == PlaylistTypes.YouTube_Playlist:
            if "playlist?list=" in url:
                listid = url.split('=')[1]
            else:
                video = url.split('&')[0]
                await self.process_song(video)
                return
            with yt_dlp.YoutubeDL(yt_dlp_options) as ydl:
                r = ydl.extract_info(url, download=False)
                for entry in r['entries']:
                    link = f"https://www.youtube.com/watch?v={entry['id']}"
                    song = Song(Origins.Playlist, Sites.YouTube, webpage_url=link)
                    self.playlist.add(song)

        if playlist_type == PlaylistTypes.BandCamp_Playlist:
            with yt_dlp.YoutubeDL(yt_dlp_options) as ydl:
                r = ydl.extract_info(url, download=False)
                for entry in r['entries']:
                    link = entry.get('url')
                    song = Song(Origins.Playlist, Sites.Bandcamp, webpage_url=link)
                    self.playlist.add(song)

        for song in list(self.playlist.playque)[:5]:
            asyncio.ensure_future(self.preload(song))

    @staticmethod
    async def preload(song):
        if song.info.title is not None:
            return

        def down(song):
            if song.info.webpage_url is None:
                return None
            downloader = yt_dlp.YoutubeDL(
                {'format': 'bestaudio', 'title': True, "cookiefile": "cookies.txt"})
            r = downloader.extract_info(
                song.info.webpage_url, download=False)
            song.base_url = r.get('url')
            song.info.uploader = r.get('uploader')
            song.info.title = r.get('title')
            song.info.duration = r.get('duration')
            song.info.webpage_url = r.get('webpage_url')
            song.info.thumbnail = r.get('thumbnails')[0]['url']

        loop = asyncio.get_event_loop()
        executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=5)
        await asyncio.wait(fs={loop.run_in_executor(executor, down, song)}, return_when=asyncio.ALL_COMPLETED)

    @staticmethod
    def search_youtube(title):
        """Searches YouTube for the video title and returns the first results video link"""
        # if title is already a link
        if get_url(title) is not None:
            return title

        with yt_dlp.YoutubeDL(yt_dlp_options) as ydl:
            r = ydl.extract_info(title, download=False)
        if r is None:
            return None
        videocode = r['entries'][0]['id']
        return "https://www.youtube.com/watch?v={}".format(videocode)

    async def stop_player(self):
        """Stops the player and removes all songs from the queue"""
        if self.guild.voice_client is None or (
                not self.guild.voice_client.is_paused() and not self.guild.voice_client.is_playing()):
            return
        self.playlist.next(self.current_song)
        self.clear_queue()
        self.guild.voice_client.stop()

    async def prev_song(self):
        """Loads the last song from the history into the queue and starts it"""
        self.timer.cancel()
        self.timer = Timer(self.timeout_handler)
        if len(self.playlist.playhistory) == 0:
            return

        prev_song = self.playlist.prev(self.current_song)
        if not self.guild.voice_client.is_playing() and not self.guild.voice_client.is_paused():
            if prev_song == "Dummy":
                self.playlist.next(self.current_song)
                return None
            await self.play_song(prev_song)
        else:
            self.guild.voice_client.stop()

    async def timeout_handler(self):
        if self.guild.voice_client is not None and self.guild.voice_client.is_playing():
            self.timer = Timer(self.timeout_handler)  # restart timer
            return

        self.timer = Timer(self.timeout_handler)
        await self.udisconnect()

    async def uconnect(self, ctx):
        if not ctx.author.voice:
            await ctx.respond("Tu dois être dans un vocal pour utiliser cette commande.", ephemeral=True)
            return False

        if self.guild.voice_client is None:
            await self.register_voice_channel(ctx.author.voice.channel)
            return True
        else:
            await ctx.respond("Le bot est déjà dans un autre vocal", ephemeral=True)

    async def udisconnect(self):
        await self.stop_player()
        await self.guild.voice_client.disconnect(force=True)

    def clear_queue(self):
        self.playlist.playque.clear()


async def register(bot, guild):
    guild_to_settings[guild.id] = Settings(guild)
    guild_to_audiocontroller[guild.id] = AudioController(bot, guild)
