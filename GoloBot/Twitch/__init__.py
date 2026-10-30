from aiohttp import ClientSession

from GoloBot import CustomSlash
from GoloBot.template import *


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


class CogTwitch(AutoAddedCog):
    db: Transaction

    async def on_ready(self, **kwargs):
        db_path = kwargs.get('db', config.get('DB_STREAMS', 'annonces_streams.json'))
        self.db = Transaction(JsonStore(db_path))
        self.task_annonces.start()

    @tasks.loop(minutes=10)
    async def task_annonces(self):
        await self.bot.wait_until_ready()
        async with ClientSession() as session:
            await self.bot.token.twitch.reload(session)
            with self.db as data:
                for guild_id, channels in data.items():
                    guild = await self.bot.fetch_guild(guild_id)
                    for channel_id, streamers in channels.items():
                        channel = await guild.fetch_channel(channel_id)
                        for streamer in streamers:
                            await streamer.annonce(self.bot, channel, session)

    @CustomSlash()
    async def liste_streams(self, ctx: ApplicationContext):
        await ctx.defer(ephemeral=True)
        embed = GBEmbed(title="Alertes de streams", guild=ctx.guild)
        if not ctx.guild.id in self.db:
            await ctx.respond(f"Aucune alerte configurée sur ce serveur")
            return

        for channel_id, streamers in self.db[ctx.guild.id].items():
            channel = await ctx.guild.fetch_channel(channel_id)
            values = [s.url for s in streamers]
            values.sort()
            embed.add_field(name=f"Poste dans {channel.name}",
                            value='- ' + '\n- '.join(values))
        await ctx.respond(embed=embed)

    @CustomSlash()
    async def add_stream(self, ctx: ApplicationContext, chaine: str, salon: discord.TextChannel, notif: str):
        await ctx.defer(ephemeral=True)
        streamer = Streamer(token=self.bot.token.twitch, login=chaine, id=None, notif=notif)
        gid = salon.guild.id
        cid = salon.id
        if not gid in self.db:
            self.db[gid] = dict()
        if not cid in self.db[gid]:
            self.db[gid][cid] = list()
        if not rec_in(self.db[gid][cid], streamer.id):
            self.db[gid][cid].append(streamer.to_json())
            self.db.write()
            await ctx.respond(f"{streamer.url} va maintenant être annoncé dans {salon.mention}")
        else:
            await ctx.respond(f"{streamer.url} est déjà annoncé dans {salon.mention}")

    @CustomSlash()
    async def remove_stream(self, ctx: ApplicationContext, chaine: str, salon: discord.TextChannel):
        await ctx.defer(ephemeral=True)
        chaine = chaine.lower()
        suppr = list()
        gid = ctx.guild.id
        gdel = list()  # guilds à supprimer après le parcours
        if gid in self.db:
            cdel = list()  # salons à supprimer après le parcours
            for cid, streamers in self.db[gid].items():
                skip = False
                remove = list()
                if isinstance(salon, discord.TextChannel):
                    skip = not int(cid) == salon.id
                if skip:
                    continue

                for i in range(len(streamers)):
                    streamer = streamers[i]
                    if streamer.url.strip('/').endswith(chaine):
                        suppr.append(f'<#{cid}>')  # pour l'affichage à la fin
                        remove.append(i)  # on ajoute l'indice à la liste de suppression

                # parcours en sens inverse pour éviter les out of range
                for i in reversed(remove):
                    del self.db[gid][cid][i]

                if len(streamers) == 0:
                    cdel.append(cid)
            for cid in cdel:
                del self.db[gid][cid]

            if len(self.db[gid]) == 0:
                gdel.append(gid)
        for gid in gdel:
            del self.db[gid]
        await ctx.respond(f"Les annonces de stream de {chaine} ne seront plus postées dans {', '.join(suppr)}")
