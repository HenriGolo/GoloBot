import discord
from aiohttp import ClientSession
from ..Auxilliaire import *
from ..template import *
import requests
import json


class AccessToken(Storable):
    def __init__(self, twitchID, twitchSecret):
        self.twitchID = twitchID
        self.twitchSecret = twitchSecret

    async def use(self, session: ClientSession):
        if not hasattr(self, 'access_token'):
            await self.reload(session)
        if hasattr(self, 'expires_at'):
            if now() > self.expires_at:
                await self.reload(session)
        else:
            await self.reload(session)
        return self.access_token

    async def reload(self, session: ClientSession):
        request = 'https://id.twitch.tv/oauth2/token'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {'client_id': self.twitchID,
                'client_secret': self.twitchSecret,
                'grant_type': 'client_credentials'}
        async with session.post(request, headers=headers, data=data) as response:
            json = await response.json()
            for key, value in json.items():
                setattr(self, key, value)
            if hasattr(self, 'expires_in'):
                setattr(self, 'expires_at', now() + timedelta(seconds=self.expires_in))
        return self


async def get_streams(login, token: AccessToken, session: ClientSession):
    request = f'https://api.twitch.tv/helix/streams?user_login={login}'
    headers = {'Content-Type': 'application/json',
               'Authorization': f'Bearer {await token.use(session)}',
               'Client-Id': token.twitchID}
    async with session.get(request, headers=headers) as response:
        json = await response.json()
        data = json['data']
        return data


async def get_users(login, id, token: AccessToken, session: ClientSession):
    request = f'https://api.twitch.tv/helix/users?login={login}'
    if id:
        request = f'https://api.twitch.tv/helix/users?id={id}'
    headers = {'Content-Type': 'application/json',
               'Authorization': f'Bearer {await token.use(session)}',
               'Client-Id': token.twitchID}
    async with session.get(request, headers=headers) as response:
        json = await response.json()
        data = json['data']
        return data


class Streamer(Storable):
    def __init__(self, token: AccessToken, login: str = '', id: int = 0, notif: str = '', msg_url: str = ''):
        self.token = token
        self.login = login.strip('/').split('/')[-1]
        self.id = id
        self.notif = notif
        self.msg_url = msg_url
        self.url = f'https://twitch.tv/{self.login}'
        self.loaded = False

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            login = self.login == other.login
            notif = self.notif == other.notif
            msg = self.msg_url = other.msg_url
            return login and notif and msg
        return False

    def __str__(self):
        return self.url

    async def reload(self, session: ClientSession):
        self.loaded = False
        users = await get_users(login=self.login, id=self.id, token=self.token, session=session)
        data = users[0]
        for key, value in data.items():
            if key == 'created_at':
                value = datetime.fromisoformat(value[:-1])  # format RFC3339, termine par Z
            elif key == 'login':
                self.url = f'https://twitch.tv/{value}'
            elif key == 'id':
                value = int(value)
            setattr(self, key, value)
        self.loaded = True
        return self

    async def generate_embed(self, session: ClientSession) -> GBEmbed:
        if not self.loaded:
            await self.reload(session)
        streams = await get_streams(self.login, self.token, session)
        if not streams:
            return None
        stream = streams[0]
        started_at = datetime.fromisoformat(stream['started_at'][:-1])
        started_at = convert_timezone(started_at, 'UTC', 'Europe/Paris')
        embed = GBEmbed(title=stream['title'], color=0xffffff, url=self.url, timestamp=started_at)
        embed.set_author(name=self.display_name, icon_url=self.profile_image_url)
        embed.set_image(url=f"https://static-cdn.jtvnw.net/ttv-boxart/{stream['game_id']}-570x760.jpg")
        # embed.set_image(url=stream['thumbnail_url'].format(width=1920, height=1080))
        embed.add_field(name="Jeu", value=stream['game_name'])
        embed.set_footer(text=f"{stream['viewer_count']} viewers")
        return embed

    async def annonce(self, bot: BotTemplate, channel: discord.TextChannel, session: ClientSession) -> bool:
        if not self.loaded:
            await self.reload(session)
        embed = await self.generate_embed(session)
        view = GBView(bot).add_links(**{'Y aller': self.url})

        # on récupère le message
        message = None
        if self.msg_url is not None:
            message = await jumpurl2Message(bot, self.msg_url)

        if embed is None:
            if message is not None:
                await message.delete()
                self.msg_url = ''
            return False

        if message is None:
            func = channel.send
        else:
            # On cherche à savoir si l'embed généré contient des nouveautés
            previous = message.embeds[0]
            modif = False
            for elt in ['title', 'description']:
                if not getattr(embed, elt) == getattr(previous, elt):
                    modif = True

            for i in range(len(embed.fields)):
                if not embed.fields[i].name == previous.fields[i].name:
                    modif = True
                elif not embed.fields[i].value == previous.fields[i].value:
                    modif = True
                # Pas la peine de chercher plus loin
                if modif:
                    break

            if modif:
                func = message.edit
            else:
                return False

        message = await func(self.notif, embed=embed, view=view)
        self.msg_url = message.jump_url
        return True
