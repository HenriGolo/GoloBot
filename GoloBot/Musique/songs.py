from GoloBot.Auxilliaire import MyEmbed
from collections import deque
from discord import Colour
from datetime import timedelta


class Song:
    def __init__(self, origin, host, base_url=None, uploader=None, title=None, duration=None, webpage_url=None,
                 thumbnail=None):
        self.host = host
        self.origin = origin
        self.base_url = base_url
        self.info = self.Sinfo(uploader, title, duration,
                               webpage_url, thumbnail)

    class Sinfo:
        def __init__(self, uploader, title, duration, webpage_url, thumbnail):
            self.uploader = uploader
            self.title = title
            self.duration = duration
            self.webpage_url = webpage_url
            self.thumbnail = thumbnail
            self.output = ""

        def format_output(self, playtype, color=Colour.blurple()):
            embed = MyEmbed(title=playtype,
                            description=f"[{self.title}]({self.webpage_url})",
                            color=color)
            if self.thumbnail is not None:
                embed.set_thumbnail(url=self.thumbnail)
            embed.add_field(name="Uploader", value=self.uploader, inline=False)
            if self.duration is not None:
                embed.add_field(name="Durée", value=str(timedelta(seconds=self.duration)), inline=False)
            else:
                embed.add_field(name="Durée", value="Inconnue", inline=False)
            return embed


class Playlist:
    def __init__(self):
        # Stores the links os the songs in queue and the ones already played
        self.playque = deque()
        self.playhistory = deque()
        # A seperate history that remembers the names of the tracks that were played
        self.trackname_history = deque()

    def __len__(self):
        return len(self.playque)

    def add_name(self, trackname):
        self.trackname_history.append(trackname)
        if len(self.trackname_history) > 15:
            self.trackname_history.popleft()

    def add(self, track):
        self.playque.append(track)

    def next(self, song_played):
        if len(self.playque) == 0:
            return None

        if len(self.playque) == 0:
            return None

        if song_played != "Dummy":
            if len(self.playhistory) > 10:
                self.playhistory.popleft()

        return self.playque[0]

    def prev(self, current_song):

        if current_song is None:
            self.playque.appendleft(self.playhistory[-1])
            return self.playque[0]

        ind = self.playhistory.index(current_song)
        self.playque.appendleft(self.playhistory[ind - 1])
        if current_song is not None:
            self.playque.insert(1, current_song)

    def move(self, oldindex: int, newindex: int):
        temp = self.playque[oldindex]
        del self.playque[oldindex]
        self.playque.insert(newindex, temp)

    def empty(self):
        self.playque.clear()
        self.playhistory.clear()
